# app/config.py

# Импорты стандартных библиотек
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings

# Импорты сторонних библиотек
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Description:
        Настройки приложения.

    Args:
    Основные настройки:
        APP_NAME: Название приложения.
        API_V1_STR: Путь к API версии 1.
        DEBUG: Режим отладки.
    
    Настройки модели:
        MODEL_NAME: Название модели.
        MODEL_PATH: Путь к модели.
        NUM_LABELS: Количество меток.
        MAX_LENGTH: Максимальная длина.
        LABEL_MAP_PATH: Путь к файлу соответствия меток.
    
    Настройки сервера:
        HOST: Хост сервера.
        PORT: Порт сервера.
        WORKERS: Количество рабочих процессов.

    Returns:
        None

    Raises:
        None

    Examples:
        >>> settings = Settings()
        >>> settings.APP_NAME
        'BERT Inference Service'
    """

    # Основные настройки
    APP_NAME: str = "BERT Censorship"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Настройки модели
    MODEL_NAME: str = "BERT"
    MODEL_PATH: Optional[str] = "BERT"
    NUM_LABELS: int = 393
    MAX_LENGTH: int = 1024
    LABEL_MAP_PATH: str = "BERT/id_topic.json"

    # Настройки сервера
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache()
def get_settings() -> Settings:
    """
    Description:
        Получение настроек приложения с кэшированием.

    Args:
        None

    Returns:
        Settings: Объект настроек приложения.

    Raises:
        None

    Examples:
        >>> settings = get_settings()
        >>> settings.APP_NAME
        'BERT Inference Service'
    """
    return Settings()
