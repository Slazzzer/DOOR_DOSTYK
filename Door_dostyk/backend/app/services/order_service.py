from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate
from app.mocks.accounting_mock import send_to_1c
from app.mocks.email_mock import send_email


def list_orders(db: Session) -> list[Order]:
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .order_by(Order.ord_created_at.desc())
        .all()
    )


def create_order(db: Session, data: OrderCreate) -> Order:
    if not data.items:
        raise HTTPException(status_code=400, detail="Заказ не может быть пустым")

    order = Order(
        ord_client_name=data.ord_client_name,
        ord_client_phone=data.ord_client_phone,
        ord_status="new",
    )
    db.add(order)
    db.flush()

    total = 0.0

    for item in data.items:
        product = db.query(Product).filter(Product.prod_id == item.oi_product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар #{item.oi_product_id} не найден")
        if product.prod_quantity < item.oi_quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Недостаточно '{product.prod_name}' на складе: есть {product.prod_quantity}, запрошено {item.oi_quantity}",
            )

        product.prod_quantity -= item.oi_quantity

        line_total = float(product.prod_price) * item.oi_quantity
        total += line_total

        order_item = OrderItem(
            oi_order_id=order.ord_id,
            oi_product_id=item.oi_product_id,
            oi_quantity=item.oi_quantity,
            oi_price=float(product.prod_price),
        )
        db.add(order_item)

    order.ord_total_amount = total
    db.commit()
    db.refresh(order)

    send_to_1c(order.ord_id, float(order.ord_total_amount))
    send_email(
        to=data.ord_client_name,
        subject=f"Заказ #{order.ord_id} оформлен",
        body=f"Сумма заказа: {order.ord_total_amount} руб.",
    )

    return order
