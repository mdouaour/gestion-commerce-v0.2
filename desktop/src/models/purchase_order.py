from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, Enum, Text
from sqlalchemy.orm import relationship
from .database import Base
import enum

class POStatus(str, enum.Enum):
    DRAFT = 'draft'
    DELIVERED = 'delivered'
    PAID = 'paid'
    CANCELLED = 'cancelled'

class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'

    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(100), nullable=False)
    status = Column(String, default=POStatus.DRAFT)
    total_amount = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    items = relationship('PurchaseOrderItem', back_populates='po', cascade='all, delete-orphan')
    user = relationship('User')

class PurchaseOrderItem(Base):
    __tablename__ = 'purchase_order_items'

    id = Column(Integer, primary_key=True, index=True)
    po_id = Column(Integer, ForeignKey('purchase_orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    purchase_price = Column(Float, nullable=False)
    selling_price = Column(Float, nullable=False)

    po = relationship('PurchaseOrder', back_populates='items')
    product = relationship('Product')
