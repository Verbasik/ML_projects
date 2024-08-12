# ============================
# БЛОК ИМПОРТОВ
# ============================
# Импорт аннотаций типов
from typing import Any, Dict, List

# Импорт для поиска по векторным представлениям
import faiss

# Импорт библиотек LangChain
from langchain_openai import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain_community.vectorstores import FAISS

class BaseAgent():
    """
    Базовый класс для создания агентов.
    """

    def __init__(self, llm, system_prompt, tools: List[Any] = None):
        """
        Description:
            Инициализация агента.

        Args:
            tools: Список инструментов, доступных агенту.
        """
        self.system_prompt = system_prompt
        self.llm = llm
        self.messages: List[Dict[str, Any]] = []

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Description:
            Обрабатывает входящее сообщение и возвращает ответ.

        Args:
            message: Входящее сообщение.

        Returns:
            Ответ агента.
        """
        # Добавляем входящее сообщение в историю
        self.messages.append({"role": "user", "content": message["content"]})
        
        response = self.llm.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", 
                 "content": self.system_prompt},
                *self.messages
            ]
        ).choices[0].message.content

        # Добавляем ответ агента в историю
        self.messages.append({"role": "assistant", "content": response})

        return response
    
    def search_rag(self, query: str, index: FAISS) -> str:
        """
        Description:
            Выполняет поиск по базе знаний (RAG) и возвращает ответ.
        
        Args:
            query: Запрос пользователя.
            index: Faiss индекс для поиска.
        
        Returns:
            Ответ на основе RAG.
        """
        # Создаем цепочку для вопрос-ответ
        qa_chain = load_qa_chain(ChatOpenAI(model_name="gpt-4o-mini"), chain_type="map_reduce")
        
        # Выполняем поиск
        docs = index.similarity_search(query)
        
        # Генерируем ответ
        answer = qa_chain.invoke({
            "input_documents": docs, 
            "question": query
        })
        
        return answer

    def save_faiss_index(self, index: faiss.Index, filename: str):
        """
        Description:
            Сохраняет FAISS индекс в файл.

        Args:
            index: FAISS индекс для сохранения.
            filename: Имя файла для сохранения.
        """
        try:
            index.save(filename)
            print(f"FAISS index saved to {filename}")
        except Exception as e:
            print(f"Error saving FAISS index: {e}")

    def load_faiss_index(self, filename: str) -> faiss.Index:
        """
        Description:
            Загружает FAISS индекс из файла.

        Args:
            filename: Имя файла для загрузки индекса.

        Returns:
            faiss.Index: Загруженный FAISS индекс.
        """
        try:
            index = faiss.read_index(filename)
            print(f"FAISS index loaded from {filename}")
            return index
        except Exception as e:
            print(f"Error loading FAISS index: {e}")
            return None