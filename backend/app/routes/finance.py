from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.finance import CashRegister, CashTransaction, Withdrawal, WithdrawalCreate
from app.services.finance_service import FinanceService
from app.routes.deps import get_db, get_current_user, check_admin

router = APIRouter()

@router.get("/register", response_model=CashRegister)
async def read_register(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get current cash register status.
    """
    return await FinanceService.get_or_create_register(db)

@router.get("/transactions", response_model=List[CashTransaction])
async def read_transactions(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
) -> Any:
    """
    Get cash transactions.
    """
    return await FinanceService.get_transactions(db, skip=skip, limit=limit)

@router.post("/withdraw", response_model=Withdrawal)
async def create_withdrawal(
    *,
    db: AsyncSession = Depends(get_db),
    withdrawal_in: WithdrawalCreate,
    current_user = Depends(check_admin),
) -> Any:
    """
    Create a withdrawal (Admin only).
    """
    try:
        return await FinanceService.create_withdrawal(
            db, obj_in=withdrawal_in, admin_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
