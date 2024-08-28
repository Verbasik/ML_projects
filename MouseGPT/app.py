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
from back.tools.pdf_loader   import pdf_loader
from back.tools.ipynb_loader import ipynb_loader
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
HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')
LANGCHAIN_TRACING_V2     = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_API_KEY        = os.getenv('LANGCHAIN_API_KEY')
TAVILY_API_KEY           = os.getenv('TAVILY_API_KEY')
OPENAI_API_KEY           = os.environ['OPENAI_API_KEY']

# Инициализация логгера
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('socketio').setLevel(logging.DEBUG)
logging.getLogger('engineio').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

# Инициализация клиента OpenAI
openai.api_key = OPENAI_API_KEY

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

@traceable
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
        # Возврат на страницу, если файл не был загружен
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # Возврат на страницу, если файл не выбран
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('process_pdf', file_path=file_path))
    
    return render_template('html/home.html')

@traceable
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
    if file.filename == '':
        return "No selected file", 400

    # Сохранение файла на сервере
    filename = secure_filename(file.filename)
    file_base_name = os.path.splitext(filename)[0]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    pdf_pages, faiss_index = pdf_loader(file_path)
    
    # Создаем Faiss индекс на основе PDF файла
    unique_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{file_base_name}.faiss")
    file_manager.save_faiss_index(faiss_index.index, unique_filename)

    # Итеративная суммаризация
    summary = ""
    summary_filename = f"{file_base_name}.md"

    for page in pdf_pages:
        prompt = file_manager.read_document('prompts/chank_prompt.txt') + "\n" + page.page_content
        summarized_content = agent.process_message({"content": prompt})
        summary += summarized_content + "\n"
        file_manager.append_document(summarized_content, summary_filename)

    # Запись окончательной суммаризации
    file_manager.write_document(summary, summary_filename)

    # Сохранение имен файлов в сессии для дальнейшего использования
    session['summary_filename'] = summary_filename
    session['faiss_index_filename'] = unique_filename

    return f"Faiss indices and file summarization are ready: {summary_filename}"

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
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    file_base_name = os.path.splitext(filename)[0]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Загрузка и обработка .ipynb файла
    chunks = ipynb_loader(file_path)
    
    summary = ""
    summary_filename = f"{file_base_name}.md"
    for chunk in chunks:
        prompt = file_manager.read_document('prompts/chank_prompt.txt') + "\n" + chunk
        summarized_content = agent.process_message({"content": prompt})
        summary += summarized_content + "\n"
        file_manager.append_document(summarized_content, summary_filename)

    file_manager.write_document(summary, summary_filename)

    session['summary_filename'] = summary_filename

    return f"Notebook summarization is ready: {summary_filename}"


@traceable
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
    if message:
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

