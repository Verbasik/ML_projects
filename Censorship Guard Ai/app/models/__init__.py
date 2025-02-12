#  app/models/__init__.py

# Импорт моделей и схем
from .bert import BERTModel
from .schemas import PredictionRequest, PredictionResponse

__all__ = ['BERTModel', 'PredictionRequest', 'PredictionResponse']
