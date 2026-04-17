import re
from datetime import datetime, timezone

from pydantic import BaseModel, field_serializer, field_validator


class OrderItemCreate(BaseModel):
    oi_product_id: int
    oi_quantity: int


class OrderCreate(BaseModel):
    ord_client_name: str
    ord_client_phone: str | None = None
    items: list[OrderItemCreate]

    @field_validator("ord_client_name")
    @classmethod
    def validate_client_name(cls, v: str) -> str:
        s = v.strip()
        if len(s) < 3:
            raise ValueError("Укажите ФИО не короче 3 символов")
        if not re.search(r"[А-Яа-яЁёA-Za-z]", s):
            raise ValueError("В ФИО должны быть буквы")
        return s

    @field_validator("ord_client_phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        if v is None:
            return None
        raw = str(v).strip()
        if not raw:
            return None
        digits = re.sub(r"[\s\-()]", "", raw)
        if digits.startswith("8") and len(digits) == 11:
            digits = "+7" + digits[1:]
        elif digits.startswith("7") and len(digits) == 11:
            digits = "+" + digits
        elif not digits.startswith("+"):
            digits = "+" + digits.lstrip("+")
        if not re.fullmatch(r"\+7\d{10}", digits):
            raise ValueError("Телефон в формате +7XXXXXXXXXX (например +79205386674)")
        return digits


class OrderItemRead(BaseModel):
    oi_id: int
    oi_order_id: int
    oi_product_id: int
    oi_quantity: int
    oi_price: float

    model_config = {"from_attributes": True}


class OrderRead(BaseModel):
    ord_id: int
    ord_client_name: str
    ord_client_phone: str | None
    ord_status: str
    ord_total_amount: float
    ord_created_at: datetime
    items: list[OrderItemRead]

    model_config = {"from_attributes": True}

    @field_serializer("ord_created_at")
    def serialize_ord_created_at(self, v: datetime) -> str:
        """TIMESTAMP без таймзоны в БД хранится как UTC; в JSON отдаём с явным UTC."""
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.isoformat()
