from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.stock_service import StockService
from app.schemas.stock import StockAdjustment
from app.core.errors import ErrorCode
from app.routes.deps import raise_http_exception
from app.models.user import User # For type hinting
from fastapi import HTTPException, status
from typing import List, Optional

class ProductService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: ProductCreate) -> Product:
        product = await ProductService.get_by_sku(db, sku=obj_in.sku)
        if product:
            raise_http_exception(status.HTTP_400_BAD_REQUEST, ErrorCode.SKU_ALREADY_EXISTS, "SKU already exists")
        
        db_obj = Product(
            name=obj_in.name,
            sku=obj_in.sku,
            description=obj_in.description,
            price=obj_in.price,
            stock_quantity=obj_in.stock_quantity,
            category_id=obj_in.category_id
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[Product]:
        result = await db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise_http_exception(status.HTTP_404_NOT_FOUND, ErrorCode.PRODUCT_NOT_FOUND)
        return product

    @staticmethod
    async def get_by_sku(db: AsyncSession, sku: str) -> Optional[Product]:
        result = await db.execute(select(Product).where(Product.sku == sku))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Product]:
        result = await db.execute(select(Product).options(selectinload(Product.category)))
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, db_obj: Product, obj_in: ProductUpdate) -> Product:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db_obj.version += 1 # Optimistic locking
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, id: int) -> bool:
        db_obj = await ProductService.get(db, id=id)
        if not db_obj:
            raise_http_exception(status.HTTP_404_NOT_FOUND, ErrorCode.PRODUCT_NOT_FOUND)
        await db.delete(db_obj)
        await db.commit()
        return True
