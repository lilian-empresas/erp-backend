from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.order import OrderStatus

# --- Item Schemas ---

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = 1

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int
    product_sku: str
    product_name: str
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)

# --- Order Schemas ---

class OrderBase(BaseModel):
    customer_name: Optional[str] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    customer_name: Optional[str] = None

class Order(OrderBase):
    id: int
    status: str
    total_amount: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItem] = []

    model_config = ConfigDict(from_attributes=True)
