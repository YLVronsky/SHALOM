<<<<<<< HEAD
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseniy
=======
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a

import asyncio
import logging
import random
from datetime import datetime
from typing import Dict, Optional, List
from maxapi import Bot
from core.config import config

class QuizManager:
    """Сервис управления викториной"""
    
    def __init__(self, bot: Bot, storage):
        self.bot = bot
        self.storage = storage
        self.active_users = set()
        self.logger = logging.getLogger(__name__)

    async def smart_quiz_scheduler(self, user_id: str, chat_id: str):
        """Умный планировщик вопросов с адаптивным алгоритмом"""
        if user_id in self.active_users:
            return

        self.active_users.add(user_id)
        self.logger.info(f"Smart quiz started for user {user_id}")
        
        while user_id in self.active_users:
            settings = self.storage.get_user_settings(user_id)
<<<<<<< HEAD
            
            if not self._can_send_question_now(user_id, settings):
                await asyncio.sleep(300)  
                continue
            
=======

            if not self._can_send_question_now(user_id, settings):
                await asyncio.sleep(300)
                continue

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            interval = await self._calculate_next_interval(user_id, settings)
            await asyncio.sleep(interval)
            
            if user_id not in self.active_users:
                break
<<<<<<< HEAD
                
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            if self._can_send_question_now(user_id, settings):
                await self._send_smart_question(user_id, chat_id)
        
        self.logger.warning(f"Запущен smart_quiz_scheduler для {user_id}, task_id={id(asyncio.current_task())}")


    def _can_send_question_now(self, user_id: str, settings: Dict) -> bool:
        """Проверяет, можно ли отправить вопрос сейчас"""
        now = datetime.now()
<<<<<<< HEAD
        
        if settings["questions_today"] >= settings["daily_goal"]:
            return False
        
=======

        if settings["questions_today"] >= settings["daily_goal"]:
            return False

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        weekday = now.strftime("%A").lower()
        day_schedule = settings["schedule"][weekday]
        
        if not day_schedule["enabled"]:
            return False
        
        current_time = now.time()
        start_time = datetime.strptime(day_schedule["start"], "%H:%M").time()
        end_time = datetime.strptime(day_schedule["end"], "%H:%M").time()
        
        return start_time <= current_time <= end_time

    async def _calculate_next_interval(self, user_id: str, settings: Dict) -> int:
        """Рассчитывает интервал до следующего вопроса на основе алгоритма"""
        base_min = settings["min_interval"] * 60
        base_max = settings["max_interval"] * 60
<<<<<<< HEAD
        
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        stats = self.storage.get_user_stats(user_id)
        
        if stats["total_questions_answered"] == 0:
            return random.randint(base_min // 2, base_max // 2)
        
        correct_rate = stats["correct_answers"] / stats["total_questions_answered"]
        
        if correct_rate < 0.5:
            adjustment = 0.7
        elif correct_rate < 0.8:
            adjustment = 1.0
        else:
            adjustment = 1.3
        
        adjusted_min = int(base_min * adjustment)
        adjusted_max = int(base_max * adjustment)
        
        return random.randint(adjusted_min, adjusted_max)

    async def _send_smart_question(self, user_id: str, chat_id: str):
        """Отправляет умно выбранный вопрос и обновляет статистику"""
        qa_list = self.storage.get_user_qa(user_id)
        if not qa_list:
            await self._handle_empty_questions(user_id, chat_id)
            return
        
        qa = self._select_question_by_algorithm(user_id, qa_list)
        if not qa:
            return
        
        question_id = qa.get('id')
        if question_id:
            self.storage.update_question_last_reviewed(user_id, question_id)
        
        self.storage.save_current_question(user_id, qa)
        
        try:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=f"❓ Вопрос: {qa['question']}"
            )
            
            settings = self.storage.get_user_settings(user_id)
            new_questions_today = settings.get("questions_today", 0) + 1

            self.storage.update_user_settings(
                user_id,
                questions_today=new_questions_today,
                last_question_date=datetime.now().isoformat()
            )

            stats = self.storage.get_user_stats(user_id)
            last_time = stats.get("last_study_date")
            if last_time:
                delta = (datetime.now() - datetime.fromisoformat(last_time)).total_seconds() / 60
            else:
                delta = 0
                
            stats["total_study_time_minutes"] = stats.get("total_study_time_minutes", 0) + int(delta)
            stats["last_study_date"] = datetime.now().isoformat()

            self.storage.save_user_stats(user_id, stats)
            
            self.logger.info(f"Sent smart question to {user_id}: {qa['question']}")
            
        except Exception as e:
            self.logger.error(f"Error sending question to {user_id}: {e}")

        

    def _select_question_by_algorithm(self, user_id: str, qa_list: List[Dict]) -> Optional[Dict]:
        """Выбирает вопрос по умному алгоритму на основе статистики"""
        if not qa_list:
            return None
        
        if len(qa_list) <= 3:
            return random.choice(qa_list)
        
        weights = []
        for qa in qa_list:
            weight = self._calculate_question_weight(user_id, qa)
            weights.append(weight)
