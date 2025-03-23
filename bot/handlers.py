import logging
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from bot.storage import storage
from bot.config import WELCOME_MESSAGE, HELP_MESSAGE, MODEL_HELP_MESSAGE, AVAILABLE_MODELS, SYSTEM_MESSAGES
from services.openai_service import get_completion

# Настройка логирования
logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start."""
    user = update.effective_user
    user_id = user.id
    
    # Сбрасываем историю диалога
    storage.reset_messages(user_id)
    
    # Добавляем системное сообщение в историю
    model = storage.get_model(user_id)
    storage.add_message(user_id, "system", SYSTEM_MESSAGES[model])
    
    # Отправляем приветственное сообщение
    await update.message.reply_text(
        WELCOME_MESSAGE.format(user.first_name),
        parse_mode=ParseMode.MARKDOWN
    )

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /help."""
    await update.message.reply_text(HELP_MESSAGE)

async def reset_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /reset."""
    user_id = update.effective_user.id
    
    # Сбрасываем историю диалога
    storage.reset_messages(user_id)
    
    # Добавляем системное сообщение в историю
    model = storage.get_model(user_id)
    storage.add_message(user_id, "system", SYSTEM_MESSAGES[model])
    
    await update.message.reply_text(
        "История диалога сброшена. Теперь мы можем начать новый разговор!"
    )

async def model_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /model."""
    user_id = update.effective_user.id
    
    # Проверяем, указана ли модель
    if not context.args:
        await update.message.reply_text(MODEL_HELP_MESSAGE)
        return
    
    model_key = context.args[0].lower()
    
    # Проверяем, существует ли указанная модель
    if model_key not in AVAILABLE_MODELS:
        await update.message.reply_text(
            f"Модель '{model_key}' не найдена. {MODEL_HELP_MESSAGE}"
        )
        return
    
    # Устанавливаем новую модель
    model = AVAILABLE_MODELS[model_key]
    storage.set_model(user_id, model)
    
    # Сбрасываем историю диалога при смене модели
    storage.reset_messages(user_id)
    
    # Добавляем системное сообщение для новой модели
    storage.add_message(user_id, "system", SYSTEM_MESSAGES[model])
    
    await update.message.reply_text(
        f"Модель изменена на {model_key}. История диалога сброшена."
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик текстовых сообщений."""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # Отправляем индикатор набора текста
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    # Сохраняем сообщение пользователя
    storage.add_message(user_id, "user", user_message)
    
    # Получаем модель пользователя
    model = storage.get_model(user_id)
    
    # Получаем историю сообщений
    messages = storage.get_messages(user_id)
    
    # Получаем ответ от OpenAI
    response = await get_completion(messages, model)
    
    if response:
        # Сохраняем ответ модели в историю
        storage.add_message(user_id, "assistant", response)
        
        # Отправляем ответ пользователю
        await update.message.reply_text(response)
    else:
        # Если получили пустой ответ (что не должно происходить, но на всякий случай)
        await update.message.reply_text(
            "Извините, произошла ошибка. Пожалуйста, попробуйте еще раз или используйте команду /reset."
        )
