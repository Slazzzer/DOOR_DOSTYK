from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.shipment import Shipment, ShipmentItem
from app.schemas.shipment import ShipmentCreate
from app.mocks.email_mock import send_email


def create_shipment(db: Session, data: ShipmentCreate) -> Shipment:
    if not data.items:
        raise HTTPException(status_code=400, detail="Приёмка не может быть пустой")

    shipment = Shipment(
        shp_supplier_name=data.shp_supplier_name,
        shp_status="received",
    )
    db.add(shipment)
    db.flush()

    for item in data.items:
        product = db.query(Product).filter(Product.prod_id == item.si_product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар #{item.si_product_id} не найден")

        product.prod_quantity += item.si_quantity

        shipment_item = ShipmentItem(
            si_shipment_id=shipment.shp_id,
            si_product_id=item.si_product_id,
            si_quantity=item.si_quantity,
        )
        db.add(shipment_item)

    db.commit()
    db.refresh(shipment)

    send_email(
        to=data.shp_supplier_name,
        subject=f"Приёмка #{shipment.shp_id} завершена",
        body=f"Товар от '{data.shp_supplier_name}' принят на склад",
    )

    return shipment
