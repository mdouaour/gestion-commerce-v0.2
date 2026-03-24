from sqlalchemy import String, DateTime, ForeignKey, Float, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from app.core.database import Base

class Sale(Base):
    __tablename__ = "sales"

    id: Mapped[int] = mapped_column(primary_key=True)
    total_amount: Mapped[float] = mapped_column(default=0.0)
    
    # In-store sales always go to the Cash Register
    cash_transaction_id: Mapped[Optional[int]] = mapped_column(ForeignKey("cash_transactions.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    items: Mapped[List["SaleItem"]] = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship("User")
    cash_transaction: Mapped[Optional["CashTransaction"]] = relationship("CashTransaction")

class SaleItem(Base):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    price_at_sale: Mapped[float] = mapped_column()

    # Relationships
    sale: Mapped["Sale"] = relationship("Sale", back_populates="items")
    product: Mapped["Product"] = relationship("Product")

from app.models.user import User
from app.models.product import Product
from app.models.finance import CashTransaction
