from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class SaleItemBase(BaseModel):
    product_id: int
    quantity: int
    price_at_sale: float

class SaleItemCreate(SaleItemBase):
    # Added for optimistic locking validation at API level
    version: int 

class SaleItem(SaleItemBase):
    id: int
    sale_id: int
    model_config = ConfigDict(from_attributes=True)

class SaleCreate(BaseModel):
    items: List[SaleItemCreate]

class Sale(BaseModel):
    id: int
    total_amount: float
    cash_transaction_id: Optional[int]
    created_at: datetime
    user_id: int
    items: List[SaleItem]

    model_config = ConfigDict(from_attributes=True)
