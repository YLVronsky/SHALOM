# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# storage.py

import json
import logging
from pathlib import Path
from datetime import datetime, date
import os

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

def user_settings_file(user_id: str) -> Path:
    """Возвращает путь к файлу с настройками пользователя."""
    return DATA_DIR / f"user_settings_{user_id}.json"

def user_stats_file(user_id: str) -> Path:
    """Возвращает путь к файлу со статистикой пользователя."""
    return DATA_DIR / f"user_stats_{user_id}.json"

# --- Функции для загрузки/сохранения JSON ---

def load_json_file(file_path: Path):
    """Загружает данные из JSON файла."""
    try:
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.error(f"Error loading {file_path}: {e}")
    return None

def save_json_file(file_path: Path, data):
    """Сохраняет данные в JSON файл."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving {file_path}: {e}")
        return False

# --- Работа с вопросами пользователя ---

def save_user_qa(user_id: str, qa_list: list):
    """Сохраняет список вопросов-ответов пользователя."""
    return save_json_file(user_qa_file(user_id), qa_list)

def get_user_qa(user_id: str) -> list:
    """Загружает список вопросов-ответов пользователя."""
    data = load_json_file(user_qa_file(user_id))
    return data if data else []

def add_user_qa(user_id: str, question: str, answer: str) -> bool:
    """Добавляет один вопрос-ответ пользователю."""
    qa_list = get_user_qa(user_id)
    qa_list.append({
        "question": question,
        "answer": answer,
        "created_date": datetime.now().isoformat(),
        "id": len(qa_list) + 1
    })
    return save_user_qa(user_id, qa_list)

def remove_user_qa(user_id: str, qa_id: int) -> bool:
    """Удаляет вопрос-ответ по ID."""
    qa_list = get_user_qa(user_id)
    qa_list = [qa for qa in qa_list if qa.get('id') != qa_id]
    return save_user_qa(user_id, qa_list)

# --- Работа с текущим вопросом ---

def save_current_question(user_id: str, question_data: dict):
    """Сохраняет текущий вопрос для пользователя."""
    question_data['asked_at'] = datetime.now().isoformat()
    return save_json_file(current_question_file(user_id), question_data)

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
            return True
        except Exception as e:
            logging.error(f"Error deleting {file_path}: {e}")
    return False

# --- Работа с настройками пользователя ---

def get_default_settings() -> dict:
    """Возвращает настройки по умолчанию."""
    return {
        "active": False,
        "daily_goal": 10,
        "min_interval": 30,  # минут
        "max_interval": 120, # минут
        "schedule": {
            "monday": {"start": "09:00", "end": "21:00", "enabled": True},
            "tuesday": {"start": "09:00", "end": "21:00", "enabled": True},
            "wednesday": {"start": "09:00", "end": "21:00", "enabled": True},
            "thursday": {"start": "09:00", "end": "21:00", "enabled": True},
            "friday": {"start": "09:00", "end": "21:00", "enabled": True},
            "saturday": {"start": "10:00", "end": "18:00", "enabled": True},
            "sunday": {"start": "10:00", "end": "18:00", "enabled": True}
        },
        "questions_today": 0,
        "last_question_date": None,
        "last_reset_date": date.today().isoformat()
    }

def get_user_settings(user_id: str) -> dict:
    """Загружает настройки пользователя."""
    settings = load_json_file(user_settings_file(user_id))
    if not settings:
        return get_default_settings()
    
    # Проверяем, нужно ли сбросить дневной счетчик
    if settings.get('last_reset_date') != date.today().isoformat():
        settings['questions_today'] = 0
        settings['last_reset_date'] = date.today().isoformat()
        save_user_settings(user_id, settings)
    
    return settings

def save_user_settings(user_id: str, settings: dict) -> bool:
    """Сохраняет настройки пользователя."""
    return save_json_file(user_settings_file(user_id), settings)

def update_user_settings(user_id: str, **kwargs) -> bool:
    """Обновляет определенные настройки пользователя."""
    settings = get_user_settings(user_id)
    settings.update(kwargs)
    return save_user_settings(user_id, settings)

def reset_daily_counters() -> int:
    """Сбрасывает дневные счетчики для всех пользователей. Возвращает количество обновленных пользователей."""
    reset_count = 0
    today = date.today().isoformat()
    
    for settings_file in DATA_DIR.glob("user_settings_*.json"):
        try:
            user_id = settings_file.stem.replace("user_settings_", "")
            settings = load_json_file(settings_file)
            if settings and settings.get('last_reset_date') != today:
                settings['questions_today'] = 0
                settings['last_reset_date'] = today
                if save_json_file(settings_file, settings):
                    reset_count += 1
        except Exception as e:
            logging.error(f"Error resetting counters for {settings_file}: {e}")
    
    logging.info(f"Reset daily counters for {reset_count} users")
    return reset_count

# --- Работа со статистикой пользователя ---

def get_default_stats() -> dict:
    """Возвращает статистику по умолчанию."""
    return {
        "total_questions_answered": 0,
        "correct_answers": 0,
        "incorrect_answers": 0,
        "current_streak": 0,
        "best_streak": 0,
        "average_response_time": 0,
        "total_study_time_minutes": 0,
        "last_study_date": None,
        "question_stats": {}  # Статистика по отдельным вопросам
    }

def get_user_stats(user_id: str) -> dict:
    """Загружает статистику пользователя."""
    stats = load_json_file(user_stats_file(user_id))
    return stats if stats else get_default_stats()

def save_user_stats(user_id: str, stats: dict) -> bool:
    """Сохраняет статистику пользователя."""
    return save_json_file(user_stats_file(user_id), stats)

def update_user_stats(user_id: str, question_id: int = None, correct: bool = None, 
                     response_time: float = None, quality: int = None) -> bool:
    """Обновляет статистику пользователя после ответа на вопрос."""
    stats = get_user_stats(user_id)
    
    # Основная статистика
    stats["total_questions_answered"] += 1
    if correct:
        stats["correct_answers"] += 1
        stats["current_streak"] += 1
        stats["best_streak"] = max(stats["best_streak"], stats["current_streak"])
    else:
        stats["incorrect_answers"] += 1
        stats["current_streak"] = 0
    
    # Обновляем среднее время ответа
    if response_time is not None:
        total_time = stats["average_response_time"] * (stats["total_questions_answered"] - 1)
        stats["average_response_time"] = (total_time + response_time) / stats["total_questions_answered"]
    
    # Статистика по конкретному вопросу
    if question_id is not None:
        if str(question_id) not in stats["question_stats"]:
            stats["question_stats"][str(question_id)] = {
                "times_asked": 0,
                "times_correct": 0,
                "total_response_time": 0,
                "last_quality": 0,
                "last_reviewed": None
            }
        
        q_stats = stats["question_stats"][str(question_id)]
        q_stats["times_asked"] += 1
        q_stats["last_reviewed"] = datetime.now().isoformat()
        
        if correct:
            q_stats["times_correct"] += 1
        
        if response_time is not None:
            q_stats["total_response_time"] += response_time
        
        if quality is not None:
            q_stats["last_quality"] = quality
    
    stats["last_study_date"] = datetime.now().isoformat()
    
    return save_user_stats(user_id, stats)

def update_question_last_reviewed(user_id: str, question_id: int) -> bool:
    """Обновляет только время последнего просмотра вопроса (без увеличения счетчиков)."""
    stats = get_user_stats(user_id)
    
    if str(question_id) not in stats["question_stats"]:
        stats["question_stats"][str(question_id)] = {
            "times_asked": 0,
            "times_correct": 0,
            "total_response_time": 0,
            "last_quality": 0,
            "last_reviewed": None
        }
    
    stats["question_stats"][str(question_id)]["last_reviewed"] = datetime.now().isoformat()
    return save_user_stats(user_id, stats)

def get_question_stats(user_id: str, question_id: int) -> dict:
    """Возвращает статистику по конкретному вопросу."""
    stats = get_user_stats(user_id)
    return stats["question_stats"].get(str(question_id), {
        "times_asked": 0,
        "times_correct": 0,
        "total_response_time": 0,
        "last_quality": 0,
        "last_reviewed": None
    })

# --- Вспомогательные функции ---

def get_all_user_ids() -> list:
    """Возвращает список всех user_id, у которых есть данные."""
    user_ids = set()
    
    # Из файлов с вопросами
    for qa_file in DATA_DIR.glob("user_*.json"):
        user_id = qa_file.stem.replace("user_", "")
        if user_id and not user_id.startswith("settings_") and not user_id.startswith("stats_"):
            user_ids.add(user_id)
    
    # Из файлов с настройками
    for settings_file in DATA_DIR.glob("user_settings_*.json"):
        user_id = settings_file.stem.replace("user_settings_", "")
        if user_id:
            user_ids.add(user_id)
    
    return list(user_ids)

def cleanup_orphaned_files() -> int:
    """Удаляет файлы, для которых нет соответствующего пользователя. Возвращает количество удаленных файлов."""
    user_ids = get_all_user_ids()
    deleted_count = 0
    
    # Проверяем все файлы в DATA_DIR
    for file_path in DATA_DIR.iterdir():
        if file_path.is_file():
            # Извлекаем user_id из имени файла
            stem = file_path.stem
            if stem.startswith("user_") and not stem.startswith("user_settings_") and not stem.startswith("user_stats_"):
                file_user_id = stem.replace("user_", "")
            elif stem.startswith("user_settings_"):
                file_user_id = stem.replace("user_settings_", "")
            elif stem.startswith("user_stats_"):
                file_user_id = stem.replace("user_stats_", "")
            elif stem.startswith("current_"):
                file_user_id = stem.replace("current_", "")
            else:
                continue
            
            # Если user_id нет в списке активных пользователей, удаляем файл
            if file_user_id not in user_ids:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    logging.info(f"Deleted orphaned file: {file_path}")
                except Exception as e:
                    logging.error(f"Error deleting orphaned file {file_path}: {e}")
    
    return deleted_count

def get_user_data_size(user_id: str) -> dict:
    """Возвращает информацию о размере данных пользователя."""
    files = {
        "qa": user_qa_file(user_id),
        "settings": user_settings_file(user_id),
        "stats": user_stats_file(user_id),
        "current": current_question_file(user_id)
    }
    
    sizes = {}
    total_size = 0
    
    for key, file_path in files.items():
        if file_path.exists():
            size = file_path.stat().st_size
            sizes[key] = size
            total_size += size
        else:
            sizes[key] = 0
    
    sizes["total"] = total_size
    return sizes

# --- Миграции данных (для будущих обновлений) ---

def migrate_user_data(user_id: str) -> bool:
    """Мигрирует данные пользователя к последней версии формата."""
    try:
        # Миграция настроек
        settings = get_user_settings(user_id)
        default_settings = get_default_settings()
        
        # Добавляем отсутствующие поля
        for key, value in default_settings.items():
            if key not in settings:
                settings[key] = value
        
        save_user_settings(user_id, settings)
        
        # Миграция статистики
        stats = get_user_stats(user_id)
        default_stats = get_default_stats()
        
        for key, value in default_stats.items():
            if key not in stats:
                stats[key] = value
        
        save_user_stats(user_id, stats)
        
        # Миграция вопросов (добавляем ID, если нет)
        qa_list = get_user_qa(user_id)
        for i, qa in enumerate(qa_list):
            if 'id' not in qa:
                qa['id'] = i + 1
            if 'created_date' not in qa:
                qa['created_date'] = datetime.now().isoformat()
        
        save_user_qa(user_id, qa_list)
        
        logging.info(f"Successfully migrated data for user {user_id}")
        return True
        
    except Exception as e:
        logging.error(f"Error migrating data for user {user_id}: {e}")
        return False