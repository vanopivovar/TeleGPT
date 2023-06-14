from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import openai
import os

# Инициализация OpenAI с вашим ключом
openai.api_key = os.getenv('OPENAI_TOKEN')

# Инициализация бота Telegram
updater = Updater(token=os.getenv('BOT_TOKEN'), use_context=True)

dispatcher = updater.dispatcher

# Функция для обработки команд
def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}, you use ChatGPT 3.5 model! Please, ask me\!',
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

# Запуск бота с использованием вебхука
PORT = int(os.environ.get('PORT', 5000))
updater.start_webhook(listen="0.0.0.0",
                      port=int(PORT),
                      url_path=os.getenv('BOT_TOKEN'))
updater.bot.set_webhook("https://pivovar-gpt-bot.herokuapp.com/" + os.getenv('BOT_TOKEN'))
updater.idle()
