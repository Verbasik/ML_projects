# app/models/schemas.py

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import List, Optional

class ModelConfig(BaseSettings):
    """
    Description:
        Конфигурация модели

    Args:
        model_name: Название модели
        num_labels: Количество меток
        max_length: Максимальная длина
        label_map_path: Путь к файлу с метками
    """
    model_name: str     = Field(default="BERT", env="MODEL_NAME")
    num_labels: int     = Field(default=393,    env="NUM_LABELS")
    max_length: int     = Field(default=1024,   env="MAX_LENGTH")
    label_map_path: str = Field(default="app/BERT/id_topic.json", env="LABEL_MAP_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

class PredictionRequest(BaseModel):
    """
    Description:
        Схема запроса на предсказание

    Args:
        texts: Список текстов для классификации
    """
    texts: List[str] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="Список текстов для классификации"
    )

class PredictionResponse(BaseModel):
    """
    Description:
        Схема ответа с предсказанием

    Args:
        prediction: Предсказанный класс
        confidence: Уверенность модели в предсказании
    """
    prediction: str = Field(..., description="Предсказанный класс")
    confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Уверенность модели в предсказании"
    )
