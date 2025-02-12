# app/main.py

# Импорты стандартных библиотек
import logging

# Импорты сторонних библиотек
from fastapi import FastAPI

# Импорты локальных модулей
from config import get_settings
from api.health import router as health_router
from api.route  import router as api_v1_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
settings = get_settings()

def create_application() -> FastAPI:
    """
    Description:
        Создание экземпляра FastAPI приложения.

    Args:
        None

    Returns:
        FastAPI: Экземпляр FastAPI приложения.

    Raises:
        None

    Examples:
        >>> app = create_application()
        >>> app.title
        'BERT Inference Service'
    """
    app = FastAPI(
        title=settings.APP_NAME,
        debug=settings.DEBUG
    )

    # Подключение маршрутов
    app.include_router(health_router, tags=["health"])
    app.include_router(
        api_v1_router,
        prefix=settings.API_V1_STR,
        tags=["api"]
    )

    return app

app = create_application()

@app.on_event("startup")
async def startup_event():
    """
    Description:
        Действия при запуске приложения.

    Args:
        None

    Returns:
        None

    Raises:
        None

    Examples:
        >>> await startup_event()
        'Starting up application...'
    """
    logger.info("Starting up application...")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Description:
        Действия при остановке приложения.

    Args:
        None

    Returns:
        None

    Raises:
        None

    Examples:
        >>> await shutdown_event()
        'Shutting down application...'
    """
    logger.info("Shutting down application...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )