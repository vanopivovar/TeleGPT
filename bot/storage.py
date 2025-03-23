from typing import Dict, List, Any, Optional
import os
from pymongo import MongoClient
from bot.config import DEFAULT_MODEL, MAX_HISTORY_LENGTH, SYSTEM_MESSAGES

class UserStorage:
    """Класс для управления данными пользователей в MongoDB."""
    
    def __init__(self):
        """Инициализация подключения к MongoDB."""
        # Получаем строку подключения из переменных окружения
        mongo_uri = os.getenv("MONGODB_URI")
        if not mongo_uri:
            raise ValueError("MONGODB_URI environment variable is not set")
        
        # Создаем подключение к MongoDB
        self.client = MongoClient(mongo_uri)
        self.db = self.client.get_database("telegpt_db")
        self.users_collection = self.db.users
    
    def get_user_data(self, user_id: int) -> Dict[str, Any]:
        """
        Получить данные пользователя, создавая их при необходимости.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с данными пользователя
        """
        # Попытка найти пользователя в базе
        user_data = self.users_collection.find_one({"_id": user_id})
        
        # Если пользователь не найден, создаем новую запись
        if not user_data:
            default_data = {
                "_id": user_id,
                "messages": [],
                "model": DEFAULT_MODEL
            }
            self.users_collection.insert_one(default_data)
            return default_data
        
        return user_data
    
    def get_messages(self, user_id: int) -> List[Dict[str, str]]:
        """
        Получить историю сообщений пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список сообщений пользователя
        """
        return self.get_user_data(user_id).get("messages", [])
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в историю пользователя.
        
        Args:
            user_id: ID пользователя
            role: Роль сообщения ("user", "assistant", "system")
            content: Содержание сообщения
        """
        # Добавляем сообщение в список
        self.users_collection.update_one(
            {"_id": user_id},
            {"$push": {"messages": {"role": role, "content": content}}}
        )
        
        # Получаем текущие сообщения
        messages = self.get_messages(user_id)
        
        # Ограничиваем историю сообщений
        if len(messages) > MAX_HISTORY_LENGTH * 2:  # Умножаем на 2, так как каждый обмен это 2 сообщения
            # Находим системные сообщения
            system_messages = [msg for msg in messages if msg["role"] == "system"]
            # Находим последние обычные сообщения, за исключением системных
            other_messages = [msg for msg in messages if msg["role"] != "system"][-MAX_HISTORY_LENGTH * 2:]
            
            # Обновляем историю сообщений
            self.users_collection.update_one(
                {"_id": user_id},
                {"$set": {"messages": system_messages + other_messages}}
            )
    
    def reset_messages(self, user_id: int) -> None:
        """
        Сбросить историю сообщений пользователя.
        
        Args:
            user_id: ID пользователя
        """
        # Сохраняем только системные сообщения
        model = self.get_model(user_id)
        system_messages = [msg for msg in self.get_messages(user_id) if msg["role"] == "system"]
        
        # Если системных сообщений нет, добавляем одно
        if not system_messages:
            system_messages = [{"role": "system", "content": SYSTEM_MESSAGES.get(model, SYSTEM_MESSAGES["gpt-4o"])}]
        
        # Обновляем историю сообщений
        self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"messages": system_messages}}
        )
    
    def set_model(self, user_id: int, model: str) -> None:
        """
        Установить модель для пользователя.
        
        Args:
            user_id: ID пользователя
            model: Название модели
        """
        self.users_collection.update_one(
            {"_id": user_id},
            {"$set": {"model": model}}
        )
    
    def get_model(self, user_id: int) -> str:
        """
        Получить модель пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Название модели
        """
        return self.get_user_data(user_id).get("model", DEFAULT_MODEL)

# Создаем единый экземпляр хранилища
storage = UserStorage()
