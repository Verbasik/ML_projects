# ============================
# БЛОК ИМПОРТОВ
# ============================
# Импорт внешних библиотек
import speech_recognition as sr
from pydub import AudioSegment
import math
import os
import time

def transcribe_media(file_path: str) -> list[str]:
    """
    Description:
        Транскрибирует аудио или видео файл на текст, разбивая на чанки по 30 секунд.

    Args:
        file_path: Путь к аудио или видео файлу.

    Returns:
        Список строк с транскрибированными текстовыми чанками медиа.
    
    Raises:
        Exception: Если возникает ошибка при транскрибировании.
    
    Examples:
        >>> transcribe_media("example.mp3")
        >>> transcribe_media("example.mp4")
        ['Первый чанк текста', 'Второй чанк текста', ...]
    """
    try:
        # Определяем, является ли файл видео по его расширению
        is_video = file_path.lower().endswith(('.mp4', '.avi', '.mov'))
        
        # Загрузка аудио/видео файла
        audio = AudioSegment.from_file(file_path)
        
        # Если это видео, конвертируем во временный аудио файл
        if is_video:
            temp_audio_path = "temp.wav"
            audio.export(temp_audio_path, format="wav")
        else:
            temp_audio_path = file_path
        
        recognizer = sr.Recognizer()
        
        # Работа с аудиофайлом
        with sr.AudioFile(temp_audio_path) as source:
            # Получаем длительность аудио в миллисекундах
            duration_ms = len(audio)
            
            # Определяем длительность чанка в миллисекундах
            chunk_duration_ms = 30 * 1000
            chunks_count = math.ceil(duration_ms / chunk_duration_ms)  # Количество чанков
            
            transcribed_chunks = []
            print(f"Начинаем распознавание речи. Всего чанков: {chunks_count}")
            print(f"Общая длительность аудио: {duration_ms / 1000:.2f} секунд")
            print("-" * 50)

            for i in range(chunks_count):
                # Определяем начало и конец текущего чанка
                start = i * chunk_duration_ms
                end = min((i + 1) * chunk_duration_ms, duration_ms)
                
                print(f"Обработка чанка {i+1}/{chunks_count} ({(i+1)/chunks_count*100:.1f}%)")
                print(f"Временной интервал: {start/1000:.2f}с - {end/1000:.2f}с")
                
                # Читаем часть аудио из источника
                audio_chunk = recognizer.record(source, duration=(end - start) / 1000, offset=start / 1000)
                
                # Пытаемся распознать текст для текущего чанка
                try:
                    text = recognizer.recognize_google(audio_chunk, language="ru-RU")
                    transcribed_chunks.append(text)
                    print(f"Распознанный текст: {text}")
                except sr.UnknownValueError:
                    # Если не удалось распознать текст, добавляем пустую строку
                    transcribed_chunks.append("")
                    print("❌ Не удалось распознать речь в этом фрагменте")
                except sr.RequestError as e:
                    error_message = f"Ошибка при запросе к сервису Google Speech Recognition: {e}"
                    print(f"⚠️ {error_message}")
                    transcribed_chunks.append(f"Error during recognition: {str(e)}")
                
                print("-" * 50)

                # Добавляем задержку между запросами
                time.sleep(1)

            print(f"Распознавание завершено. Обработано {chunks_count} чанков.")
            print(f"Общее количество распознанных фрагментов: {len([chunk for chunk in transcribed_chunks if chunk])}")
        
        # Удаляем временный аудио файл, если он был создан
        if is_video and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        
        return transcribed_chunks
    except Exception as e:
        # Обрабатываем общие исключения и возвращаем сообщение об ошибке
        print(f"Ошибка в функции transcribe_media: {str(e)}")
        return [f"Error during transcription: {str(e)}"]

def merge_chunks(chunks: list[str], min_chunk_length: int = 100, max_chunk_length: int = 1000) -> list[str]:
    """
    Description:
        Объединяет небольшие чанки текста в более крупные.

    Args:
        chunks: Список строк с текстовыми чанками.
        min_chunk_length: Минимальная длина чанка (в символах) для объединения.
        max_chunk_length: Максимальная длина объединенного чанка.

    Returns:
        Список объединенных чанков.
    
    Raises:
        None
    
    Examples:
        >>> merge_chunks(['Короткий чанк', 'Еще один короткий', 'Длинный чанк текста'])
        ['Короткий чанк Еще один короткий', 'Длинный чанк текста']
    """
    # Инициализируем список для хранения объединенных чанков
    merged_chunks = []
    # Инициализируем переменную для текущего объединяемого чанка
    current_chunk = ""

    # Проходим по всем чанкам в исходном списке
    for chunk in chunks:
        # Проверяем, не превысит ли длина текущего чанка максимально допустимую при добавлении нового
        if len(current_chunk) + len(chunk) <= max_chunk_length:
            # Если не превысит, добавляем новый чанк к текущему
            current_chunk += " " + chunk if current_chunk else chunk
        else:
            # Если превысит, добавляем текущий чанк в список объединенных (если он не пустой)
            if current_chunk:
                merged_chunks.append(current_chunk)
            # И начинаем новый текущий чанк
            current_chunk = chunk

        # Проверяем, достиг ли текущий чанк минимальной длины
        if len(current_chunk) >= min_chunk_length:
            # Если достиг, добавляем его в список объединенных
            merged_chunks.append(current_chunk)
            # И очищаем текущий чанк
            current_chunk = ""

    # После обработки всех чанков проверяем, остался ли непустой текущий чанк
    if current_chunk:
        # Если остался, добавляем его в список объединенных
        merged_chunks.append(current_chunk)

    # Возвращаем список объединенных чанков
    return merged_chunks
