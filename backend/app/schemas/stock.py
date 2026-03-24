from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class StockAdjustment(BaseModel):
    product_id: int
    change_amount: int
    reason: str

class StockHistory(BaseModel):
    id: int
    product_id: int
    change_amount: int
    reason: str
    created_at: datetime
    user_id: int

    model_config = ConfigDict(from_attributes=True)
