# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# config.py

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

@dataclass
class DatabaseConfig:
    """Конфигурация хранилища данных"""
    data_dir: Path = Path(os.getenv('DATA_DIR', 'bot_data'))

@dataclass
class QuizConfig:
    """Конфигурация викторины"""
    empty_qa_interval: int = int(os.getenv('EMPTY_QA_INTERVAL', '60'))  # секунды при отсутствии вопросов

@dataclass
class BotConfig:
    """Конфигурация бота"""
    token: str = os.getenv('BOT_TOKEN', '')
    version: str = os.getenv('BOT_VERSION', '0.4.0')

class Config:
    """
    Главный класс конфигурации приложения.
    Сохраняет обратную совместимость с существующим кодом.
    """
    
    def __init__(self):
        # Проверяем обязательные переменные
        self._validate_required_env_vars()
        
        # Инициализируем конфигурации
        self.bot = BotConfig()
        self.database = DatabaseConfig()
        self.quiz = QuizConfig()

    def _validate_required_env_vars(self):
        """Проверка обязательных переменных окружения"""
        required_vars = ['BOT_TOKEN']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}\n"
                "Please create .env file with the following variables:\n"
                "BOT_TOKEN=your_bot_token_here\n"
                "DATA_DIR=bot_data (optional)\n"
                "EMPTY_QA_INTERVAL=60 (optional)\n"
                "BOT_VERSION=0.4.0 (optional)"
            )

    def get_default_schedule(self) -> dict:
        """Возвращает расписание по умолчанию (для storage.py)"""
        return {
            "monday": {"start": "09:00", "end": "21:00", "enabled": True},
            "tuesday": {"start": "09:00", "end": "21:00", "enabled": True},
            "wednesday": {"start": "09:00", "end": "21:00", "enabled": True},
            "thursday": {"start": "09:00", "end": "21:00", "enabled": True},
            "friday": {"start": "09:00", "end": "21:00", "enabled": True},
            "saturday": {"start": "10:00", "end": "18:00", "enabled": True},
            "sunday": {"start": "10:00", "end": "18:00", "enabled": True}
        }


# Создаем экземпляр конфигурации
config = Config()

# Сохраняем обратную совместимость с существующим кодом
BOT_TOKEN = config.bot.token
DATA_DIR = config.database.data_dir
EMPTY_QA_INTERVAL = config.quiz.empty_qa_interval
VERSION_BOT = config.bot.version


# Для обратной совместимости с USER_SETTINGS из старого config.py
USER_SETTINGS = {
    "max_questions_per_day": 20,
    "min_interval_minutes": 30,
    "max_interval_minutes": 120,
    "working_hours_start": "09:00",
    "working_hours_end": "21:00"
}