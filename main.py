from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

# Инициализация OpenAI с вашим ключом
openai.api_key = ''

# Инициализация бота Telegram
updater = Updater(token='', use_context=True)

dispatcher = updater.dispatcher

# Функция для обработки команд
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\!',
        reply_markup=ForceReply(selective=True),
    )

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# Функция для обработки текстовых сообщений
def echo(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text},
        ]
    )
    update.message.reply_text(response['choices'][0]['message']['content'])

echo_handler = MessageHandler(Filters.text & ~Filters.command, echo)
dispatcher.add_handler(echo_handler)

# Запуск бота
updater.start_polling()

updater.idle()
