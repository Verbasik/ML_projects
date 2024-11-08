# back/file_manager.py
# ============================
# БЛОК ИМПОРТОВ
# ============================
# Импорт стандартных библиотек
import logging
from pathlib import Path

# Импорт аннотаций типов
from typing import Any

# Импорт для поиска по векторным представлениям
import faiss

# Импорт библиотек LangChain
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

class FileManager:
    """
    Description:
        Класс для управления файлами, включая чтение, запись и добавление содержимого.
    """
    logging.basicConfig(level=logging.INFO)

    def __init__(self, working_directory: str = 'temp'):
        """
        Description:
            Инициализация рабочей директории.

        Args:
            working_directory: Путь к рабочей директории.
        """
        # Создаем рабочую директорию
        self.working_directory = Path(working_directory).absolute()
        self.working_directory.mkdir(parents=True, exist_ok=True)
        logging.info("WORKING_DIRECTORY: %s", self.working_directory)

    def read_document(self, file_name: str) -> str:
        """
        Description:
            Читает и возвращает содержимое файла.

        Args:
            file_name (str): Имя файла для чтения.

        Returns:
            str: Содержимое файла.
        """
        return FileManager._read_document(self.working_directory, file_name)

    @staticmethod
    def _read_document(working_directory: Path, file_name: str) -> str:
        """
        Description:
            Вспомогательный метод для чтения содержимого файла.

        Args:
            working_directory: Рабочая директория.
            file_name (str): Имя файла для чтения.

        Returns:
            str: Содержимое файла.
        """
        # Создаем путь к файлу с учетом рабочей директории
        file_path = working_directory / file_name.lstrip('/')
        logging.info(f"Attempting to read file from path: {file_path}")

        try:
            # Открываем файл для чтения
            with file_path.open("r", encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            # Логируем ошибку и возвращаем сообщение об ошибке
            logging.error(f"File {file_name} not found at path: {file_path}")
            return f"File {file_name} not found."

    def write_document(self, content: str, file_name: str) -> str:
        """
        Description:
            Создает и сохраняет текстовый документ.

        Args:
            content: Текстовое содержимое для записи в файл.
            file_name: Имя файла для сохранения.

        Returns:
            str: Сообщение о сохранении файла.
        
        Raises:
            FileNotFoundError: Если файл не найден.
        """
        return FileManager._write_document(self.working_directory, content, file_name)

    @staticmethod
    def _write_document(working_directory: Path, content: str, file_name: str) -> str:
        """
        Description:
            Вспомогательный метод для записи документа.

        Args:
            working_directory: Рабочая директория.
            content: Текстовое содержимое для записи в файл.
            file_name: Имя файла для сохранения.

        Returns:
            str: Сообщение о сохранении файла.
        
        Raises:
            FileNotFoundError: Если файл не найден.
        """
        # Создаем путь к файлу и необходимые директории
        file_path = working_directory / file_name.lstrip('/')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Открываем файл для записи
            with file_path.open("w", encoding='utf-8') as file:
                file.write(content)
            return f"Document saved to {file_name}"
        except IOError as e:
            # Логируем ошибку и возвращаем сообщение об ошибке
            logging.error(f"Error writing to file {file_name}: {e}")
            return f"Error writing to file {file_name}: {e}"

    def append_document(self, content: str, file_name: str) -> str:
        """
        Description:
            Добавляет содержимое в конец существующего файла.

        Args:
            content: Текстовое содержимое для добавления в файл.
            file_name: Имя файла для добавления содержимого.

        Returns:
            str: Сообщение о сохранении файла.
        """
        return FileManager._append_document(self.working_directory, content, file_name)

    @staticmethod
    def _append_document(working_directory: Path, content: str, file_name: str) -> str:
        """
        Description:
            Вспомогательный метод для добавления содержимого в документ.

        Args:
            working_directory: Рабочая директория.
            content: Текстовое содержимое для добавления в файл.
            file_name: Имя файла для добавления содержимого.

        Returns:
            str: Сообщение о сохранении файла.
        """
        # Создаем путь к файлу и необходимые директории
        file_path = working_directory / file_name.lstrip('/')
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Открываем файл для добавления содержимого
            with file_path.open("a", encoding='utf-8') as file:
                file.write(content)
            return f"Document appended to {file_name}"
        except IOError as e:
            # Логируем ошибку и возвращаем сообщение об ошибке
            logging.error(f"Error appending to file {file_name}: {e}")
            return f"Error appending to file {file_name}: {e}"
        
    def save_faiss_index(self, index: Any, file_name: str) -> str:
        """
        Description:
            Сохраняет FAISS индекс в файл.

        Args:
            index: FAISS индекс для сохранения.
            file_name: Имя файла для сохранения индекса.

        Returns:
            str: Сообщение о сохранении индекса.
        """
        try:
            file_path = self.working_directory / file_name.lstrip('/')
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Сохранение индекса FAISS
            faiss.write_index(index, str(file_path))
            return f"FAISS index saved to {file_name}"
        except IOError as e:
            logging.error(f"Error saving FAISS index to file {file_name}: {e}")
            return f"Error saving FAISS index to file {file_name}: {e}"

    def load_faiss_index(self, file_name: str) -> Any:
        """
        Description:
            Загружает FAISS индекс из файла.

        Args:
            file_name: Имя файла для загрузки индекса.

        Returns:
            Any: Загруженный FAISS индекс.
        """
        try:
            file_path = self.working_directory / file_name.lstrip('/')
            
            # Загрузка индекса FAISS
            embeddings  = OpenAIEmbeddings()
            faiss_index = FAISS.load_local(file_path, embeddings, allow_dangerous_deserialization=True)
            return faiss_index
        except FileNotFoundError:
            logging.error(f"FAISS index file {file_name} not found at path: {file_path}")
            return None
        except IOError as e:
            logging.error(f"Error loading FAISS index from file {file_name}: {e}")
            return None