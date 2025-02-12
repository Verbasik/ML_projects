# app/api/health.py

# Стандартные библиотеки
import logging
from typing import Dict

# Сторонние библиотеки
from fastapi import APIRouter, Response

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Description:
        Эндпоинт для проверки здоровья сервиса.

    Returns:
        Dict[str, str]: Словарь с ключом "status" и значением "healthy", 
        указывающий на состояние сервиса.

    Examples:
        >>> Пример использования эндпоинта через curl:
        >>> curl -X GET "http://localhost:8000/health"
        {"status": "healthy"}
    """
    logger.info("Health check requested")
    return {"status": "healthy"}