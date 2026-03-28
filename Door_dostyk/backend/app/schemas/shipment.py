from pydantic import BaseModel
from datetime import datetime


class ShipmentItemCreate(BaseModel):
    si_product_id: int
    si_quantity: int


class ShipmentCreate(BaseModel):
    shp_supplier_name: str
    items: list[ShipmentItemCreate]


class ShipmentItemRead(BaseModel):
    si_id: int
    si_shipment_id: int
    si_product_id: int
    si_quantity: int

    model_config = {"from_attributes": True}


class ShipmentRead(BaseModel):
    shp_id: int
    shp_supplier_name: str
    shp_status: str
    shp_created_at: datetime
    items: list[ShipmentItemRead]

    model_config = {"from_attributes": True}
