from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User as UserModel
from app.schemas.stock import StockAdjustment, StockHistory
from app.schemas.product import Product
from app.services.stock_service import StockService
from app.routes.deps import get_db, get_current_user

router = APIRouter()

@router.post("/adjust", response_model=Product)
async def adjust_stock(
    *,
    db: AsyncSession = Depends(get_db),
    adjustment: StockAdjustment,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Adjust stock quantity of a product.
    """
    product = await StockService.adjust_stock(
        db, adjustment=adjustment, user_id=current_user.id
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.get("/history/{product_id}", response_model=List[StockHistory])
async def read_stock_history(
    *,
    db: AsyncSession = Depends(get_db),
    product_id: int,
    current_user: UserModel = Depends(get_current_user),
) -> Any:
    """
    Get stock history for a product.
    """
    return await StockService.get_history(db, product_id=product_id)
