# app/api/route.py

# Импорты стандартных библиотек
import logging
from typing import List

# Импорты сторонних библиотек
from fastapi import APIRouter, Depends, HTTPException

# Импорты локальных модулей
from models.schemas import PredictionRequest, PredictionResponse
from services.bert_service import BERTService
from config import get_settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    service: BERTService = Depends()
) -> PredictionResponse:
    """
    Description:
        Эндпоинт для получения предсказаний.

    Args:
        request (PredictionRequest): Запрос на предсказание.
        service (BERTService, optional): Сервис для выполнения предсказаний.
            По умолчанию Depends().

    Returns:
        PredictionResponse: Ответ с предсказанием.

    Raises:
        HTTPException: В случае ошибки предсказания.

    Examples:
        >>> response = await predict(request)
        >>> response
        PredictionResponse(...)
    """
    try:
        result = await service.predict(request)
        return result
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
