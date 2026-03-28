from pydantic import BaseModel
from datetime import datetime


class OrderItemCreate(BaseModel):
    oi_product_id: int
    oi_quantity: int


class OrderCreate(BaseModel):
    ord_client_name: str
    ord_client_phone: str | None = None
    items: list[OrderItemCreate]


class OrderItemRead(BaseModel):
    oi_id: int
    oi_order_id: int
    oi_product_id: int
    oi_quantity: int
    oi_price: float

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    ord_id: int
    ord_client_name: str
    ord_client_phone: str | None
    ord_status: str
    ord_total_amount: float
    ord_created_at: datetime
    items: list[OrderItemRead]

    model_config = {"from_attributes": True}
