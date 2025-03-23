import os
import logging
import time
import random
import asyncio
from typing import List, Dict, Optional
import openai
from openai import OpenAI
from bot.config import MAX_TOKENS, SYSTEM_MESSAGES

# Инициализируем клиент OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))

# Настройка логирования
logger = logging.getLogger(__name__)

# Переменная для отслеживания времени последнего запроса
last_request_time = 0
min_request_interval = 1.5  # Минимальный интервал между запросами в секундах

async def get_completion(messages: List[Dict[str, str]], model: str) -> Optional[str]:
    """
    Получить ответ от OpenAI API с задержкой между запросами.
    
    Args:
        messages: Список сообщений для API
        model: Название модели для использования
    
    Returns:
        Ответ от модели или None в случае ошибки
    """
    global last_request_time
    
    try:
        # Добавляем системное сообщение, если его нет
        if not any(msg["role"] == "system" for msg in messages):
            system_message = SYSTEM_MESSAGES.get(model, SYSTEM_MESSAGES["gpt-4o"])
            messages = [{"role": "system", "content": system_message}] + messages
        
        # Вычисляем, сколько времени прошло с последнего запроса
        current_time = time.time()
        elapsed = current_time - last_request_time
        
        # Если прошло меньше минимального интервала, добавляем задержку
        if elapsed < min_request_interval:
            delay = min_request_interval - elapsed + random.uniform(0.1, 0.5)  # Добавляем небольшой случайный компонент
            logger.info(f"Добавляем задержку {delay:.2f} секунд между запросами к API")
            await asyncio.sleep(delay)
        
        # Обновляем время последнего запроса
        last_request_time = time.time()
        
        # Вызываем API OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=MAX_TOKENS,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
        
        # Возвращаем ответ
        return response.choices[0].message.content
    
    except openai.RateLimitError:
        logger.warning("OpenAI API rate limit exceeded")
        # Увеличиваем интервал при превышении лимита
        last_request_time = time.time()
        return "Извините, превышен лимит запросов к API. Пожалуйста, попробуйте позже."
    
    except openai.APIConnectionError:
        logger.error("Failed to connect to OpenAI API")
        return "Извините, не удалось соединиться с сервером. Пожалуйста, попробуйте позже."
    
    except openai.APITimeoutError:
        logger.error("OpenAI API request timed out")
        return "Извините, запрос к серверу превысил время ожидания. Пожалуйста, попробуйте позже."
    
    except Exception as e:
        logger.error(f"Error in OpenAI API request: {str(e)}")
        return "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже."