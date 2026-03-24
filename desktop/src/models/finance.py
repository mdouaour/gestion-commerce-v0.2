from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Boolean, func, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum

class TransactionType(str, enum.Enum):
    SALE = 'sale'
    WITHDRAWAL = 'withdrawal'
    DEPOSIT = 'deposit'
    ADJUSTMENT = 'adjustment'

class CashRegister(Base):
    __tablename__ = 'cash_registers'

    id = Column(Integer, primary_key=True, index=True)
    current_balance = Column(Float, default=0.0)
    is_open = Column(Boolean, default=True)
    last_opened_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class CashTransaction(Base):
    __tablename__ = 'cash_transactions'

    id = Column(Integer, primary_key=True, index=True)
    register_id = Column(Integer, ForeignKey('cash_registers.id'), index=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)
    reason = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship('User')

class Withdrawal(Base):
    __tablename__ = 'withdrawals'

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)
    admin_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    admin = relationship('User')
