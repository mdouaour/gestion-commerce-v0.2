from app.core.database import Base
from app.models.user import User
from app.models.product import Product, Category
from app.models.finance import CashRegister, CashTransaction, Withdrawal
from app.models.parcel import Parcel, ParcelItem
from app.models.sale import Sale, SaleItem
from sqlalchemy import String, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

class StockHistory(Base):
    __tablename__ = "stock_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    change_amount: Mapped[int] = mapped_column() # positive for addition, negative for deduction
    reason: Mapped[str] = mapped_column(String(255)) # e.g., "Sale #123", "Restock", "Return #456"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    product: Mapped["Product"] = relationship("Product")
    user: Mapped["User"] = relationship("User")
