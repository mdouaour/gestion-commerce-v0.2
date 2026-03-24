from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional

class ProductService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: ProductCreate) -> Product:
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
        return result.scalar_one_or_none()

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
        
        # Increment version for optimistic locking
        db_obj.version += 1
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, id: int) -> bool:
        db_obj = await ProductService.get(db, id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True
