from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product

router = APIRouter(prefix="/api/products", tags=["products"])


@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.prod_id == product_id).first()
    if not product:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Товар не найден")
    return product
