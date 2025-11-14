<<<<<<< HEAD
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseniy
=======
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a

import json
import logging
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Optional, Any
from core.config import config

class Storage:
    """Сервис для работы с хранилищем данных"""
    
    def __init__(self):
        self.data_dir = config.database.data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)

    
    def _user_qa_file(self, user_id: str) -> Path:
        data_dir = self.data_dir / f"user_{user_id}"
        return data_dir / f"user_{user_id}.json"

    def _current_question_file(self, user_id: str) -> Path:
        data_dir = self.data_dir / f"user_{user_id}"
        return data_dir / f"current_{user_id}.json"

    def _user_settings_file(self, user_id: str) -> Path:
        data_dir = self.data_dir / f"user_{user_id}"
        return data_dir / f"user_settings_{user_id}.json"

    def _user_stats_file(self, user_id: str) -> Path:
        data_dir = self.data_dir / f"user_{user_id}"
        return data_dir / f"user_stats_{user_id}.json"

    def _load_json_file(self, file_path: Path) -> Any:
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading {file_path}: {e}")
        return None

    def _save_json_file(self, file_path: Path, data: Any) -> bool:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving {file_path}: {e}")
            return False

    
    def get_default_settings(self) -> Dict[str, Any]:
        return {
            "active": False,
            "daily_goal": 10,
            "min_interval": 30,
            "max_interval": 120,
            "schedule": config.get_default_schedule(),
            "questions_today": 0,
            "last_question_date": None,
            "last_reset_date": date.today().isoformat()
        }

    def get_user_settings(self, user_id: str) -> Dict[str, Any]:
        settings = self._load_json_file(self._user_settings_file(user_id))
        if not settings:
            return self.get_default_settings()
<<<<<<< HEAD
        
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        if settings.get('last_reset_date') != date.today().isoformat():
            settings['questions_today'] = 0
            settings['last_reset_date'] = date.today().isoformat()
            self.save_user_settings(user_id, settings)
        
        return settings

    def save_user_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        return self._save_json_file(self._user_settings_file(user_id), settings)

    def update_user_settings(self, user_id: str, **kwargs) -> bool:
        settings = self.get_user_settings(user_id)
        settings.update(kwargs)
        return self.save_user_settings(user_id, settings)

    
    def save_user_qa(self, user_id: str, qa_list: List[Dict]) -> bool:
        return self._save_json_file(self._user_qa_file(user_id), qa_list)

    def get_user_qa(self, user_id: str) -> List[Dict]:
        data = self._load_json_file(self._user_qa_file(user_id))
        return data if data else []

    def add_user_qa(self, user_id: str, question: str, answer: str) -> bool:
        qa_list = self.get_user_qa(user_id)
        qa_list.append({
            "question": question,
            "answer": answer,
            "created_date": datetime.now().isoformat(),
            "id": len(qa_list) + 1
        })
        return self.save_user_qa(user_id, qa_list)

    def remove_user_qa(self, user_id: str, qa_id: int) -> bool:
        qa_list = self.get_user_qa(user_id)
        qa_list = [qa for qa in qa_list if qa.get('id') != qa_id]
        return self.save_user_qa(user_id, qa_list)

    
    def save_current_question(self, user_id: str, question_data: Dict[str, Any]) -> bool:
        question_data['asked_at'] = datetime.now().isoformat()
        return self._save_json_file(self._current_question_file(user_id), question_data)

    def get_current_question(self, user_id: str) -> Optional[Dict[str, Any]]:
        data = self._load_json_file(self._current_question_file(user_id))
        return data if data else None

    def remove_current_question(self, user_id: str) -> bool:
        file_path = self._current_question_file(user_id)
        if file_path.exists():
            try:
                file_path.unlink()
                return True
            except Exception as e:
                self.logger.error(f"Error deleting {file_path}: {e}")
        return False

    
    def get_default_stats(self) -> Dict[str, Any]:
        return {
            "total_questions_answered": 0,
            "correct_answers": 0,
            "incorrect_answers": 0,
            "current_streak": 0,
            "best_streak": 0,
            "average_response_time": 0,
            "total_study_time_minutes": 0,
            "last_study_date": None,
            "question_stats": {}
        }

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        stats = self._load_json_file(self._user_stats_file(user_id))
        return stats if stats else self.get_default_stats()

    def save_user_stats(self, user_id: str, stats: Dict[str, Any]) -> bool:
        return self._save_json_file(self._user_stats_file(user_id), stats)

    def update_user_stats(self, user_id: str, question_id: int = None, correct: bool = None, 
                         response_time: float = None, quality: int = None) -> bool:
        stats = self.get_user_stats(user_id)
<<<<<<< HEAD
        
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        stats["total_questions_answered"] += 1
        if correct:
            stats["correct_answers"] += 1
            stats["current_streak"] += 1
            stats["best_streak"] = max(stats["best_streak"], stats["current_streak"])
        else:
            stats["incorrect_answers"] += 1
            stats["current_streak"] = 0
<<<<<<< HEAD
        
        if response_time is not None:
            total_time = stats["average_response_time"] * (stats["total_questions_answered"] - 1)
            stats["average_response_time"] = (total_time + response_time) / stats["total_questions_answered"]
        
=======

        if response_time is not None:
            total_time = stats["average_response_time"] * (stats["total_questions_answered"] - 1)
            stats["average_response_time"] = (total_time + response_time) / stats["total_questions_answered"]

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
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
        
        return self.save_user_stats(user_id, stats)

    def update_question_last_reviewed(self, user_id: str, question_id: int) -> bool:
        stats = self.get_user_stats(user_id)
        
        if str(question_id) not in stats["question_stats"]:
            stats["question_stats"][str(question_id)] = {
                "times_asked": 0,
                "times_correct": 0,
                "total_response_time": 0,
                "last_quality": 0,
                "last_reviewed": None
            }
        
        stats["question_stats"][str(question_id)]["last_reviewed"] = datetime.now().isoformat()
        return self.save_user_stats(user_id, stats)

    def get_question_stats(self, user_id: str, question_id: int) -> Dict[str, Any]:
        stats = self.get_user_stats(user_id)
        return stats["question_stats"].get(str(question_id), {
            "times_asked": 0,
            "times_correct": 0,
            "total_response_time": 0,
            "last_quality": 0,
            "last_reviewed": None
        })

    
    def reset_daily_counters(self) -> int:
        reset_count = 0
        today = date.today().isoformat()
        
        for settings_file in self.data_dir.glob("user_settings_*.json"):
            try:
                user_id = settings_file.stem.replace("user_settings_", "")
                settings = self._load_json_file(settings_file)
                if settings and settings.get('last_reset_date') != today:
                    settings['questions_today'] = 0
                    settings['last_reset_date'] = today
                    if self._save_json_file(settings_file, settings):
                        reset_count += 1
            except Exception as e:
                self.logger.error(f"Error resetting counters for {settings_file}: {e}")
        
        self.logger.info(f"Reset daily counters for {reset_count} users")
        return reset_count

    def get_all_user_ids(self) -> List[str]:
        user_ids = set()
        
        for qa_file in self.data_dir.glob("user_*.json"):
            user_id = qa_file.stem.replace("user_", "")
            if user_id and not user_id.startswith("settings_") and not user_id.startswith("stats_"):
                user_ids.add(user_id)
        
        for settings_file in self.data_dir.glob("user_settings_*.json"):
            user_id = settings_file.stem.replace("user_settings_", "")
            if user_id:
                user_ids.add(user_id)
        
        return list(user_ids)