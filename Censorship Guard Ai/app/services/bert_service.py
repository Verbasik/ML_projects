# app/services/bert_service.py

# Стандартные библиотеки
import logging

# Сторонние библиотеки
from fastapi import Depends

# Локальные модули
from models.bert import BERTModel
from models.schemas import ModelConfig, PredictionRequest, PredictionResponse
from config import get_settings

logger = logging.getLogger(__name__)

class BERTService:
    """
    Description:
        Сервис для работы с моделью BERT, включая инициализацию модели и получение предсказаний.

    Examples:
        Пример использования сервиса:
        >>> service = BERTService(settings)
        >>> response = await service.predict(request)
    """

    def __init__(self, settings=Depends(get_settings)) -> None:
        """
        Description:
            Инициализация сервиса BERT.

        Args:
            settings: Настройки приложения, полученные через зависимость.

        Raises:
            RuntimeError: Ошибка инициализации модели.
        """
        self.settings = settings
        self.model = None
        self._initialize_model()

    def _initialize_model(self) -> None:
        """
        Description:
            Инициализация модели BERT на основе конфигурации.

        Raises:
            RuntimeError: Ошибка инициализации модели.

        Examples:
            >>> service._initialize_model()
        """
        try:
            config = ModelConfig(
                model_name=self.settings.MODEL_NAME,
                num_labels=self.settings.NUM_LABELS,
                max_length=self.settings.MAX_LENGTH,
                label_map_path=self.settings.LABEL_MAP_PATH,
            )
            self.model = BERTModel(config)
            logger.info("BERT model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BERT model: {str(e)}")
            raise RuntimeError(f"Model initialization failed: {str(e)}")

    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        """
        Description:
            Получение предсказания от модели BERT.

        Args:
            request (PredictionRequest): Запрос на предсказание.

        Returns:
            PredictionResponse: Ответ с предсказанием.

        Raises:
            RuntimeError: Ошибка предсказания или модель не инициализирована.

        Examples:
            >>> request = PredictionRequest(texts=["Sample text"])
            >>> response = await service.predict(request)
        """
        if not self.model:
            raise RuntimeError("Model not initialized")

        return await self.model.predict(request)