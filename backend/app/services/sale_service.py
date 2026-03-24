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
from typing import List, Optional
from fastapi import HTTPException

class SaleService:
    @staticmethod
    async def create_sale(db: AsyncSession, obj_in: SaleCreate, user_id: int) -> Sale:
        total_amount = 0.0
        
        # 1. Start Sale object
        db_sale = Sale(user_id=user_id, total_amount=0.0)
        db.add(db_sale)
        await db.flush() # Get ID
        
        # 2. Process items with Optimistic Locking check
        for item_in in obj_in.items:
            # Fetch product and verify version
            result = await db.execute(select(Product).where(Product.id == item_in.product_id))
            product = result.scalar_one_or_none()
            
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item_in.product_id} not found")
            
            # REQUIREMENT #6: Optimistic Locking
            if product.version != item_in.version:
                raise HTTPException(
                    status_code=409, 
                    detail=f"Product '{product.name}' was modified by another transaction. Please refresh."
                )
            
            if product.stock_quantity < item_in.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Insufficient stock for '{product.name}'"
                )
            
            # Create SaleItem
            item = SaleItem(
                sale_id=db_sale.id,
                product_id=product.id,
                quantity=item_in.quantity,
                price_at_sale=item_in.price_at_sale
            )
            db.add(item)
            
            total_amount += item_in.quantity * item_in.price_at_sale
            
            # Update Stock (Service already increments version)
            adj = StockAdjustment(
                product_id=product.id,
                change_amount=-item_in.quantity,
                reason=f"In-store Sale #{db_sale.id}"
            )
            await StockService.adjust_stock(db, adj, user_id)
            
        # 3. Finalize Sale Total
        db_sale.total_amount = total_amount
        
        # 4. Cash Register Transaction (REQUIREMENT #1)
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
        return result.scalar_one_or_none()

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
