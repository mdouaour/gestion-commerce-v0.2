from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.models.finance import TransactionType
from app.schemas.sale import SaleCreate
from app.services.stock_service import StockService
from app.services.finance_service import FinanceService
from app.schemas.stock import StockAdjustment
from app.core.errors import ErrorCode
from app.routes.deps import raise_http_exception
from app.models.finance import CashTransaction
from fastapi import HTTPException, status
from typing import List, Optional

class SaleService:
    @staticmethod
    async def create_sale(db: AsyncSession, obj_in: SaleCreate, user_id: int) -> Sale:
        total_amount = 0.0
        
        db_sale = Sale(user_id=user_id, total_amount=0.0)
        db.add(db_sale)
        await db.flush()
        
        for item_in in obj_in.items:
            result = await db.execute(select(Product).where(Product.id == item_in.product_id))
            product = result.scalar_one_or_none()
            
            if not product:
                raise_http_exception(status.HTTP_404_NOT_FOUND, ErrorCode.PRODUCT_NOT_FOUND, f"Product {item_in.product_id} not found")
            
            if product.version != item_in.version:
                raise_http_exception(status.HTTP_409_CONFLICT, ErrorCode.OPTIMISTIC_LOCK_CONFLICT, f"Product '{product.name}' was modified by another transaction. Please refresh.")
            
            if product.stock_quantity < item_in.quantity:
                raise_http_exception(status.HTTP_400_BAD_REQUEST, ErrorCode.INSUFFICIENT_STOCK, f"Insufficient stock for '{product.name}'")
            
            item = SaleItem(
                sale_id=db_sale.id,
                product_id=product.id,
                quantity=item_in.quantity,
                price_at_sale=item_in.price_at_sale
            )
            db.add(item)
            
            total_amount += item_in.quantity * item_in.price_at_sale
            
            adj = StockAdjustment(
                product_id=product.id,
                change_amount=-item_in.quantity,
                reason=f"In-store Sale #{db_sale.id}"
            )
            await StockService.adjust_stock(db, adj, user_id)
            
        db_sale.total_amount = total_amount
        
        cash_tx = await FinanceService.add_transaction(
            db, 
            amount=total_amount, 
            type=TransactionType.SALE, 
            reason=f"In-store Sale #{db_sale.id}", 
            user_id=user_id
        )
        db_sale.cash_transaction_id = cash_tx.id
        
        await db.commit()
        await db.refresh(db_sale)
        
        return await SaleService.get(db, db_sale.id)

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[Sale]:
        result = await db.execute(
            select(Sale)
            .options(selectinload(Sale.items))
            .where(Sale.id == id)
        )
        sale = result.scalar_one_or_none()
        if not sale:
            raise_http_exception(status.HTTP_404_NOT_FOUND, ErrorCode.SALE_NOT_FOUND)
        return sale

    @staticmethod
    async def get_all(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Sale]:
        result = await db.execute(
            select(Sale)
            .options(selectinload(Sale.items))
            .order_by(Sale.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
