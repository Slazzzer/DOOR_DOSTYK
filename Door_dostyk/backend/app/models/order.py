from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    ord_id           = Column(Integer, primary_key=True, autoincrement=True)
    ord_client_name  = Column(String(150), nullable=False)
    ord_client_phone = Column(String(20))
    ord_status       = Column(String(30), nullable=False, default="new")
    ord_total_amount = Column(Numeric(12, 2), nullable=False, default=0)
    ord_created_at   = Column(DateTime, nullable=False, server_default=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    oi_id         = Column(Integer, primary_key=True, autoincrement=True)
    oi_order_id   = Column(Integer, ForeignKey("orders.ord_id", ondelete="CASCADE"), nullable=False)
    oi_product_id = Column(Integer, ForeignKey("products.prod_id"), nullable=False)
    oi_quantity   = Column(Integer, nullable=False)
    oi_price      = Column(Numeric(10, 2), nullable=False)

    order   = relationship("Order", back_populates="items")
    product = relationship("Product")
