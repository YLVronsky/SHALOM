# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# config.py

import os
from pathlib import Path

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', 'f9LHodD0cOI9Fh9VVdQ8Jut17WGOoPHZOltK3AEJBmM6ZHcCdN1aqsf1Ab2GAXyvpFYA2wyuA_33yrVCicKp')

# Настройки викторины
QUIZ_INTERVAL = 300  # 5 минут в секундах
EMPTY_QA_INTERVAL = 60  # Пауза при отсутствии вопросов (секунды)

# Настройки файлового хранилища
DATA_DIR = Path("bot_data")

# Заглушка 
USER_SETTINGS = {
    "max_questions_per_day": 20,
    "min_interval_minutes": 30,
    "max_interval_minutes": 120,
    "working_hours_start": "09:00",
    "working_hours_end": "21:00"
}

VERSION_BOT = "0.4.0"
