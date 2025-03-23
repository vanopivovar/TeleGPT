import os
import logging
import time
import random
import asyncio
from typing import List, Dict, Optional
import anthropic
from bot.config import MAX_TOKENS, SYSTEM_MESSAGES

# Инициализируем клиент Anthropic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Настройка логирования
logger = logging.getLogger(__name__)

# Переменная для отслеживания времени последнего запроса
last_request_time = 0
min_request_interval = 1.5  # Минимальный интервал между запросами в секундах

async def get_completion(messages: List[Dict[str, str]], model: str) -> Optional[str]:
    """
    Получить ответ от Anthropic API с задержкой между запросами.
    
    Args:
        messages: Список сообщений для API
        model: Название модели для использования (полное имя)
    
    Returns:
        Ответ от модели или None в случае ошибки
    """
    global last_request_time
    
    # Логируем ключевую информацию
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY не настроен в переменных окружения")
        return "Ошибка: API ключ для Anthropic не настроен. Пожалуйста, обратитесь к администратору."
    
    logger.info(f"Используем модель Anthropic: {model}")
    logger.info(f"API ключ настроен: {api_key[:4]}...{api_key[-4:]}")
    
    try:
        # Преобразуем формат сообщений из telegram-openai в формат Anthropic
        system_content = ""
        anthropic_messages = []
        
        # Извлекаем системное сообщение
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
                break
        
        # Если системного сообщения нет, используем значение по умолчанию
        if not system_content:
            system_content = SYSTEM_MESSAGES.get(model, "Вы - полезный и дружелюбный ассистент Claude.")
        
        # Добавляем остальные сообщения
        for msg in messages:
            if msg["role"] != "system":
                anthropic_messages.append({
                    "role": "assistant" if msg["role"] == "assistant" else "user",
                    "content": msg["content"]
                })
        
        # Вычисляем, сколько времени прошло с последнего запроса
        current_time = time.time()
        elapsed = current_time - last_request_time
        
        # Если прошло меньше минимального интервала, добавляем задержку
        if elapsed < min_request_interval:
            delay = min_request_interval - elapsed + random.uniform(0.1, 0.5)
            logger.info(f"Добавляем задержку {delay:.2f} секунд между запросами к Anthropic API")
            await asyncio.sleep(delay)
        
        # Обновляем время последнего запроса
        last_request_time = time.time()
        
        # Логируем отправляемые данные
        logger.info(f"Отправляем в Anthropic API: система={system_content[:50]}..., сообщения={len(anthropic_messages)}")
        
        # Вызываем API Anthropic
        response = client.messages.create(
            model=model,
            system=system_content,
            messages=anthropic_messages,
            max_tokens=MAX_TOKENS
        )
        
        # Возвращаем ответ
        return response.content[0].text
    
    except anthropic.RateLimitError:
        logger.warning("Anthropic API rate limit exceeded")
        # Увеличиваем интервал при превышении лимита
        last_request_time = time.time()
        return "Извините, превышен лимит запросов к API. Пожалуйста, попробуйте позже."
    
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {str(e)}")
        # Подробно логируем ошибку
        error_details = f"Status: {e.status_code}, Type: {e.error_type}, Message: {e.message}"
        logger.error(error_details)
        return f"Ошибка в Anthropic API: {error_details}. Пожалуйста, попробуйте другую модель."
    
    except anthropic.APIConnectionError:
        logger.error("Failed to connect to Anthropic API")
        return "Извините, не удалось соединиться с сервером. Пожалуйста, попробуйте позже."
    
    except anthropic.APITimeoutError:
        logger.error("Anthropic API request timed out")
        return "Извините, запрос к серверу превысил время ожидания. Пожалуйста, попробуйте позже."
    
    except Exception as e:
        logger.error(f"Error in Anthropic API request: {str(e)}")
        return f"Произошла ошибка при обработке запроса: {str(e)}. Пожалуйста, попробуйте позже."