from sqlalchemy import String, DateTime, ForeignKey, Float, Enum, func, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from typing import List, Optional
from app.core.database import Base

class ParcelStatus(str, enum.Enum):
    CREATED = "created"
    IN_DELIVERY = "in_delivery"
    DELIVERED = "delivered"
    RETURNED = "returned"
    EXCHANGED = "exchanged"

class Parcel(Base):
    __tablename__ = "parcels"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_name: Mapped[str] = mapped_column(String(100))
    client_phone: Mapped[str] = mapped_column(String(20))
    client_address: Mapped[str] = mapped_column(String(255))
    
    status: Mapped[ParcelStatus] = mapped_column(Enum(ParcelStatus), default=ParcelStatus.CREATED)
    
    total_amount: Mapped[float] = mapped_column(default=0.0) # money_to_collect (items total + shipping)
    shipping_fee: Mapped[float] = mapped_column(default=0.0)
    
    # Financial tracking (Requirement #2)
    is_money_collected: Mapped[bool] = mapped_column(default=False)
    collected_amount: Mapped[float] = mapped_column(default=0.0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Relationships
    items: Mapped[List["ParcelItem"]] = relationship("ParcelItem", back_populates="parcel", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship("User")

class ParcelItem(Base):
    __tablename__ = "parcel_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    parcel_id: Mapped[int] = mapped_column(ForeignKey("parcels.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column()
    price_at_sale: Mapped[float] = mapped_column()

    # Relationships
    parcel: Mapped["Parcel"] = relationship("Parcel", back_populates="items")
    product: Mapped["Product"] = relationship("Product")

from app.models.user import User
from app.models.product import Product
