from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderCreate, OrderRead
from app.services.order_service import create_order

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.post("/", response_model=OrderRead)
def post_order(data: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, data)
