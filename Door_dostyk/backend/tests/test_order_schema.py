"""Unit-тесты фич заказа: валидация телефона/ФИО в OrderCreate, UTC в OrderRead."""

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.order import OrderCreate, OrderRead


def _items():
    return [{"oi_product_id": 1, "oi_quantity": 1}]


def test_order_create_rejects_invalid_phone():
    """Мусор вроде ++++++ не должен проходить валидацию телефона."""
    with pytest.raises(ValidationError) as exc:
        OrderCreate(
            ord_client_name="Иванов Иван Петрович",
            ord_client_phone="++++++",
            items=_items(),
        )
    errs = exc.value.errors()
    assert any(e.get("loc") == ("ord_client_phone",) for e in errs)


def test_order_create_normalizes_valid_russian_mobile():
    """Ввод с 8, пробелами и дефисами приводится к +7 и десяти цифрам."""
    o = OrderCreate(
        ord_client_name="Иванов Иван",
        ord_client_phone="8 (920) 538-66-74",
        items=_items(),
    )
    assert o.ord_client_phone == "+79205386674"


def test_order_read_serializes_naive_created_at_as_utc():
    """Naive datetime из БД в JSON уходит с явным UTC (+00:00), чтобы фронт мог перевести в Москву."""
    o = OrderRead(
        ord_id=1,
        ord_client_name="Тест",
        ord_client_phone=None,
        ord_status="new",
        ord_total_amount=0.0,
        ord_created_at=datetime(2026, 4, 17, 12, 30, 0),
        items=[],
    )
    payload = o.model_dump(mode="json")
    assert payload["ord_created_at"] == "2026-04-17T12:30:00+00:00"
