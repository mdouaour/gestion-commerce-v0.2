from sqlalchemy.ext.asyncio import AsyncSession
from app.models.product import Product
from app.models.base import StockHistory
from app.schemas.stock import StockAdjustment
from typing import Optional

class StockService:
    @staticmethod
    async def adjust_stock(
        db: AsyncSession, 
        adjustment: StockAdjustment, 
        user_id: int
    ) -> Optional[Product]:
        # Get product
        result = await db.execute(
            select(Product).where(Product.id == adjustment.product_id)
        )
        product = result.scalar_one_or_none()
        
        if not product:
            return None
            
        # Update stock
        product.stock_quantity += adjustment.change_amount
        product.version += 1 # Optimistic locking
        
        # Create history entry
        history = StockHistory(
            product_id=product.id,
            change_amount=adjustment.change_amount,
            reason=adjustment.reason,
            user_id=user_id
        )
        
        db.add(history)
        await db.commit()
        await db.refresh(product)
        return product

from sqlalchemy import select
