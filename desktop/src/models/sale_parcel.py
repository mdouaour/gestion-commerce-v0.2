from sqlalchemy import Column, Integer, Float, DateTime, String, ForeignKey, Boolean, func, Enum
from sqlalchemy.orm import relationship
from .database import Base
import enum

class ParcelStatus(str, enum.Enum):
    CREATED = 'created'
    IN_DELIVERY = 'in_delivery'
    DELIVERED = 'delivered'
    RETURNED = 'returned'
    EXCHANGED = 'exchanged'

class Sale(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, default=0.0)
    cash_transaction_id = Column(Integer, ForeignKey('cash_transactions.id'), nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    is_cancelled = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    items = relationship('SaleItem', back_populates='sale', cascade='all, delete-orphan')
    user = relationship('User')

class SaleItem(Base):
    __tablename__ = 'sale_items'

    id = Column(Integer, primary_key=True, index=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Float, nullable=False)

    sale = relationship('Sale', back_populates='items')
    product = relationship('Product')

class Parcel(Base):
    __tablename__ = 'parcels'

    id = Column(Integer, primary_key=True, index=True)
    client_name = Column(String(100), nullable=False)
    client_phone = Column(String(20), nullable=False)
    client_address = Column(String(255), nullable=False)
    status = Column(String, default=ParcelStatus.CREATED)
    total_amount = Column(Float, default=0.0)
    shipping_fee = Column(Float, default=0.0)
    is_money_collected = Column(Boolean, default=False)
    collected_amount = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship('ParcelItem', back_populates='parcel', cascade='all, delete-orphan')
    user = relationship('User')

class ParcelItem(Base):
    __tablename__ = 'parcel_items'

    id = Column(Integer, primary_key=True, index=True)
    parcel_id = Column(Integer, ForeignKey('parcels.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_at_sale = Column(Float, nullable=False)

    parcel = relationship('Parcel', back_populates='items')
    product = relationship('Product')
