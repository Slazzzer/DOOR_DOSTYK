from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.shipment import ShipmentCreate, ShipmentRead
from app.services.shipment_service import create_shipment

router = APIRouter(prefix="/api/shipments", tags=["shipments"])


@router.post("/", response_model=ShipmentRead)
def post_shipment(data: ShipmentCreate, db: Session = Depends(get_db)):
    return create_shipment(db, data)
