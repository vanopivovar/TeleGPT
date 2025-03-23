import os
import logging
from typing import List, Dict, Optional
import openai
from openai import OpenAI
from bot.config import MAX_TOKENS, SYSTEM_MESSAGES

# Инициализируем клиент OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_TOKEN"))

# Настройка логирования
logger = logging.getLogger(__name__)

async def get_completion(messages: List[Dict[str, str]], model: str) -> Optional[str]:
    """
    Получить ответ от OpenAI API.
    
    Args:
        messages: Список сообщений для API
        model: Название модели для использования
    
    Returns:
        Ответ от модели или None в случае ошибки
    """
    try:
        # Добавляем системное сообщение, если его нет
        if not any(msg["role"] == "system" for msg in messages):
            system_message = SYSTEM_MESSAGES.get(model, SYSTEM_MESSAGES["gpt-4o"])
            messages = [{"role": "system", "content": system_message}] + messages
            
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
