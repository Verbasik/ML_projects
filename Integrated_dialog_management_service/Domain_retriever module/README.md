## **Domain Retriever** 🔍

Для поиска необходимой информации в базе знаний требуется RAG или Embeddings хранилище.

Поиск может быть семантическим 🧠, может быть словесным 📝.

Семантический поиск основан на пространстве Embeddings сделанного настроенного моделью или отдельными слоями.

**Класс Domain_Retriever** 👨‍💻

Класс `Domain_Retriever` функционирует как классификатор для обработки естественного языка (NLU), оптимизированный для точного поиска и классификации терминов и запросов в тексте. Этот класс является важным элементом системы, обеспечивающим понимание контекста и извлечение сущностей, что критично для адаптации ответов системы к потребностям пользователя.

**Класс NerExtractor** 🧠

`NerExtractor` — это специализированный класс для извлечения именованных сущностей, использующий передовые технологии и предобученные модели из библиотеки transformers. Этот класс важен для анализа текста и извлечения критически значимой информации, что позволяет улучшить понимание контекста взаимодействий и обогатить пользовательский опыт.

**Класс Domain_Retriever** 🧐

Классификатор для обработки естественного языка (NLU), предназначенный для поиска и классификации терминов и запросов.

Методы:

- `__init__(self, file_path = './Question.docx')`: Инициализация классификатора NLU с указанием пути к файлу с данными.
- `load_context(self, context) -> None`: Загрузка контекстных моделей из S3 хранилища для дальнейшего использования.
- `predict(self, context, model_input: pd.DataFrame) -> str`: Прогнозирует контекст и извлекает сущности, связанные с входным запросом.

Остальные методы класса `Domain_Retriever` предоставляют функциональность для работы с текстовыми данными, включая извлечение данных из файла, поиск в контексте, извлечение сущностей и вычисление векторных представлений.

- `get_data(self, file_path: str) -> tuple`: Извлекает данные из указанного файла и возвращает кортеж из двух элементов - список всех данных и список секций.
- `search_in_context(self, query, sentence_embeddings, model, tokenizer, data_list, treshold, top_k=5) -> list`: Выполняет поиск в контексте с использованием векторных представлений и возвращает список наиболее релевантных результатов.
- `search_in_context_with_score(self, query, sentence_embeddings, model, tokenizer, data_list, treshold, top_k=5) -> list`: Выполняет поиск в контексте с использованием векторных представлений и возвращает список наиболее релевантных результатов вместе с их сходством.
- `get_context(self, question: str) -> str`: Извлекает контекст, релевантный заданному вопросу.
- `extract_named_entities(self, question: str) -> Dict[str, Any]`: Извлекает именованные сущности из заданного вопроса.
- `get_entities(self, text: str) -> list`: Извлекает сущности из указанного текста.
- `get_embenddings(self, data_list, max_length=12) -> torch.Tensor`: Вычисляет векторные представления для указанного списка данных.
- `mean_pooling(self, model_output, attention_mask) -> torch.Tensor`: Вычисляет среднее значение векторных представлений для указанного модельного вывода и маски внимания.

**Класс NerExtractor** 🧾

Класс для извлечения именованных сущностей из текста, использующий предобученные модели NER из библиотеки transformers.

Методы:

- `__init__(self)`: Инициализация экстрактора сущностей.
- `load_context(self, context) -> None`: Загрузка моделей NER из S3 хранилища.
- `predict(self, context, query) -> list`: Прогнозирует и извлекает именованные сущности из текста.
