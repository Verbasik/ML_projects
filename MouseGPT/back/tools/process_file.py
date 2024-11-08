# back/tools/process_file.py
# ============================
# БЛОК ИМПОРТОВ
# ============================
# Импорт стандартных библиотек
import os
from pathlib import Path

# Импорт внешних библиотек
from werkzeug.utils import secure_filename

# LangSmith импорты:
from langsmith import traceable

# Импорт внутренних библиотек
from back.tools.pdf_loader import pdf_loader
from back.tools.ipynb_loader import ipynb_loader
from back.tools.transcribe_media import transcribe_media, merge_chunks

@traceable
def process_file(file, agent, file_manager, session, process_func, chunk_prompt_type: str) -> str:
    """
    Description:
        Обрабатывает загруженные файлы (PDF, IPYNB, видео, аудео) и создает суммаризацию.

    Args:
        file: Загруженный файл.
        agent: Экземпляр агента для обработки текста.
        file_manager: Менеджер для работы с файлами.
        session: Сессия для хранения информации о файлах.
        process_func: Функция для обработки конкретного типа файла.
        chunk_prompt_type: Тип запроса для обработки чанков.

    Returns:
        Имя файла с суммаризацией.
    
    Raises:
        ValueError: Если файл не выбран.
    """
    from app import app

    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    file_base_name = os.path.splitext(filename)[0]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Проверяем, если функция требует только file_path
    if process_func.__name__ == 'process_ipynb_file':
        chunks = process_func(file_path)
    else:
        chunks = process_func(file_manager, session, file_path)

    if not chunks:
        print("❌ No chunks received from process_func")
        return "Error: No content to summarize"
    
    summary_filename = f"{file_base_name}_summary.md"
    summary = ""

    # Проверяем, существует ли файл
    file_exists = Path(file_manager.working_directory / summary_filename).exists()

    # Генерация суммаризации по чанкам
    total_chunks = len(chunks)
    print(f"🚀 Начинаем обработку {total_chunks} чанков текста.")
    print("📊 " + "-" * 50)

    for i, chunk in enumerate(chunks, 1):
        progress = i/total_chunks*100
        print(f"⏳ Обработка чанка {i}/{total_chunks} [{progress:.1f}%]")
        
        prompt = file_manager.read_document(
            f'prompts/{chunk_prompt_type}_chank_prompt.txt'
        ) + "\n" + chunk
        summarized_content = agent.process_message({"content": prompt})
        
        print(f"📝 Результат суммаризации чанка {i}:")
        print(f"✨ Суммаризация выполнена успешно")
        print("📊 " + "-" * 50)
        
        summary += summarized_content + "\n"
        
        if i == 0 and not file_exists:
            print(f"📁 Создание нового файла суммаризации")
            file_manager.write_document(
                f"# Summarization for {file_base_name}\n\n## Chunk {i+1}\n{summarized_content}\n",
                summary_filename
            )
        else:
            print(f"📎 Добавление данных в существующий файл")
            file_manager.append_document(
                f"\n## Chunk {i+1}\n{summarized_content}\n",
                summary_filename
            )

    # Финальная суммаризация
    print("🎯 Подготовка финальной суммаризации...")
    final_summary_prompt = f"Summarize the following text in a concise manner:\n\n{summary}"
    final_summary = agent.process_message({"content": final_summary_prompt})
    
    # Добавляем финальную суммаризацию к существующему файлу
    print("📌 Сохранение финальной суммаризации")
    file_manager.append_document(
        "\n## Final Summary\n" + final_summary + "\n",
        summary_filename
    )
    
    session['summary_filename'] = summary_filename
    print("✅ Обработка файла успешно завершена!")

    return summary_filename


def process_pdf_file(file_manager, session, file_path: str) -> list[str]:
    """
    Description:
        Обрабатывает PDF файл, создавая FAISS индекс и возвращает содержание страниц.

    Args:
        file_manager: Менеджер для работы с файлами.
        session: Сессия для хранения данных о файлах.
        file_path: Путь к PDF файлу.

    Returns:
        Список страниц PDF файла в текстовом формате.
    """
    from app import app

    pdf_pages, faiss_index = pdf_loader(file_path)
    
    # Сохранение Faiss индекса
    unique_filename = os.path.join(app.config['UPLOAD_FOLDER'], f"{os.path.splitext(os.path.basename(file_path))[0]}.faiss")
    file_manager.save_faiss_index(faiss_index.index, unique_filename)
    session['faiss_index_filename'] = unique_filename

    return [page.page_content for page in pdf_pages]


def process_ipynb_file(file_path: str) -> list[str]:
    """
    Description:
        Обрабатывает Jupyter Notebook файл, возвращая его содержание.

    Args:
        file_path: Путь к IPYNB файлу.

    Returns:
        Список строк с содержанием IPYNB файла.
    """
    return ipynb_loader(file_path)

def process_audio_file(file_path: str) -> list[str]:
    """
    Description:
        Обрабатывает аудиофайл: транскрибирует его и объединяет чанки.

    Args:
        file_path: Путь к аудиофайлу.

    Returns:
        Список объединенных чанков транскрибированного текста.
    """
    transcribed_chunks = transcribe_media(file_path)
    merged_chunks = merge_chunks(transcribed_chunks)
    return merged_chunks


def process_video_file(file_manager, session, file_path: str) -> list[str]:
    """
    Description:
        Обрабатывает видеофайл, транскрибируя его в текстовые чанки.

    Args:
        file_manager: Менеджер для работы с файлами.
        session: Сессия для хранения данных о файлах.
        file_path: Путь к видеофайлу.

    Returns:
        Список строк с транскрибированным содержанием видео.
    """
    transcribed_chunks = transcribe_media(file_path)
    if not transcribed_chunks or not isinstance(transcribed_chunks[0], str):
        print("Error: Transcription failed or returned non-text data")
        return ["Error: Video transcription failed"]
    
    # Объединяем небольшие чанки
    merged_chunks = merge_chunks(transcribed_chunks)
    
    return merged_chunks
