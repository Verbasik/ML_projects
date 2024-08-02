# Проект Locust Load Testing

Этот проект предназначен для проведения нагрузочного тестирования с использованием Locust и Generation Inference (TGI) – инструментария для развертывания и обслуживания больших языковых моделей (LLM). TGI обеспечивает высокопроизводительную генерацию текста для самых популярных моделей с открытым исходным кодом, включая Llama, Falcon, StarCoder, BLOOM, GPT-NeoX и T5.

## Установка

1. Клонируйте репозиторий:
    ```sh
    git clone https://github.com/yourusername/locust-load-testing.git
    cd locust-load-testing
    ```

2. Создайте виртуальное окружение и активируйте его:
    ```sh
    python -m venv venv
    source venv/bin/activate  # Для Windows используйте `venv\Scripts\activate`
    ```

3. Установите необходимые зависимости:
    ```sh
    pip install -r requirements.txt
    ```

## Конфигурация

Перед запуском тестов, убедитесь, что у вас настроена переменная окружения `TGI_URL`, содержащая URL вашего API. Например:

```sh
export TGI_URL=http://localhost:8000
```

## Запуск тестов

**Запуск Locust**
Для запуска Locust в режиме без графического интерфейса используйте следующую команду:

```sh
Копировать код
locust -f locust.py --host=http://<HOST>:<PORT> -u <INITIAL_USERS> -r <SPAWN_RATE> --run-time <RUN_TIME> --headless
```

Пример:

```sh
Копировать код
locust -f locust.py --host=http://localhost:8080 -u 10 -r 1 --run-time 1m --headless
```
Параметры:

-u <INITIAL_USERS>: устанавливает начальное количество пользователей.
-r <SPAWN_RATE>: устанавливает скорость добавления пользователей.
--run-time <RUN_TIME>: устанавливает время выполнения теста.
--headless: запускает Locust в режиме без графического интерфейса.

Пример команды для сбора данных о GPU
Для сбора данных о загрузке GPU используйте следующую команду:

```sh
Копировать код
nvidia-smi --query-gpu=timestamp,index,name,utilization.gpu,utilization.memory,memory.total,memory.free,memory.used --format=csv -l 1 > gpu_usage.csv
```
Пример команды для копирования файла с удаленного сервера
Для копирования файла с удаленного сервера используйте следующую команду:

```sh
Копировать код
scp <USERNAME>@<REMOTE_HOST>:/path/to/gpu_usage.csv /local/path/to/destination
```
Пример:

```sh
Копировать код
scp user@remotehost:/home/user/gpu_usage.csv /local/path/to/destination
```
Логирование
Метрики запросов и количество пользователей логируются в CSV файлы:

metrics_log_tst.csv: содержит метрики запросов.
users_log.csv: содержит данные о количестве пользователей.
