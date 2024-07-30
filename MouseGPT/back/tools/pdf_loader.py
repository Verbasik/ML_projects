# Импорт аннотаций типов
from typing import List

# Импорт библиотек LangChain
from langchain_community.document_loaders import PyPDFLoader

def pdf_loader(file_path: str) -> List[str]:
    """
    Description:
      Загружает PDF-файл и возвращает список документов.

    Args:
        file_path: Путь к PDF-файлу.

    Returns:
        Список документов, загруженных из PDF-файла.

    Raises:
        FileNotFoundError: Если указанный файл не найден.
        ValueError: Если файл не является допустимым PDF.

    Examples:
        >>> pdf_loader("example.pdf")
        ['Document content as a string.']
    """
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    
    return docs