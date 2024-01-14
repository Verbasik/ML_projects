# VicunaBot - Управление чат-диалогами с помощью LLM 🤖

## Описание модуля
`VicunaBot` - это класс, созданный для управления чат-диалогами с использованием модели LLM (Language Learning Model). Он обеспечивает генерацию подсказок и ответов на основе текущего контекста диалога. 🌐

### Основные функции 🛠️
- **Генерация ответов**: С использованием текущего контекста и подсказки.
- **Управление диалогом**: Обновление и сохранение истории диалога.
- **Сохранение модели**: Регистрация и сохранение модели в MLflow.

### Важные библиотеки 📚
- `mlflow`, `torch`, `transformers`: Для работы с машинным обучением и моделированием.
- `boto3`, `botocore`: Для работы с облачными сервисами.
- `pandas`: Для обработки и анализа данных.
- `langchain`: Для работы с чат-моделями и схемами сообщений.

## Основные методы класса

### `__init__(self, model, tokenizer, device, gen_kwargs)`
Инициализация VicunaBot с компонентами модели LLM.

### `generate(self, messages, stop, prompt)`
Генерация ответа модели LLM на основе текущего контекста и подсказки.

### `predict(self, context, model_input)`
Вычисление предсказаний модели на основе входных данных и сохранение диалога.

### `get_assistant_response(self)`
Получение ответа от ассистента, основываясь на текущем контексте диалога.

### `save_model(model_name, registered_model_name)`
Сохранение модели в MLflow.

## Пример использования 📝
```python
# Создание объекта VicunaBot
model = LlamaForCausalLM.from_pretrained(...)
tokenizer = LlamaTokenizer.from_pretrained(...)
vicuna_bot = VicunaBot(model, tokenizer, device='cuda', gen_kwargs={...})

# Генерация ответа
messages = [...]
response = vicuna_bot.generate(messages)
```
