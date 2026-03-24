from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.finance import CashRegister, CashTransaction, Withdrawal, TransactionType
from app.schemas.finance import CashTransactionCreate, WithdrawalCreate
from typing import Optional, List
from datetime import datetime

class FinanceService:
    @staticmethod
    async def get_or_create_register(db: AsyncSession) -> CashRegister:
        result = await db.execute(select(CashRegister).where(CashRegister.id == 1))
        register = result.scalar_one_or_none()
        
        if not register:
            register = CashRegister(id=1, current_balance=0.0, is_open=True)
            db.add(register)
            await db.commit()
            await db.refresh(register)
        
        return register

    @staticmethod
    async def add_transaction(
        db: AsyncSession, 
        amount: float, 
        type: TransactionType, 
        reason: str, 
        user_id: int
    ) -> CashTransaction:
        register = await FinanceService.get_or_create_register(db)
        
        # Update balance
        register.current_balance += amount
        
        transaction = CashTransaction(
            register_id=register.id,
            amount=amount,
            type=type,
            reason=reason,
            user_id=user_id
        )
        
        db.add(transaction)
        await db.commit()
        await db.refresh(transaction)
        return transaction

    @staticmethod
    async def create_withdrawal(
        db: AsyncSession, 
        obj_in: WithdrawalCreate, 
        admin_id: int
    ) -> Withdrawal:
        register = await FinanceService.get_or_create_register(db)
        
        if register.current_balance < obj_in.amount:
            raise ValueError("Insufficient funds in cash register")
            
        # 1. Update Register balance
        register.current_balance -= obj_in.amount
        
        # 2. Log as CashTransaction
        transaction = CashTransaction(
            register_id=register.id,
            amount=-obj_in.amount,
            type=TransactionType.WITHDRAWAL,
            reason=f"Withdrawal: {obj_in.reason}",
            user_id=admin_id
        )
        
        # 3. Create Withdrawal record
        withdrawal = Withdrawal(
            amount=obj_in.amount,
            reason=obj_in.reason,
            admin_id=admin_id
        )
        
        db.add(transaction)
        db.add(withdrawal)
        await db.commit()
        await db.refresh(withdrawal)
        return withdrawal

    @staticmethod
    async def get_transactions(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[CashTransaction]:
        result = await db.execute(
            select(CashTransaction)
            .order_by(CashTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
