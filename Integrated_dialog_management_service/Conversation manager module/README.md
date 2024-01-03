# Conversation Manager 🗣️

Модуль ConversationManager - это ключевая часть программы, которая управляет взаимодействиями в чате. Он эффективно сохраняет всё, что пользователи говорят, и упрощает процесс ответов модели. Реализация не только сохранила все основные функции из старого кода, но и улучшила работу с базой данных, где хранится история разговоров, обеспечивая более гладкую интеграцию с другими модулями программы.

## Ключевые Компоненты 🧩

- DBConnection 🗄️: Управляет подключением к базе данных SQLite, обеспечивая надежное хранение и доступ к истории диалогов. Этот компонент соответствует блоку "Dialog db" на схеме, отражая взаимодействие с базой данных.

- DialogueHistory 📜: Отвечает за операции с историей диалогов: инициализацию, обновление и извлечение информации. Этот компонент совпадает с функциональностью "Conversation manager" на схеме, обеспечивая централизованное управление историей диалога.

- ConversationManager 🤖: Интегрирует DBConnection и DialogueHistory, предоставляя унифицированный интерфейс для эффективного управления диалогами. Это соответствует "Conversation manager" на схеме, указывая на то, что модуль является центральным узлом для управления диалогами в системе.

## Работа Модуля 🔄

- Инициализация Диалога: Создаёт новую запись в базе данных при начале диалога.

- Добавление Сообщений: Вносит сообщения пользователей в историю, обеспечивая непрерывность диалога.

- Извлечение Истории: Позволяет получить полную историю общения с пользователем, что критически важно для контекстуализации ответов.

## Интеграция и Взаимодействие 🔄

ConversationManager легко интегрируется с другими компонентами системы, такими как обработчики запросов и модули формирования ответов, обеспечивая доступ к истории диалогов для более точной и контекстуальной работы.

## Пример Использования 📝

Для включения ConversationManager в ваш проект:

Создайте экземпляр класса с указанием пути к базе данных.
Используйте методы класса для управления историей диалогов.