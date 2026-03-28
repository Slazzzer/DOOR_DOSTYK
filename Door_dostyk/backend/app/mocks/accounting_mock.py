import logging
from datetime import datetime

logger = logging.getLogger("mock.accounting")


def send_to_1c(order_id: int, total_amount: float) -> dict:
    """Имитация отправки данных заказа в 1С:Бухгалтерия."""
    logger.info(
        "[1С Mock] Заказ #%d на сумму %.2f руб. отправлен в 1С:Бухгалтерия",
        order_id,
        total_amount,
    )
    return {
        "status": "ok",
        "message": f"Заказ #{order_id} принят в 1С",
        "timestamp": datetime.now().isoformat(),
    }
