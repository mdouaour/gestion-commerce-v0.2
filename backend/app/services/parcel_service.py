from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.parcel import Parcel, ParcelItem, ParcelStatus
from app.schemas.parcel import ParcelCreate, ParcelUpdate
from app.services.stock_service import StockService
from app.services.finance_service import FinanceService
from app.schemas.stock import StockAdjustment
from app.core.errors import ErrorCode
from app.routes.deps import raise_http_exception
from app.models.user import User as UserModel # Type hinting
from app.models.product import Product # For type hinting
from app.models.user import User # For type hinting
from fastapi import HTTPException, status
from typing import List, Optional

class ParcelService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: ParcelCreate, user_id: int) -> Parcel:
        total_items_amount = sum(item.quantity * item.price_at_sale for item in obj_in.items)
        total_amount = total_items_amount + obj_in.shipping_fee
        
        db_obj = Parcel(
            client_name=obj_in.client_name,
            client_phone=obj_in.client_phone,
            client_address=obj_in.client_address,
            shipping_fee=obj_in.shipping_fee,
            total_amount=total_amount,
            status=ParcelStatus.CREATED,
            user_id=user_id
        )
        db.add(db_obj)
        await db.flush()
        
        for item_in in obj_in.items:
            item = ParcelItem(
                parcel_id=db_obj.id,
                product_id=item_in.product_id,
                quantity=item_in.quantity,
                price_at_sale=item_in.price_at_sale
            )
            db.add(item)
            
            adj = StockAdjustment(
                product_id=item_in.product_id,
                change_amount=-item_in.quantity,
                reason=f"Parcel #{db_obj.id} created"
            )
            await StockService.adjust_stock(db, adj, user_id)
            
        await db.commit()
        await db.refresh(db_obj)
        
        return await ParcelService.get(db, db_obj.id)

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[Parcel]:
        result = await db.execute(
            select(Parcel)
            .options(selectinload(Parcel.items))
            .where(Parcel.id == id)
        )
        parcel = result.scalar_one_or_none()
        if not parcel:
            raise_http_exception(status.HTTP_404_NOT_FOUND, ErrorCode.PARCEL_NOT_FOUND)
        return parcel

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Parcel]:
        result = await db.execute(
            select(Parcel)
            .options(selectinload(Parcel.items))
            .order_by(Parcel.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def update_status(db: AsyncSession, id: int, status: ParcelStatus, user_id: int) -> Optional[Parcel]:
        parcel = await ParcelService.get(db, id)
        if not parcel:
            raise_http_exception(status.HTTP_404_NOT_FOUND, ErrorCode.PARCEL_NOT_FOUND)
            
        old_status = parcel.status
        parcel.status = status
        
        if status == ParcelStatus.RETURNED and old_status != ParcelStatus.RETURNED:
            for item in parcel.items:
                adj = StockAdjustment(
                    product_id=item.product_id,
                    change_amount=item.quantity,
                    reason=f"Parcel #{parcel.id} returned"
                )
                await StockService.adjust_stock(db, adj, user_id)
        
        if status == ParcelStatus.DELIVERED:
            parcel.is_money_collected = True
            parcel.collected_amount = parcel.total_amount
            
        await db.commit()
        await db.refresh(parcel)
        return parcel
