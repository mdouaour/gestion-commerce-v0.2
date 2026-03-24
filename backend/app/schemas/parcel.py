from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.parcel import ParcelStatus

class ParcelItemBase(BaseModel):
    product_id: int
    quantity: int
    price_at_sale: float

class ParcelItemCreate(ParcelItemBase):
    pass

class ParcelItem(ParcelItemBase):
    id: int
    parcel_id: int
    model_config = ConfigDict(from_attributes=True)

class ParcelBase(BaseModel):
    client_name: str
    client_phone: str
    client_address: str
    shipping_fee: float = 0.0

class ParcelCreate(ParcelBase):
    items: List[ParcelItemCreate]

class ParcelUpdate(BaseModel):
    status: Optional[ParcelStatus] = None
    is_money_collected: Optional[bool] = None
    collected_amount: Optional[float] = None

class Parcel(ParcelBase):
    id: int
    status: ParcelStatus
    total_amount: float
    is_money_collected: bool
    collected_amount: float
    created_at: datetime
    updated_at: datetime
    user_id: int
    items: List[ParcelItem]

    model_config = ConfigDict(from_attributes=True)
