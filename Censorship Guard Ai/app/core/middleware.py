# app/core/middleware.py

# Стандартные библиотеки
import time
import logging

# Сторонние библиотеки
from fastapi import Request

logger = logging.getLogger(__name__)

async def logging_middleware(request: Request, call_next):
    """
    Description:
        Middleware для логирования входящих запросов и времени их обработки.

    Args:
        request (Request): Входящий HTTP-запрос.
        call_next: Функция для передачи запроса следующему middleware или обработчику.

    Returns:
        Response: Ответ, сгенерированный следующим middleware или обработчиком.

    Examples:
        Пример использования middleware в FastAPI:
        >>> app.add_middleware(logging_middleware)
    """
    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Path: {request.url.path} "
        f"Method: {request.method} "
        f"Status: {response.status_code} "
        f"Processing time: {process_time:.3f}s"
    )

    return response