import os

# Базовые настройки
PORT = int(os.getenv("PORT", 5000))
WEBHOOK_URL = os.getenv("APP_LINK") if os.getenv("APP_LINK") else None

# Настройки моделей
DEFAULT_MODEL = "gpt-4o"
AVAILABLE_MODELS = {
    "gpt4": "gpt-4o",
    "gpt3": "gpt-3.5-turbo",
    "claude35": "claude-3-5-sonnet",
    "claude37": "claude-3-7-sonnet",
}

# Определяем, какие модели к какому провайдеру относятся
MODEL_PROVIDERS = {
    "gpt-4o": "openai",
    "gpt-3.5-turbo": "openai",
    "claude-3-5-sonnet": "anthropic",
    "claude-3-7-sonnet": "anthropic",
}

# Лимиты и настройки контекста
MAX_HISTORY_LENGTH = 10  # Максимальное количество сообщений в истории
MAX_TOKENS = 1000  # Максимальное количество токенов на ответ

# Системные сообщения для разных моделей
SYSTEM_MESSAGES = {
    "gpt-4o": "Вы - полезный и дружелюбный ассистент, встроенный в Telegram бота.",
    "gpt-3.5-turbo": "Вы - полезный и дружелюбный ассистент, встроенный в Telegram бота.",
    "claude-3-5-sonnet": "Вы - полезный и дружелюбный ассистент Claude, встроенный в Telegram бота.",
    "claude-3-7-sonnet": "Вы - полезный и дружелюбный ассистент Claude, встроенный в Telegram бота."
}

# Тексты сообщений
WELCOME_MESSAGE = """
Привет, {}! Я бот с интегрированными ИИ-моделями. 
Просто напишите мне ваш вопрос, и я постараюсь помочь.

Доступные команды:
/help - получить справку
/reset - сбросить историю диалога
/model - выбрать модель ИИ
"""

HELP_MESSAGE = """
Я бот с интегрированными ИИ-моделями. Вы можете задавать мне любые вопросы!

Доступные команды:
/start - начать или перезапустить бота
/help - показать это сообщение
/reset - сбросить историю нашего диалога
/model - выбрать модель ИИ

Доступные модели:
- gpt4 (GPT-4o от OpenAI)
- gpt3 (GPT-3.5-turbo от OpenAI)
- claude35 (Claude 3.5 Sonnet от Anthropic)
- claude37 (Claude 3.7 Sonnet от Anthropic)

Я запоминаю контекст нашего разговора, чтобы давать более точные ответы.
"""

MODEL_HELP_MESSAGE = """
Пожалуйста, укажите модель после команды.
Например: /model gpt4

Доступные модели:
- gpt4 (GPT-4o от OpenAI, более мощная, но медленнее)
- gpt3 (GPT-3.5-turbo от OpenAI, быстрее, но менее мощная)
- claude35 (Claude 3.5 Sonnet от Anthropic, хороший баланс скорости и качества)
- claude37 (Claude 3.7 Sonnet от Anthropic, самая мощная модель)
"""