# Импорт аннотаций типов
from typing import Any, Dict, List

class AgentState():
    """
    Класс для представления состояния агента.
    """
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []

class BaseAgent(AgentState):
    """
    Базовый класс для создания агентов.
    """

    def __init__(self, llm, system_prompt, tools: List[Any] = None):
        """
        Инициализация агента.

        Args:
            tools: Список инструментов, доступных агенту.
        """
        super().__init__()
        self.system_prompt = system_prompt
        self.llm = llm
        self.tools = tools or []

    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
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

    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Вызывает инструмент по имени.

        Args:
            tool_name: Имя инструмента.
            **kwargs: Дополнительные аргументы для инструмента.

        Returns:
            Результат работы инструмента.
        """
        for tool in self.tools:
            if tool.__class__.__name__ == tool_name:
                return tool.run(**kwargs)
        raise ValueError(f"Инструмент '{tool_name}' не найден.")