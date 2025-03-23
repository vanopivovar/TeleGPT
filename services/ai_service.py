import logging
from typing import List, Dict, Optional
from services import openai_service, anthropic_service

# Настройка логирования
logger = logging.getLogger(__name__)

# Определение провайдеров напрямую в этом файле
MODEL_PROVIDERS = {
    "gpt-4o": "openai",
    "gpt-3.5-turbo": "openai",
    "claude-3-5-sonnet": "anthropic",
    "claude-3-7-sonnet": "anthropic",
}

# Маппинг для полных имен моделей Anthropic
# Использование текущих моделей без дат в именах
ANTHROPIC_MODEL_NAMES = {
    "claude-3-5-sonnet": "claude-3-5-sonnet",
    "claude-3-7-sonnet": "claude-3-7-sonnet"
}

async def get_completion(messages: List[Dict[str, str]], model: str) -> Optional[str]:
    """
    Маршрутизатор для выбора соответствующего API сервиса в зависимости от модели.
    
    Args:
        messages: Список сообщений для API
        model: Название модели для использования
    
    Returns:
        Ответ от модели или None в случае ошибки
    """
    # Определяем провайдера на основе названия модели
    provider = MODEL_PROVIDERS.get(model)
    
    logger.info(f"Используем модель {model} от провайдера {provider}")
    
    if provider == "openai":
        return await openai_service.get_completion(messages, model)
    elif provider == "anthropic":
        # Используем полное имя модели для Anthropic
        full_model_name = ANTHROPIC_MODEL_NAMES.get(model, model)
        logger.info(f"Полное имя модели Anthropic: {full_model_name}")
        return await anthropic_service.get_completion(messages, full_model_name)
    else:
        logger.error(f"Неизвестный провайдер для модели {model}")
        return "Извините, указанная модель не поддерживается. Пожалуйста, выберите другую модель с помощью команды /model."