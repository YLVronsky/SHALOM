# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# core/logger.py
import logging
import sys
from datetime import datetime
from pathlib import Path
from core.config import config

def setup_logger():
    """Настройка логгера для всего приложения"""
    
    # Создаем путь к лог-файлу в директории data_dir
    log_dir = Path(config.database.data_dir) / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)  # Создаем директорию и все родительские, если они не существуют
    
    # Генерируем безопасное имя файла для Windows
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = log_dir / f"bot_{timestamp}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Логгер инициализирован. Лог-файл: {log_file}")
    
    return logger

# Создаем глобальный логгер
logger = setup_logger()