from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.finance import TransactionType

class CashRegisterBase(BaseModel):
    current_balance: float = 0.0
    is_open: bool = True

class CashRegister(CashRegisterBase):
    id: int
    last_opened_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CashTransactionBase(BaseModel):
    register_id: int
    amount: float
    type: TransactionType
    reason: str

class CashTransactionCreate(CashTransactionBase):
    pass

class CashTransaction(CashTransactionBase):
    id: int
    created_at: datetime
    user_id: int
    model_config = ConfigDict(from_attributes=True)

class WithdrawalBase(BaseModel):
    amount: float
    reason: str

class WithdrawalCreate(WithdrawalBase):
    pass

class Withdrawal(WithdrawalBase):
    id: int
    admin_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
