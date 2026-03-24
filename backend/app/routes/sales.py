from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.sale import Sale, SaleCreate
from app.services.sale_service import SaleService
from app.routes.deps import get_db, get_current_user

router = APIRouter()

@router.get("/", response_model=List[Sale])
async def read_sales(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Retrieve sales.
    """
    return await SaleService.get_all(db, skip=skip, limit=limit)

@router.post("/", response_model=Sale)
async def create_sale(
    *,
    db: AsyncSession = Depends(get_db),
    sale_in: SaleCreate,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Create new sale.
    """
    return await SaleService.create_sale(db, obj_in=sale_in, user_id=current_user.id)

@router.get("/{id}", response_model=Sale)
async def read_sale(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get sale by ID.
    """
    sale = await SaleService.get(db, id=id)
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale
