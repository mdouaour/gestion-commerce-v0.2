from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.product import Category
from app.schemas.product import CategoryCreate, CategoryUpdate
from typing import List, Optional

class CategoryService:
    @staticmethod
    async def create(db: AsyncSession, obj_in: CategoryCreate) -> Category:
        db_obj = Category(
            name=obj_in.name,
            description=obj_in.description
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def get(db: AsyncSession, id: int) -> Optional[Category]:
        result = await db.execute(select(Category).where(Category.id == id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(db: AsyncSession) -> List[Category]:
        result = await db.execute(select(Category))
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, db_obj: Category, obj_in: CategoryUpdate) -> Category:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, id: int) -> bool:
        db_obj = await CategoryService.get(db, id)
        if not db_obj:
            return False
        await db.delete(db_obj)
        await db.commit()
        return True
