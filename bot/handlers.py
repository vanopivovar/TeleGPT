import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters
from telegram.constants import ParseMode

from bot.storage import storage
from bot.config import WELCOME_MESSAGE, HELP_MESSAGE, MODEL_HELP_MESSAGE, AVAILABLE_MODELS, SYSTEM_MESSAGES
from services.ai_service import get_completion

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
    """Обработчик команды /model - показывает кнопки для выбора модели."""
    # Создаем клавиатуру с кнопками для выбора модели
    keyboard = [
        [
            InlineKeyboardButton("GPT-4o", callback_data="model:gpt4"),
            InlineKeyboardButton("GPT-3.5", callback_data="model:gpt3")
        ],
        [
            InlineKeyboardButton("Claude 3.5", callback_data="model:claude35"),
            InlineKeyboardButton("Claude 3.7", callback_data="model:claude37")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Отправляем сообщение с кнопками
    await update.message.reply_text(
        "Выберите модель ИИ для общения:",
        reply_markup=reply_markup
    )

async def model_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатия на кнопку выбора модели."""
    query = update.callback_query
    await query.answer()  # Отвечаем на запрос, чтобы убрать индикатор загрузки
    
    # Получаем данные из callback
    data = query.data.split(":")
    if len(data) != 2 or data[0] != "model":
        await query.edit_message_text("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
        return
    
    model_key = data[1]
    user_id = update.effective_user.id
    
    # Проверяем, существует ли указанная модель
    if model_key not in AVAILABLE_MODELS:
        await query.edit_message_text(f"Модель '{model_key}' не найдена.")
        return
    
    # Устанавливаем новую модель
    model = AVAILABLE_MODELS[model_key]
    storage.set_model(user_id, model)
    
    # Сбрасываем историю диалога при смене модели
    storage.reset_messages(user_id)
    
    # Добавляем системное сообщение для новой модели
    storage.add_message(user_id, "system", SYSTEM_MESSAGES[model])
    
    # Отображаем название выбранной модели
    model_display_names = {
        "gpt4": "GPT-4o",
        "gpt3": "GPT-3.5 Turbo",
        "claude35": "Claude 3.5 Sonnet",
        "claude37": "Claude 3.7 Sonnet"
    }
    
    display_name = model_display_names.get(model_key, model)
    
    await query.edit_message_text(
        f"Вы выбрали модель: {display_name}. История диалога сброшена."
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
    
    # Логируем информацию о запросе
    logger.info(f"Пользователь {user_id} отправил сообщение, используя модель {model}")
    
    # Получаем ответ от соответствующего API
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