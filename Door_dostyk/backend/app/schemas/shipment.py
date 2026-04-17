from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer


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

    @field_serializer("shp_created_at")
    def serialize_shp_created_at(self, v: datetime) -> str:
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.isoformat()
