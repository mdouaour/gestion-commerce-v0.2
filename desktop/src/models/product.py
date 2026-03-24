from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from .database import Base

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    products = relationship('Product', back_populates='category')

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    sku = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)
    
    # Versioning for optimistic locking in multi-tab sales
    version = Column(Integer, default=1, nullable=False)
    
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    category = relationship('Category', back_populates='products')
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class SyncQueue(Base):
    __tablename__ = 'sync_queue'

    id = Column(Integer, primary_key=True, index=True)
    table_name = Column(String, nullable=False)
    row_id = Column(Integer, nullable=False)
    operation = Column(String, nullable=False) # 'INSERT', 'UPDATE', 'DELETE'
    data = Column(Text, nullable=True) # JSON payload
    synced = Column(Integer, default=0) # 0: False, 1: True
    created_at = Column(DateTime, server_default=func.now())
