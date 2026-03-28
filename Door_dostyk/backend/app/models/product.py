from sqlalchemy import Column, Integer, String, Numeric, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    prod_id         = Column(Integer, primary_key=True, autoincrement=True)
    prod_name       = Column(String(200), nullable=False)
    prod_sku        = Column(String(50), unique=True, nullable=False)
    prod_price      = Column(Numeric(10, 2), nullable=False, default=0)
    prod_quantity   = Column(Integer, nullable=False, default=0)
    prod_created_at = Column(DateTime, nullable=False, server_default=func.now())
