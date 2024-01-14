# PromptGenerator для VicunaBot 🤖

## Описание модуля
`PromptGenerator` - это модуль, предназначенный для генерации подсказок для модели LLM (Language Learning Model), используемой в VicunaBot 🌐. Этот класс упрощает взаимодействие с ботом, формируя подсказки на основе анализа истории диалога и текущего контекста.

### Основные компоненты 🛠️
- **NLU_Classifier**: Классификатор Natural Language Understanding для извлечения контекста из вопросов пользователя.
- **VicunaBot**: Основной объект бота, который взаимодействует с моделью LLM.

### Важные библиотеки 📚
- `transformers`: Используется для работы с моделями машинного обучения и моделирования.
- `typing`: Для улучшения читаемости кода и помощи в проверке типов.

## Основные функции модуля

### `__init__(self, nlu_classifier: NLU_Classifier, vicuna_bot: VicunaBot)`
Инициализация генератора подсказок с компонентами для анализа и ответа.

### `get_prompt(self, dialogue_history, messages: List[BaseMessage]) -> str`
Генерирует подсказку для модели LLM, используя историю диалога и текущий контекст.

### `_create_prompt(self, question: str, context: str, named_entities_content: str) -> str`
Создает текст подсказки на основе вопроса, контекста и информации об именованных сущностях.

### `_update_vicuna_bot_state(self, question: str, context: str)`
Обновляет состояние VicunaBot с новым вопросом и контекстом.

## Пример использования 📝
```python
# Создание экземпляра класса с необходимыми компонентами
prompt_generator = PromptGenerator(nlu_classifier, vicuna_bot)

# Получение подсказки для вопроса пользователя
prompt = prompt_generator.get_prompt(dialogue_history, messages)
```
Этот модуль является важной частью системы VicunaBot и способствует созданию более точных и контекстно-зависимых ответов на вопросы пользователей. 🎯
