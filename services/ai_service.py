import logging
from typing import List, Dict, Optional
from bot.config import MODEL_PROVIDERS
from services import openai_service, anthropic_service

# Настройка логирования
logger = logging.getLogger(__name__)

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
        return await anthropic_service.get_completion(messages, model)
    else:
        logger.error(f"Неизвестный провайдер для модели {model}")
        return "Извините, указанная модель не поддерживается. Пожалуйста, выберите другую модель с помощью команды /model."