# back/tools/ipynb_loader.py
import nbformat
from   nbformat import read

def ipynb_loader(file_path: str):
    """
    Description:
      Загружает .ipynb файл и возвращает список документов.

    Args:
        file_path: Путь к .ipynb файлу.

    Returns:
        Список текстовых чанков, извлеченных из .ipynb файла.

    Raises:
        FileNotFoundError: Если указанный файл не найден.
        ValueError: Если файл не является допустимым .ipynb файлом.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        nb = read(f, as_version=4)
    
    # Проход по ячейкам и извлечение текста
    chunks = []
    for cell in nb.cells:
        if cell.cell_type == 'code' or cell.cell_type == 'markdown':
            chunks.append(cell.source)
    
    # Вернем список чанков для обработки
    return chunks
