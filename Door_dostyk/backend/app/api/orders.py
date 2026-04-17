from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderCreate, OrderRead
from app.services.order_service import create_order, list_orders

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("/", response_model=list[OrderRead])
def get_orders(db: Session = Depends(get_db)):
    return list_orders(db)


@router.post("/", response_model=OrderRead)
def post_order(data: OrderCreate, db: Session = Depends(get_db)):
    return create_order(db, data)
