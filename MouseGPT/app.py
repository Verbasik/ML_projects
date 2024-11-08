# app.py
# ============================
# БЛОК ИМПОРТОВ
# ============================
# Импорт стандартных библиотек
import os
import logging

# Импорт библиотеки для загрузки переменных окружения из файла .env
from dotenv import load_dotenv

# Импорт внешних библиотек
import openai
from flask import Flask, render_template, redirect, url_for, send_from_directory, request, session
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

# Импорт внутренних библиотек
from back.tools.process_file import process_file, process_pdf_file, process_ipynb_file, process_video_file, process_audio_file
from back.file_manager import FileManager
from back.agent import BaseAgent

# LangSmith импорты:
from langsmith import traceable

# ============================
# БЛОК НАСТРОЕК И ИНИЦИАЛИЗАЦИИ
# ============================
# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение API ключей из переменной окружения
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# Централизованная конфигурация типов файлов
FILE_TYPES = {
    'pdf':      {'extensions': ['pdf'],                      'processor': process_pdf_file},
    'notebook': {'extensions': ['ipynb'],                    'processor': process_ipynb_file},
    'audio':    {'extensions': ['mp3', 'wav', 'ogg', 'm4a'], 'processor': process_audio_file},
    'video':    {'extensions': ['mp4', 'avi', 'mov'],        'processor': process_video_file}
}

# Инициализация логгера
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('socketio').setLevel(logging.DEBUG)
logging.getLogger('engineio').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# Инициализация клиента OpenAI
client = openai.api_key = OPENAI_API_KEY

# Инициализация файл-менеджера
file_manager = FileManager()

# Инициализация агента
agent = BaseAgent(
    llm=openai,
    system_prompt=file_manager.read_document('prompts/system_prompt.txt'),
    tools=[]
)

# ============================
# БЛОК НАСТРОЕК FLASK ПРИЛОЖЕНИЯ
# ============================
# Flask веб-приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET!'
app.config['UPLOAD_FOLDER'] = file_manager.working_directory
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    """
    Description:
        Обрабатывает загрузку файла на сервер.

    Args:
        None

    Returns:
        HTML-страница для загрузки файла или перенаправление после успешной загрузки.

    Raises:
        None
    """
    if request.method == 'POST':
        # Проверяем, есть ли файл в запросе
        if 'file' not in request.files:
            # Если файл отсутствует, возвращаемся на страницу загрузки
            return redirect(request.url)
        
        file = request.files['file']
        
        # Проверяем, выбран ли файл (пустое имя файла означает, что файл не выбран)
        if file.filename == '':
            # Если файл не выбран, возвращаемся на страницу загрузки
            return redirect(request.url)
        
        if file:
            # Получаем безопасное имя файла, чтобы избежать проблем с системой файлов
            filename = secure_filename(file.filename)
            
            # Формируем полный путь для сохранения файла
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Сохраняем файл на сервере
            file.save(file_path)
    
    # Если метод GET или файл не был успешно загружен, отображаем страницу загрузки
    return render_template('html/home.html')

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    """
    Description:
        Обрабатывает PDF файл и создает его суммаризацию.

    Args:
        None

    Returns:
        HTML-страница с суммаризацией PDF файла.

    Raises:
        None
    """
    if 'file_path' not in request.files:
        return "No file provided", 400

    file = request.files['file_path']
    summary_filename = process_file(file, agent, file_manager, session, process_pdf_file, 'text')
    return f"PDF summarization is ready: {summary_filename}"

@app.route('/process_ipynb', methods=['POST'])
def process_ipynb():
    """
    Description:
        Обрабатывает .ipynb файл и создает его суммаризацию.

    Args:
        None

    Returns:
        HTML-страница с суммаризацией .ipynb файла.

    Raises:
        None
    """
    if 'file_path' not in request.files:
        return "No file provided", 400

    file = request.files['file_path']
    summary_filename = process_file(file, agent, file_manager, session, process_ipynb_file, 'text')
    return f"Notebook summarization is ready: {summary_filename}"

@app.route('/process_audio', methods=['POST'])
def process_audio():
    """
    Description:
        Обрабатывает загруженный аудиофайл и создает его транскрипцию и суммаризацию.

    Args:
        None (данные получаются из request.files)

    Returns:
        str: Сообщение о готовности транскрипции и суммаризации аудио с именем файла суммаризации.
        tuple: В случае ошибки возвращает сообщение об ошибке и код состояния HTTP.

    Raises:
        None (исключения обрабатываются внутри функции)
    """
    if 'file_path' not in request.files:
        return "No file provided", 400

    file = request.files['file_path']
    summary_filename = process_file(file, agent, file_manager, session, process_audio_file, 'text')
    return f"Audio transcription and summarization are ready: {summary_filename}"

@app.route('/process_video', methods=['POST'])
def process_video():
    """
    Description:
        Обрабатывает загруженный видеофайл, транскрибирует его и создает суммаризацию.

    Args:
        None (данные получаются из request.files)

    Returns:
        str: Сообщение о готовности транскрибации и суммаризации видео с именем файла суммаризации.
        tuple: В случае ошибки возвращает сообщение об ошибке и код состояния HTTP.

    Raises:
        None (исключения обрабатываются внутри функции)
    """
    if 'file_path' not in request.files:
        return "No file provided", 400

    file = request.files['file_path']
    summary_filename = process_file(file, agent, file_manager, session, process_video_file, 'text')
    return f"Video transcription and summarization are ready: {summary_filename}"

@app.route('/download_summary')
def download_summary():
    """
    Description:
        Обрабатывает запрос на скачивание суммаризации PDF файла.

    Args:
        None

    Returns:
        Файл с суммаризацией PDF файла.

    Raises:
        None
    """
    try:
        # Убедимся, что файл существует перед попыткой его отправки
        summary_filename = session.get('summary_filename', None)
        if not summary_filename:
            return "Summary file not found", 404
        
        summary_path = os.path.join(file_manager.working_directory, summary_filename)
        if not os.path.exists(summary_path):
            return "Summary file not found", 404

        # Отправка файла клиенту
        return send_from_directory(file_manager.working_directory, summary_filename, as_attachment=True)
    
    except Exception as e:
        # Логирование ошибки для последующей диагностики
        logger.error(f"Error during file download: {e}")
        return "An error occurred while processing the download", 500
    
@socketio.on('message')
def handle_message(data):
    """
    Description:
        Обрабатывает сообщение от клиента и отправляет ответ от LLM.

    Args:
        data: Данные, отправленные клиентом.

    Returns:
        None
    """
    message = data.get('message')
    if "@RAG" in message:
        # Загружаем faiss индекс из сессии для дальнейшего использования
        faiss_index_filename = session.get('faiss_index_filename', None)

        if not faiss_index_filename:
            emit('response', {'message': 'Faiss index not found'})
            return
        
        # Загружаем соответствующий Faiss индекс (например, последний загруженный PDF файл)
        faiss_index = file_manager.load_faiss_index(faiss_index_filename)

        # Используем RAG для ответа на запрос
        response = agent.search_rag(message, faiss_index)
        
        # Преобразуем ответ в JSON-сериализуемый формат
        response_dict = {
            "output_text": response["output_text"]
        }
        
        emit('response', {'message': response_dict['output_text']})

# Запуск приложения
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5002, log_output=False)

