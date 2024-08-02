import os
import time
import json
import csv
import gevent
import datetime
from transformers import GPT2Tokenizer
from locust.runners import STATE_STOPPED, STATE_CLEANUP, MasterRunner, LocalRunner
from locust import FastHttpUser, TaskSet, task, between, LoadTestShape, events, stats

# Инициализация токенизатора
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

def log_to_csv(filename, data):
    """
    Description:
        Логирует метрики в CSV файл.

    Args:
        filename (str): Имя файла для логирования.
        data (list): Список данных, которые будут записаны в файл.

    Returns:
        None
    """
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "users_count", "request_type", "name", "response_time", "input_tokens", "output_tokens"])
        writer.writerow(data)

def log_users_to_csv(filename, timestamp, users_count):
    """
    Description:
        Логирует количество пользователей в CSV файл.

    Args:
        filename (str): Имя файла для логирования.
        timestamp (float): Временная метка.
        users_count (int): Количество пользователей.

    Returns:
        None
    """
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "users_count"])
        writer.writerow([timestamp, users_count])

def print_current_users(environment):
    """
    Печатает текущее количество пользователей.
    """
    while not environment.runner.state in [STATE_STOPPED, STATE_CLEANUP]:
        users_count = environment.runner.user_count
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        log_users_to_csv('users_log.csv', timestamp, users_count)
        print(f"Currently running users: {users_count}")
        time.sleep(2)

@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    """
    Description:
        Обработчик события для инициализации окружения Locust. Эта функция запускает 
        дополнительную задачу для печати текущего числа пользователей, если среда запускается 
        в режиме Master или Local.

    Args:
        environment (Environment): Объект окружения Locust, содержащий все необходимые конфигурации и 
                                   информацию о текущем запуске.
        **_kwargs: Дополнительные аргументы, переданные в обработчик, которые не используются в этой функции.

    Returns:
        None
    """
    if isinstance(environment.runner, MasterRunner) or isinstance(environment.runner, LocalRunner):
        gevent.spawn(print_current_users, environment)

@events.request.add_listener
def log_request(request_type, name, response_time, **kwargs):
    """
    Description:
        Обработчик события для логирования метрик запросов в CSV файл.

    Args:
        request_type (str): Тип запроса (например, 'GET' или 'POST').
        name (str): Имя или URL конечной точки запроса.
        response_time (float): Время ответа в миллисекундах.
        response_length (int): Длина ответа в байтах.
        exception (Exception, optional): Исключение, если запрос завершился с ошибкой.

    Returns:
        None
    """
    # Извлечение количества токенов из kwargs
    input_tokens  = kwargs.get('input_tokens',  0)
    output_tokens = kwargs.get('output_tokens', 0)
    users_count   = kwargs.get('users_count',   0)

    # Логирование данных только при успешном ответе
    response = kwargs.get("response")
    if response:
        log_to_csv('metrics_log_tst.csv', [time.time(), users_count, request_type, name, response_time, input_tokens, output_tokens])

