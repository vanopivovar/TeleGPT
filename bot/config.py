import os

# Базовые настройки
PORT = int(os.getenv("PORT", 5000))
# WEBHOOK_URL = os.getenv("APP_LINK") + os.getenv("BOT_TOKEN") if os.getenv("APP_LINK") else None
WEBHOOK_URL = os.getenv("APP_LINK")  # Просто используйте URL приложения без добавления токена
# Настройки OpenAI
DEFAULT_MODEL = "gpt-4o"
AVAILABLE_MODELS = {
    "gpt4": "gpt-4o",
    "gpt3": "gpt-3.5-turbo"
}

# Лимиты и настройки контекста
MAX_HISTORY_LENGTH = 10  # Максимальное количество сообщений в истории
MAX_TOKENS = 1000  # Максимальное количество токенов на ответ

# Системные сообщения для разных моделей
SYSTEM_MESSAGES = {
    "gpt-4o": "Вы - полезный и дружелюбный ассистент, встроенный в Telegram бота.",
    "gpt-3.5-turbo": "Вы - полезный и дружелюбный ассистент, встроенный в Telegram бота."
}

# Тексты сообщений
WELCOME_MESSAGE = """
Привет, {}! Я бот с интегрированным GPT. 
Просто напишите мне ваш вопрос, и я постараюсь помочь.

Доступные команды:
/help - получить справку
/reset - сбросить историю диалога
/model - выбрать модель GPT
"""

HELP_MESSAGE = """
Я бот с интегрированным GPT. Вы можете задавать мне любые вопросы!

Доступные команды:
/start - начать или перезапустить бота
/help - показать это сообщение
/reset - сбросить историю нашего диалога
/model - выбрать модель GPT (доступны gpt4 и gpt3)

Я запоминаю контекст нашего разговора, чтобы давать более точные ответы.
"""

MODEL_HELP_MESSAGE = """
Пожалуйста, укажите модель после команды.
Например: /model gpt4

Доступные модели:
- gpt4 (GPT-4o, более мощная, но медленнее)
- gpt3 (GPT-3.5-turbo, быстрее, но менее мощная)
"""
