import os
import logging
import time
import random
import asyncio
import json
from typing import List, Dict, Optional
import anthropic
from bot.config import MAX_TOKENS, SYSTEM_MESSAGES

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
        return "Ошибка: API ключ для Anthropic не настроен. Пожалуйста, выберите модель OpenAI."
    
    logger.info(f"Используем модель Anthropic: {model}")
    
    try:
        # Проверяем, создан ли клиент Anthropic
        client = anthropic.Anthropic(api_key=api_key)
        logger.info("Клиент Anthropic создан успешно")
        
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
        logger.info(f"Отправляем в Anthropic API: модель={model}, сообщения={len(anthropic_messages)}")
        
        # Проверяем доступные модели
        available_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-3-5-sonnet-20240620",
            "claude-3-7-sonnet-20240307",
            "claude-instant-1.2",
            "claude-2.0",
            "claude-2.1"
        ]
        logger.info(f"Попытка использовать библиотеку anthropic с моделью {model}. Доступные модели: {available_models}")
        
        # Пробуем использовать последние версии моделей
        if model == "claude-3-5-sonnet":
            model = "claude-3-5-sonnet-20240620"
        elif model == "claude-3-7-sonnet":
            model = "claude-3-7-sonnet-20240307"
        
        logger.info(f"Используем актуальную модель: {model}")
        
        # Вызываем API Anthropic
        response = client.messages.create(
            model=model,
            system=system_content,
            messages=anthropic_messages,
            max_tokens=MAX_TOKENS
        )
        
        # Возвращаем ответ
        return response.content[0].text
    
    except anthropic.NotFoundError as e:
        logger.error(f"Модель не найдена: {str(e)}")
        return f"Модель {model} не найдена. Пожалуйста, выберите другую модель с помощью команды /model."
    
    except anthropic.RateLimitError:
        logger.warning("Anthropic API rate limit exceeded")
        # Увеличиваем интервал при превышении лимита
        last_request_time = time.time()
        return "Извините, превышен лимит запросов к API. Пожалуйста, попробуйте позже."
    
    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {str(e)}")
        return f"Ошибка в Anthropic API: {str(e)}. Пожалуйста, попробуйте другую модель."
    
    except anthropic.APIConnectionError:
        logger.error("Failed to connect to Anthropic API")
        return "Извините, не удалось соединиться с сервером. Пожалуйста, попробуйте позже."
    
    except anthropic.APITimeoutError:
        logger.error("Anthropic API request timed out")
        return "Извините, запрос к серверу превысил время ожидания. Пожалуйста, попробуйте позже."
    
    except AttributeError as e:
        logger.error(f"AttributeError: {str(e)}")
        return f"Ошибка атрибута при работе с Anthropic API: {str(e)}. Попробуйте другую модель."
    
    except Exception as e:
        logger.error(f"Error in Anthropic API request: {str(e)}", exc_info=True)
        return f"Произошла ошибка при обработке запроса: {str(e)}. Пожалуйста, попробуйте использовать модель OpenAI."