# app/models/bert.py

# Стандартные библиотеки
import json
import logging
from typing import List, Optional, Dict, Tuple

# Сторонние библиотеки
import torch
from transformers import BertTokenizer, BertForSequenceClassification
from pydantic import ValidationError

# Локальные модули
from .schemas import PredictionRequest, PredictionResponse, ModelConfig

logger = logging.getLogger(__name__)

class BERTModel:
    def __init__(self, config: ModelConfig) -> None:
        """
        Description:
            Инициализация модели BERT с конфигурацией.

        Args:
            config (ModelConfig): Конфигурация модели.

        Raises:
            RuntimeError: Ошибка инициализации модели.

        Examples:
            >>> config = ModelConfig(model_name="bert-base-uncased", num_labels=2)
            >>> model = BERTModel(config)
        """
        try:
            # Сохранение конфигурации
            self.config = config
            
            # Загрузка модели BERT для задачи классификации
            self.model = BertForSequenceClassification.from_pretrained(
                config.model_name,
                num_labels=config.num_labels,
            )
            # Загрузка токенизатора для модели BERT
            self.tokenizer = BertTokenizer.from_pretrained(config.model_name)

            # Чтение словаря меток из указанного JSON файла, который связывает индексы с метками
            with open(config.label_map_path) as f:
                self.target_variables_dict = json.load(f)

            logger.info(f"Model {config.model_name} loaded successfully")

        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise RuntimeError(f"Model initialization failed: {str(e)}")

    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        """
        Description:
            Асинхронный метод предсказания с валидацией.

        Args:
            request (PredictionRequest): Запрос на предсказание.

        Returns:
            PredictionResponse: Ответ с предсказанием.

        Raises:
            RuntimeError: Ошибка предсказания.

        Examples:
            >>> request = PredictionRequest(texts=["Sample text"])
            >>> response = await model.predict(request)
        """
        try:
            # Валидация входных данных: проверка, что список текстов не пустой
            if not request.texts:
                raise ValidationError("Empty input texts")

            # Токенизация текстов
            tokenized = self._tokenize(request.texts)

            # Преобразование токенизированных данных в тензоры (input_ids и attention_mask)
            tokens_ids, attention_mask = self._convert_to_tensors(tokenized)

            # Асинхронное получение предсказания от модели
            model_output = await self._get_prediction(tokens_ids, attention_mask)

            # Обработка выходных данных модели для получения метки
            prediction = self._adjust_output(model_output)

            # Вычисление уверенности предсказания через softmax по логитам
            confidence = float(torch.softmax(model_output["logits"], dim=1).max())

            logger.info(f"Prediction successful: {prediction}")
            
            return PredictionResponse(
                prediction=prediction,
                confidence=confidence,
            )
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise RuntimeError(f"Prediction failed: {str(e)}")

    def _tokenize(
        self, texts: List[str], max_length: Optional[int] = None
    ) -> Dict[str, List[int]]:
        """
        Description:
            Токенизация текстов с настраиваемой длиной.

        Args:
            texts (List[str]): Список текстов для токенизации.
            max_length (Optional[int]): Максимальная длина токенов.

        Returns:
            Dict[str, List[int]]: Токенизированные данные.

        Examples:
            >>> tokenized = model._tokenize(["Sample text"], max_length=128)
        """
        # Если максимальная длина не указана, берем значение из конфигурации
        max_length = max_length or self.config.max_length

        return self.tokenizer.batch_encode_plus(
            texts,
            max_length=max_length,
            padding=True,
            truncation=True,
            return_token_type_ids=False,
        )

    def _convert_to_tensors(
        self, tokenized: Dict[str, List[int]]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Description:
            Конвертация токенизированных данных в тензоры.

        Args:
            tokenized (Dict[str, List[int]]): Токенизированные данные.

        Returns:
            Tuple[torch.Tensor, torch.Tensor]: Тензоры input_ids и attention_mask.

        Raises:
            RuntimeError: Ошибка конвертации в тензоры.

        Examples:
            >>> tokens_ids, attention_mask = model._convert_to_tensors(tokenized)
        """
        try:
            return (
                torch.tensor(tokenized["input_ids"]),
                torch.tensor(tokenized["attention_mask"]),
            )
        except Exception as e:
            logger.error(f"Tensor conversion failed: {str(e)}")
            raise RuntimeError(f"Tensor conversion failed: {str(e)}")

    async def _get_prediction(
        self, tokens_ids: torch.Tensor, attention_mask: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        """
        Description:
            Получение предсказания от модели.

        Args:
            tokens_ids (torch.Tensor): Тензоры input_ids.
            attention_mask (torch.Tensor): Тензоры attention_mask.

        Returns:
            Dict[str, torch.Tensor]: Выходные данные модели.

        Raises:
            RuntimeError: Ошибка предсказания модели.

        Examples:
            >>> model_output = await model._get_prediction(tokens_ids, attention_mask)
        """
        try:
            with torch.no_grad():
                # Передача входных данных в модель и получение предсказания
                return self.model(tokens_ids, attention_mask)
        except Exception as e:
            logger.error(f"Model prediction failed: {str(e)}")
            raise RuntimeError(f"Model prediction failed: {str(e)}")

    def _adjust_output(self, model_output: Dict[str, torch.Tensor]) -> str:
        """
        Description:
            Обработка выходных данных модели.

        Args:
            model_output (Dict[str, torch.Tensor]): Выходные данные модели.

        Returns:
            str: Обработанное предсказание.

        Raises:
            RuntimeError: Ошибка обработки выходных данных.

        Examples:
            >>> prediction = model._adjust_output(model_output)
        """
        try:
            logits = model_output["logits"]

            # Определение индекса с максимальным значением логита для первого примера в батче
            index = str(int(torch.argmax(logits[0])))

            # Если индекс отсутствует в словаре меток, генерируется ошибка
            if index not in self.target_variables_dict:
                raise ValueError(f"Invalid prediction index: {index}")
            
            # Возвращаем соответствующую метку
            return self.target_variables_dict[index]
        except Exception as e:
            logger.error(f"Output adjustment failed: {str(e)}")
            raise RuntimeError(f"Output adjustment failed: {str(e)}")