## **MistralBot** 🤖

**Класс S3_provider** 🌐

Класс S3_provider предназначен для взаимодействия с хранилищем S3. Он предоставляет методы для загрузки файлов из S3 хранилища. Этот класс используется для загрузки и хранения моделей и данных, необходимых для работы сервиса.

Методы:

- `__init__(self)`: Инициализация провайдера S3. Настраивает соединение с хранилищем S3, используя заданные параметры подключения.
- `download_from_s3(self, s3_folder: str, local_folder: str) -> str`: Загрузка файлов из S3 хранилища в локальную директорию. Метод автоматически загружает все файлы из указанной папки в S3 хранилище в локальную директорию. Если локальная директория не существует, она будет создана вместе с необходимыми поддиректориями. Процесс загрузки логируется, предоставляя информацию о статусе загрузки каждого файла. В случае возникновения ошибки в процессе загрузки, метод логирует ошибку и возвращает None.

**Класс MistralBot** 🤖

Класс MistralBot управляет чат-диалогом с помощью LLM. Он генерирует подсказки и ответы, управляя взаимодействием между пользователем и моделью LLM.

Методы:

- `threaded_function(self)`: Загружает и инициализирует модель для генерации текста с использованием Hugging Face Transformers и langchain_community.llms.
- `load_context(self, context)`: Загружает модели из S3 хранилища.
- `predict(self, context, model_input: pd.DataFrame) -> str`: Генерирует ответ на запрос пользователя с учетом подсказки.
