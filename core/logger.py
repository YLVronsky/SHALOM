<<<<<<< HEAD
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseniy
=======
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a

import logging
import sys
from datetime import datetime
from pathlib import Path
from core.config import config

def setup_logger():
    """Настройка логгера для всего приложения"""
<<<<<<< HEAD
    
    log_dir = Path(config.database.data_dir) / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)
    
=======

    log_dir = Path(config.database.data_dir) / "logs"
    log_dir.mkdir(exist_ok=True, parents=True)

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
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

logger = setup_logger()