from sqlalchemy import String, DateTime, ForeignKey, Float, Enum, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from typing import List
from app.core.database import Base

class TransactionType(str, enum.Enum):
    SALE = "sale"
    WITHDRAWAL = "withdrawal"
    DEPOSIT = "deposit" # e.g. adding petty cash
    ADJUSTMENT = "adjustment" # manual fix

class CashRegister(Base):
    __tablename__ = "cash_registers"

    id: Mapped[int] = mapped_column(primary_key=True)
    current_balance: Mapped[float] = mapped_column(default=0.0)
    is_open: Mapped[bool] = mapped_column(default=True)
    last_opened_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class CashTransaction(Base):
    __tablename__ = "cash_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    register_id: Mapped[int] = mapped_column(ForeignKey("cash_registers.id"), index=True)
    amount: Mapped[float] = mapped_column() # positive for in, negative for out
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    reason: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationship
    user: Mapped["User"] = relationship("User")

class Withdrawal(Base):
    __tablename__ = "withdrawals"

    id: Mapped[int] = mapped_column(primary_key=True)
    amount: Mapped[float] = mapped_column()
    reason: Mapped[str] = mapped_column(String(255))
    admin_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationship
    admin: Mapped["User"] = relationship("User")

from app.models.user import User
