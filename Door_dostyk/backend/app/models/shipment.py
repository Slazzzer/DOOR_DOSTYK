from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    shp_id            = Column(Integer, primary_key=True, autoincrement=True)
    shp_supplier_name = Column(String(150), nullable=False)
    shp_status        = Column(String(30), nullable=False, default="received")
    shp_created_at    = Column(DateTime, nullable=False, server_default=func.now())

    items = relationship("ShipmentItem", back_populates="shipment", cascade="all, delete-orphan")


class ShipmentItem(Base):
    __tablename__ = "shipment_items"

    si_id          = Column(Integer, primary_key=True, autoincrement=True)
    si_shipment_id = Column(Integer, ForeignKey("shipments.shp_id", ondelete="CASCADE"), nullable=False)
    si_product_id  = Column(Integer, ForeignKey("products.prod_id"), nullable=False)
    si_quantity    = Column(Integer, nullable=False)

    shipment = relationship("Shipment", back_populates="items")
    product  = relationship("Product")
