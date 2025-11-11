# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# analytics.py

import logging
from datetime import datetime
from typing import Dict, Any

class AnalyticsService:
    """Сервис аналитики и метрик"""
    
    def __init__(self, storage):
        self.storage = storage
        self.logger = logging.getLogger(__name__)
        self.events = []

    async def track_command(self, user_id: str, command: str, success: bool = True):
        """Отслеживание использования команд"""
        event = {
            "type": "command",
            "user_id": user_id,
            "command": command,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        self.logger.debug(f"Command tracked: {command} by {user_id}")

    async def track_quiz_question(self, user_id: str, question_id: int, correct: bool, response_time: float):
        """Отслеживание ответов на вопросы викторины"""
        event = {
            "type": "quiz_answer",
            "user_id": user_id,
            "question_id": question_id,
            "correct": correct,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)

    async def track_user_activity(self, user_id: str, activity_type: str, details: Dict[str, Any] = None):
        """Отслеживание активности пользователя"""
        event = {
            "type": "user_activity",
            "user_id": user_id,
            "activity_type": activity_type,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)

    async def get_user_insights(self, user_id: str) -> Dict[str, Any]:
        """Получение аналитических данных по пользователю"""
        stats = self.storage.get_user_stats(user_id)
        settings = self.storage.get_user_settings(user_id)
        qa_list = self.storage.get_user_qa(user_id)
        
        total_answered = stats['total_questions_answered']
        if total_answered > 0:
            correct_rate = (stats['correct_answers'] / total_answered) * 100
            avg_response_time = stats['average_response_time']
        else:
            correct_rate = 0
            avg_response_time = 0
        
        # Анализ сложности вопросов
        question_difficulty = {}
        for qa in qa_list:
            qa_id = qa.get('id')
            if qa_id:
                q_stats = self.storage.get_question_stats(user_id, qa_id)
                times_asked = q_stats.get('times_asked', 0)
                times_correct = q_stats.get('times_correct', 0)
                
                if times_asked > 0:
                    success_rate = (times_correct / times_asked) * 100
                    if success_rate < 30:
                        difficulty = "сложный"
                    elif success_rate < 70:
                        difficulty = "средний"
                    else:
                        difficulty = "легкий"
                    
                    question_difficulty[qa_id] = {
                        "question": qa['question'],
                        "difficulty": difficulty,
                        "success_rate": success_rate,
                        "times_asked": times_asked
                    }
        
        return {
            "user_id": user_id,
            "total_questions": len(qa_list),
            "quiz_active": settings["active"],
            "performance": {
                "total_answered": total_answered,
                "correct_rate": correct_rate,
                "current_streak": stats["current_streak"],
                "best_streak": stats["best_streak"],
                "avg_response_time": avg_response_time
            },
            "daily_progress": {
                "questions_today": settings["questions_today"],
                "daily_goal": settings["daily_goal"],
                "completion_rate": (settings["questions_today"] / settings["daily_goal"]) * 100 if settings["daily_goal"] > 0 else 0
            },
            "question_analysis": question_difficulty,
            "study_habits": {
                "total_study_time": stats["total_study_time_minutes"],
                "last_study_date": stats["last_study_date"]
            }
        }

    async def get_system_metrics(self) -> Dict[str, Any]:
        """Получение системной аналитики"""
        user_ids = self.storage.get_all_user_ids()
        active_users = 0
        total_questions = 0
        total_answers = 0
        
        for user_id in user_ids:
            settings = self.storage.get_user_settings(user_id)
            stats = self.storage.get_user_stats(user_id)
            qa_list = self.storage.get_user_qa(user_id)
            
            if settings["active"]:
                active_users += 1
            
            total_questions += len(qa_list)
            total_answers += stats["total_questions_answered"]
        
        return {
            "total_users": len(user_ids),
            "active_users": active_users,
            "total_questions": total_questions,
            "total_answers": total_answers,
            "recent_events": len([e for e in self.events if self._is_recent(e['timestamp'])]),
            "collection_timestamp": datetime.now().isoformat()
        }

    def _is_recent(self, timestamp: str, hours: int = 24) -> bool:
        """Проверяет, является ли событие недавним"""
        event_time = datetime.fromisoformat(timestamp)
        return (datetime.now() - event_time).total_seconds() <= hours * 3600

    async def cleanup_old_events(self, days: int = 30):
        """Очистка старых событий"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        self.events = [
            event for event in self.events 
            if datetime.fromisoformat(event['timestamp']).timestamp() > cutoff_time
        ]
        self.logger.info(f"Cleaned up events older than {days} days")

    async def export_events(self, file_path: str):
        """Экспорт событий в файл"""
        import json
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Events exported to {file_path}")
        except Exception as e:
            self.logger.error(f"Failed to export events: {e}")