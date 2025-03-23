# TeleGPT

Телеграм-бот с интеграцией OpenAI GPT для обработки запросов пользователей.

## Особенности

- Интеграция с моделями OpenAI (GPT-4o и GPT-3.5-turbo)
- Сохранение контекста разговора
- Выбор модели GPT для каждого пользователя
- Устойчивость к ошибкам API
- Поддержка как webhook, так и long polling
- Хранение данных в MongoDB

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/TeleGPT.git
cd TeleGPT
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Создайте файл `.env` с необходимыми переменными окружения:
```
BOT_TOKEN=ваш_токен_бота_телеграм
OPENAI_TOKEN=ваш_ключ_api_openai
MONGODB_URI=ваша_строка_подключения_mongodb
ENVIRONMENT=development  # или production
APP_LINK=https://ваш-домен.com/  # только для production
```

## Запуск

### Локальная разработка

```bash
python main.py
```

### Продакшн (с использованием webhook)

Установите переменную `ENVIRONMENT=production` в файле `.env` и запустите:

```bash
python main.py
```

## Команды бота

- `/start` - Начать или перезапустить бота
- `/help` - Получить справку по использованию
- `/reset` - Сбросить историю диалога
- `/model [модель]` - Выбрать модель GPT (доступны gpt4 и gpt3)

## Структура проекта

```
TeleGPT/
├── main.py           # Точка входа
├── bot/
│   ├── __init__.py
│   ├── handlers.py   # Обработчики команд и сообщений
│   ├── storage.py    # Класс для хранения данных пользователей в MongoDB
│   └── config.py     # Конфигурационные параметры
├── services/
│   ├── __init__.py
│   └── openai_service.py  # Сервис для работы с OpenAI API
├── requirements.txt       # Зависимости проекта
├── Procfile               # Конфигурация для деплоя
├── .env.sample            # Шаблон файла .env
└── README.md              # Документация
```

## База данных

Бот использует MongoDB для хранения истории сообщений и настроек пользователей. Структура данных в MongoDB:

- Коллекция `users`:
  - `_id`: Идентификатор пользователя в Telegram
  - `messages`: Массив сообщений пользователя с OpenAI
  - `model`: Выбранная пользователем модель GPT

## Деплой

Для деплоя на Heroku убедитесь, что вы добавили все необходимые переменные окружения в настройках приложения и MongoDB в качестве аддона или внешней базы данных.

## Лицензия

MIT