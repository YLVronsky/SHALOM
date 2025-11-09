# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# storage.py

import json
import logging
from pathlib import Path

# Директория для хранения данных пользователей
DATA_DIR = Path("bot_data")
DATA_DIR.mkdir(exist_ok=True)

# Пути к файлам пользователя
def user_qa_file(user_id: str) -> Path:
    """Возвращает путь к файлу с вопросами-ответами пользователя."""
    return DATA_DIR / f"user_{user_id}.json"

def current_question_file(user_id: str) -> Path:
    """Возвращает путь к файлу с текущим вопросом пользователя."""
    return DATA_DIR / f"current_{user_id}.json"

# --- Функции для загрузки/сохранения JSON ---

def load_json_file(file_path: Path):
    """Загружает данные из JSON файла."""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
    return []

def save_json_file(file_path: Path, data):
    """Сохраняет данные в JSON файл."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Error saving {file_path}: {e}")

# --- Работа с вопросами пользователя ---

def save_user_qa(user_id: str, qa_list: list):
    """Сохраняет список вопросов-ответов пользователя."""
    save_json_file(user_qa_file(user_id), qa_list)

def get_user_qa(user_id: str) -> list:
    """Загружает список вопросов-ответов пользователя."""
    return load_json_file(user_qa_file(user_id))

# --- Работа с текущим вопросом ---

def save_current_question(user_id: str, question_data: dict):
    """Сохраняет текущий вопрос для пользователя."""
    save_json_file(current_question_file(user_id), question_data)

def get_current_question(user_id: str) -> dict | None:
    """Загружает текущий вопрос пользователя."""
    data = load_json_file(current_question_file(user_id))
    return data if data else None

def remove_current_question(user_id: str):
    """Удаляет файл с текущим вопросом."""
    file_path = current_question_file(user_id)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:

            logging.error(f"Error deleting {file_path}: {e}")
