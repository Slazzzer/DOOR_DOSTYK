from sqlalchemy.orm import Session

from app.models.product import Product


def query_products(db: Session, search: str | None = None):
    """Каталог товаров; при непустом search — фильтр по названию (ILIKE, без учёта регистра)."""
    q = db.query(Product)
    if search is not None and (term := search.strip()):
        q = q.filter(Product.prod_name.ilike(f"%{term}%"))
    return q
