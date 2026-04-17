from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.services.product_service import query_products

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/")
def get_products(
    search: str | None = Query(None, description="Подстрока для поиска по названию товара"),
    db: Session = Depends(get_db),
):
    return query_products(db, search).all()


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.prod_id == product_id).first()
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product
