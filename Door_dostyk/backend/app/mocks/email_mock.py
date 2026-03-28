import logging

logger = logging.getLogger("mock.email")


def send_email(to: str, subject: str, body: str) -> dict:
    """Имитация отправки email — вместо письма пишет лог в консоль."""
    logger.info("[Email Mock] Кому: %s", to)
    logger.info("[Email Mock] Тема: %s", subject)
    logger.info("[Email Mock] Текст: %s", body)
    return {
        "status": "ok",
        "message": f"Письмо для {to} залогировано в консоль",
    }