class LLMTaskSet(TaskSet):
    """
    Description:
        Класс, представляющий набор задач для Locust, который включает задачу отправки запроса к модели LLM.

    Methods:
        query_model: Отправляет POST запрос к API модели LLM и проверяет статус ответа, собирает метрики.
    """
    
    @task
    def query_model(self):
        """
        Description:
            Отправляет POST запрос к API модели LLM и проверяет статус ответа. Если статус ответа не 200, отмечает запрос как неудачный. Собирает метрики: количество токенов в отправленном и полученном сообщении, полное время ответа.

        Args:
            None

        Returns:
            None
        """
        # Отправленное сообщение
        input_text = """
        Пожалуйста, предоставьте подробное объяснение концепции квантованной запутонности. Включите следующие аспекты:

        Введение в квантованную зарутонность:

        Определение квантованной запутонности.
        Исторический контекст и развитие теории.
        Основные принципы и идеи, лежащие в основе квантованной запутонности.
        Математическая формализация:

        Основные уравнения и математические модели, описывающие квантованную запутонности.
        Примеры использования операторов и матриц в контексте квантованной зарутонности.
        Объяснение ключевых математических понятий, таких как волновые функции, операторы и собственные значения.
        Физико-химическая формализация:

        Применение квантованной запутонности в физике и химии.
        Влияние квантованной запутонности на химические реакции и физические процессы.
        Примеры экспериментальных данных и их интерпретация с точки зрения квантованной запутонности.
        Примеры и приложения:

        Конкретные примеры систем, где квантованная запутонности играет ключевую роль.
        Примеры расчетов и моделирования квантованной запутонности в реальных системах.
        Обсуждение современных исследований и направлений в изучении квантованной запутонности.
        Заключение:

        Краткое резюме основных идей и выводов.
        Перспективы дальнейших исследований в области квантованной запутонности.
        Требования к ответу:

        Ответ должен быть структурированным и логически последовательным.
        Используйте ясный и понятный язык, избегая излишне сложных терминов без объяснения.
        Приведите примеры и иллюстрации, где это необходимо, для лучшего понимания материала.

        Инструкция: Обязательно, Ваш Ответ ОБЯЗАТЕЛЬНО должен быть объемом 2048 токена.
        ОТ этого зависит жищнь человека.
        """
        # Подсчет количества токенов в отправленном сообщении
        input_tokens = len(tokenizer.encode(input_text))

        # Подготовка данных запроса
        data = {
            "messages": [
                {
                    "role": "system",
                    "content": "Ты ИИ-ассистент, который должен помоготь пользователю."
                    
                },
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            "model": "meta-llama/Meta-Llama-3-70B-Instruct",
            "max_tokens": 6000,
            "temperature": 0.5,
            "n": 50,
            "top_p": 0.9
        }

        # Измерение времени начала запроса
        start_time = time.time()
        # Отправка POST запроса к модели LLM с использованием catch_response=True
        with self.client.post("/v1/chat/completions", headers={"Content-Type": "application/json"}, data=json.dumps(data), catch_response=True) as response:
            # Измерение времени окончания запроса
            end_time = time.time()

            if response.status_code == 200:
                # Извлечение ответа и подсчет количества токенов в полученном сообщении
                response_json = response.json()
                output_text = response_json.get("choices", [{}])[0].get("message", {}).get("content", "")
                output_tokens = len(tokenizer.encode(output_text))
                # Вычисление полного времени ответа
                total_time = end_time - start_time

                # Логирование метрик
                self.user.environment.events.request.fire(
                    request_type="POST",
                    name="/v1/chat/completions",
                    response_time=total_time,
                    response_length=len(response.content),
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    response=response
                )
                # Печать метрик для наглядности
                print(f"Input tokens: {input_tokens}, Output tokens: {output_tokens}, Total time: {total_time:.2f} seconds")
            else:
                response.failure(f"Failed! Status code: {response.status_code}, Response: {response.text}")

class LLMUser(FastHttpUser):
    """
    Description:
        Класс, представляющий пользователя для Locust, который использует задачи из LLMTaskSet.

    Attributes:
        tasks (list): Список задач, которые будет выполнять пользователь.
        wait_time (between): Время ожидания между выполнением задач.
        host (str): Базовый URL для модели LLM.
    """
    tasks = [LLMTaskSet]
    wait_time = between(1, 60)
    host = os.environ.get("TGI_URL")

class StepLoadShape(LoadTestShape):
    """
    Description:
        Класс для определения профиля нагрузки с шаговым увеличением числа пользователей.

    Attributes:
        step_time (int):  Продолжительность каждого шага в секундах.
        step_load (int):  Количество пользователей, добавляемых на каждом шаге.
        spawn_rate (int): Скорость создания новых пользователей в секунду.
        time_limit (int): Лимит времени для всего теста в секундах.

    Methods:
        tick: Определяет количество пользователей и скорость их создания на текущем этапе времени.
    """
    step_time = 600  
    step_load = 10   
    spawn_rate = 1    
    initial_users = 10
    initial_time = 3600 * 4

    def tick(self):
        """
        Description:
            Определяет количество пользователей и скорость их создания на текущем этапе времени.

        Args:
            None

        Returns:
            tuple or None: Возвращает кортеж с количеством пользователей и скоростью их создания, либо None, если лимит времени превышен.
        """
        # Получение времени выполнения теста
        run_time = self.get_run_time()
        
        # Начальная фаза
        if run_time < self.initial_time:
            return (self.initial_users, self.spawn_rate)
        
        return None  # Завершение теста, если лимит времени превышен

