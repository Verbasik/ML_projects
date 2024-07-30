# Импорт стандартных библиотек
import os
import logging
from pathlib import Path

# Импорт библиотеки для загрузки переменных окружения из файла .env
from dotenv import load_dotenv

# Импорт аннотаций типов
from typing import Any, Dict, List

# Импорт внешних библиотек
import openai
from pydantic import BaseModel
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename

# Импорт библиотек LangChain
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.schema import AgentAction, AgentFinish
from langchain.chains.combine_documents.map_reduce import MapReduceDocumentsChain
from langchain.docstore.document import Document

# Импорт внутренних библиотек
from back.file_manager import FileManager
from back.tools.pdf_loader import pdf_loader
from back.agent import BaseAgent

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение API ключей из переменной окружения
HUGGINGFACEHUB_API_TOKEN = os.getenv('HUGGINGFACEHUB_API_TOKEN')
LANGCHAIN_TRACING_V2     = os.getenv('LANGCHAIN_TRACING_V2')
LANGCHAIN_API_KEY        = os.getenv('LANGCHAIN_API_KEY')
TAVILY_API_KEY           = os.getenv('TAVILY_API_KEY')
OPENAI_API_KEY           = os.environ['OPENAI_API_KEY']

openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Flask веб-приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SECRET!'
app.config['UPLOAD_FOLDER'] = os.getcwd()
socketio = SocketIO(app)
file_manager = FileManager(working_directory=os.getcwd())

# Инициализация агента
agent = BaseAgent(
    llm=openai,
    system_prompt=file_manager.read_document('prompts/system_prompt.txt'),
    tools=[]
)
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
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            return redirect(url_for('process_pdf', file_path=file_path))
    
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
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    pdf_pages = pdf_loader(file_path)

    # Итеративная суммаризация
    summary = ""
    for page in pdf_pages:
        prompt = file_manager.read_document('prompts/chank_prompt.txt') + "\n" + page.page_content
        summarized_content = agent.process_message({"content": prompt})
        summary += summarized_content + "\n"
        file_manager.append_document(summarized_content, 'summary.md')

    # Запись окончательной суммаризации
    file_manager.write_document(summary, 'final_summary.md')

    # Чтение окончательной суммаризации для отображения в веб-интерфейсе
    final_summary_content = file_manager.read_document('final_summary.md')

    return final_summary_content
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
    return send_from_directory(file_manager.working_directory, 'final_summary.md', as_attachment=True)
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
        response = agent.process_message({"content": message})
        emit('response', {'message': response["content"]})

if __name__ == '__main__':
    socketio.run(app, debug=True)