<<<<<<< HEAD

        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(qa_list)
        
        normalized_weights = [w / total_weight for w in weights]
        
=======
        
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(qa_list)

        normalized_weights = [w / total_weight for w in weights]

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        return random.choices(qa_list, weights=normalized_weights, k=1)[0]

    def _calculate_question_weight(self, user_id: str, qa: Dict) -> float:
        """Рассчитывает вес вопроса для алгоритма выбора"""
        question_id = qa.get('id')
        if not question_id:
<<<<<<< HEAD
            return 1.0  
=======
            return 1.0
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        
        stats = self.storage.get_question_stats(user_id, question_id)
        times_asked = stats.get('times_asked', 0)
        times_correct = stats.get('times_correct', 0)
        last_quality = stats.get('last_quality', 0)
        last_reviewed = stats.get('last_reviewed')
<<<<<<< HEAD
        
        weight = 1.0
        
        if times_asked == 0:
            weight *= 3.0  
        
        if times_asked > 0:
            success_rate = times_correct / times_asked
            if success_rate < 0.3:
                weight *= 2.5  
            elif success_rate < 0.7:
                weight *= 1.5  
            else:
                weight *= 0.7  
        
=======

        weight = 1.0

        if times_asked == 0:
            weight *= 3.0

        if times_asked > 0:
            success_rate = times_correct / times_asked
            if success_rate < 0.3:
                weight *= 2.5
            elif success_rate < 0.7:
                weight *= 1.5
            else:
                weight *= 0.7

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        if last_reviewed:
            last_review_date = datetime.fromisoformat(last_reviewed)
            days_since_review = (datetime.now() - last_review_date).days
            
            if days_since_review > 30:
                weight *= 3.0
            elif days_since_review > 7:
                weight *= 2.0
            elif days_since_review > 1:
                weight *= 1.5
<<<<<<< HEAD
        
        if last_quality <= 2:
            weight *= 2.0  
        elif last_quality >= 4:
            weight *= 0.6 
=======

        if last_quality <= 2:
            weight *= 2.0
        elif last_quality >= 4:
            weight *= 0.6
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        
        return max(0.1, weight)

    async def _handle_empty_questions(self, user_id: str, chat_id: str):
        """Обрабатывает ситуацию, когда у пользователя нет вопросов"""
        try:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=(
<<<<<<< HEAD
                    "📝 У тебя нет вопросов для викторины!\n\n"
=======
                    "У тебя нет вопросов для викторины!\n\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
                    "Добавь вопросы через команду:\n"
                    "`/add_qa Вопрос || Ответ`\n\n"
                    "Например:\n"
                    "`/add_qa Столица Франции || Париж`"
                )
            )
            
            await asyncio.sleep(config.quiz.empty_qa_interval)
            
        except Exception as e:
            self.logger.error(f"Failed to notify user {user_id} about empty questions: {e}")

    def stop_quiz_for_user(self, user_id: str):
        """Останавливает цикл викторины для пользователя"""
        self.active_users.discard(user_id)
        self.storage.remove_current_question(user_id)
        self.logger.info(f"Quiz stopped for user {user_id}")

    def get_user_quiz_status(self, user_id: str) -> Dict[str, any]:
        """Возвращает статус викторины для пользователя"""
        settings = self.storage.get_user_settings(user_id)
        return {
            "active": user_id in self.active_users,
            "questions_today": settings.get("questions_today", 0),
            "daily_goal": settings.get("daily_goal", 10),
            "next_possible_question": self._calculate_next_possible_question(user_id)
        }

    def _calculate_next_possible_question(self, user_id: str) -> str:
        """Рассчитывает, когда может быть следующий вопрос"""
        if user_id not in self.active_users:
            return "викторина остановлена"
        
        settings = self.storage.get_user_settings(user_id)
        now = datetime.now()
        
        weekday = now.strftime("%A").lower()
        day_schedule = settings["schedule"][weekday]
        
        if not day_schedule["enabled"]:
            next_day = self._find_next_available_day(weekday, settings)
            return f"следующий доступный день: {next_day}"
<<<<<<< HEAD
        
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        current_time = now.time()
        start_time = datetime.strptime(day_schedule["start"], "%H:%M").time()
        end_time = datetime.strptime(day_schedule["end"], "%H:%M").time()
        
        if current_time < start_time:
            return f"сегодня в {start_time}"
        elif current_time > end_time:
            next_day = self._find_next_available_day(weekday, settings)
            return f"следующий доступный день: {next_day}"
        else:
            return "в течение интервала"

    def _find_next_available_day(self, current_day: str, settings: Dict) -> str:
        """Находит следующий доступный день в расписании"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        days_ru = {
            "monday": "понедельник",
            "tuesday": "вторник", 
            "wednesday": "среда",
            "thursday": "четверг",
            "friday": "пятница",
            "saturday": "суббота",
            "sunday": "воскресенье"
        }
        
        current_index = days.index(current_day)
<<<<<<< HEAD
        
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        for i in range(1, 8):
            next_day_index = (current_index + i) % 7
            next_day = days[next_day_index]
            if settings["schedule"][next_day]["enabled"]:
                return days_ru[next_day]
        
        return "нет доступных дней"