# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# quiz_manager.py

import asyncio
import logging
import random
from datetime import datetime, timedelta
from maxapi import Bot
from storage import (
    get_user_qa, save_current_question, remove_current_question,
    get_user_stats, update_user_stats, get_question_stats,
    get_user_settings, update_user_settings,
    update_question_last_reviewed
)
from config import QUIZ_INTERVAL, EMPTY_QA_INTERVAL

class QuizManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_users = set()
    
    async def smart_quiz_scheduler(self, user_id: str, chat_id: str):
        """Умный планировщик вопросов с адаптивным алгоритмом."""
        if user_id in self.active_users:
            return

        self.active_users.add(user_id)
        logging.info(f"Smart quiz started for user {user_id}")
        
        while user_id in self.active_users:
            settings = get_user_settings(user_id)
            
            # Проверяем лимиты и расписание
            if not self._can_send_question_now(user_id, settings):
                await asyncio.sleep(300)  # Проверяем каждые 5 минут
                continue
            
            # Выбираем интервал на основе алгоритма
            interval = await self._calculate_next_interval(user_id, settings)
            await asyncio.sleep(interval)
            
            if user_id not in self.active_users:
                break
                
            # Проверяем еще раз перед отправкой
            if self._can_send_question_now(user_id, settings):
                await self._send_smart_question(user_id, chat_id)
    
    def _can_send_question_now(self, user_id: str, settings: dict) -> bool:
        """Проверяет, можно ли отправить вопрос сейчас."""
        now = datetime.now()
        
        # Проверяем дневной лимит
        if settings["questions_today"] >= settings["daily_goal"]:
            return False
        
        # Проверяем день недели и время
        weekday = now.strftime("%A").lower()
        day_schedule = settings["schedule"][weekday]
        
        if not day_schedule["enabled"]:
            return False
        
        current_time = now.time()
        start_time = datetime.strptime(day_schedule["start"], "%H:%M").time()
        end_time = datetime.strptime(day_schedule["end"], "%H:%M").time()
        
        return start_time <= current_time <= end_time
    
    async def _calculate_next_interval(self, user_id: str, settings: dict) -> int:
        """Рассчитывает интервал до следующего вопроса на основе алгоритма."""
        base_min = settings["min_interval"] * 60  # в секунды
        base_max = settings["max_interval"] * 60
        
        # Получаем статистику для адаптивного интервала
        stats = get_user_stats(user_id)
        
        if stats["total_questions_answered"] == 0:
            # Первые вопросы - более частые
            return random.randint(base_min // 2, base_max // 2)
        
        # Адаптируем интервал на основе успеваемости
        correct_rate = stats["correct_answers"] / stats["total_questions_answered"]
        
        if correct_rate < 0.5:
            # Низкая успеваемость - уменьшаем интервал
            adjustment = 0.7
        elif correct_rate < 0.8:
            # Средняя успеваемость - стандартный интервал
            adjustment = 1.0
        else:
            # Высокая успеваемость - увеличиваем интервал
            adjustment = 1.3
        
        adjusted_min = int(base_min * adjustment)
        adjusted_max = int(base_max * adjustment)
        
        return random.randint(adjusted_min, adjusted_max)
    
    async def _send_smart_question(self, user_id: str, chat_id: str):
        """Отправляет умно выбранный вопрос и обновляет статистику."""
        qa_list = get_user_qa(user_id)
        if not qa_list:
            await self._handle_empty_questions(user_id, chat_id)
            return
        
        # Выбираем вопрос по алгоритму
        qa = self._select_question_by_algorithm(user_id, qa_list)
        if not qa:
            return
        
        # Обновляем время последнего просмотра вопроса
        question_id = qa.get('id')
        if question_id:
            update_question_last_reviewed(user_id, question_id)
        
        save_current_question(user_id, qa)
        
        try:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=f"❓ **Вопрос:** {qa['question']}"
            )
            
            # Обновляем счетчики
            settings = get_user_settings(user_id)
            settings["questions_today"] += 1
            settings["last_question_date"] = datetime.now().isoformat()
            update_user_settings(user_id, settings)
            
            logging.info(f"Sent smart question to {user_id}: {qa['question']}")
            
        except Exception as e:
            logging.error(f"Error sending question to {user_id}: {e}")
    
    def _select_question_by_algorithm(self, user_id: str, qa_list: list) -> dict:
        """Выбирает вопрос по умному алгоритму на основе статистики."""
        if not qa_list:
            return None
        
        # Если вопросов мало, выбираем случайно
        if len(qa_list) <= 3:
            return random.choice(qa_list)
        
        # Рассчитываем веса для каждого вопроса
        weights = []
        for qa in qa_list:
            weight = self._calculate_question_weight(user_id, qa)
            weights.append(weight)
        
        # Выбираем вопрос с учетом весов
        total_weight = sum(weights)
        if total_weight == 0:
            return random.choice(qa_list)
        
        # Нормализуем веса
        normalized_weights = [w / total_weight for w in weights]
        
        # Взвешенный случайный выбор
        return random.choices(qa_list, weights=normalized_weights, k=1)[0]
    
    def _calculate_question_weight(self, user_id: str, qa: dict) -> float:
        """Рассчитывает вес вопроса для алгоритма выбора."""
        question_id = qa.get('id')
        if not question_id:
            return 1.0  # Вес по умолчанию для вопросов без ID
        
        stats = get_question_stats(user_id, question_id)
        times_asked = stats.get('times_asked', 0)
        times_correct = stats.get('times_correct', 0)
        last_quality = stats.get('last_quality', 0)
        last_reviewed = stats.get('last_reviewed')
        
        # Базовый вес
        weight = 1.0
        
        # Фактор новизны - новые вопросы имеют больший вес
        if times_asked == 0:
            weight *= 3.0  # Новые вопросы в 3 раза вероятнее
        
        # Фактор сложности - вопросы с низкой успеваемостью имеют больший вес
        if times_asked > 0:
            success_rate = times_correct / times_asked
            if success_rate < 0.3:
                weight *= 2.5  # Сложные вопросы
            elif success_rate < 0.7:
                weight *= 1.5  # Средние вопросы
            else:
                weight *= 0.7  # Легкие вопросы
        
        # Фактор времени - давно не задаваемые вопросы имеют больший вес
        if last_reviewed:
            last_review_date = datetime.fromisoformat(last_reviewed)
            days_since_review = (datetime.now() - last_review_date).days
            
            if days_since_review > 30:
                weight *= 3.0
            elif days_since_review > 7:
                weight *= 2.0
            elif days_since_review > 1:
                weight *= 1.5
        
        # Фактор качества последнего ответа
        if last_quality <= 2:
            weight *= 2.0  # Плохой ответ - повторить скорее
        elif last_quality >= 4:
            weight *= 0.6  # Хороший ответ - можно подождать
        
        return max(0.1, weight)  # Минимальный вес чтобы все вопросы имели шанс
    
    async def _handle_empty_questions(self, user_id: str, chat_id: str):
        """Обрабатывает ситуацию, когда у пользователя нет вопросов."""
        try:
            await self.bot.send_message(
                chat_id=chat_id, 
                text=(
                    "📝 **У тебя нет вопросов для викторины!**\n\n"
                    "Добавь вопросы через команду:\n"
                    "`/add_qa Вопрос || Ответ`\n\n"
                    "Например:\n"
                    "`/add_qa Столица Франции || Париж`"
                )
            )
            
            # Делаем паузу перед следующей проверкой
            await asyncio.sleep(EMPTY_QA_INTERVAL)
            
        except Exception as e:
            logging.error(f"Failed to notify user {user_id} about empty questions: {e}")
    
    async def start_quiz_for_user(self, user_id: str, chat_id: str):
        """Запускает цикл викторины для конкретного пользователя (устаревший метод)."""
        logging.warning(f"Using deprecated start_quiz_for_user for {user_id}")
        await self.smart_quiz_scheduler(user_id, chat_id)
    
    def stop_quiz_for_user(self, user_id: str):
        """Останавливает цикл викторины для пользователя."""
        self.active_users.discard(user_id)
        remove_current_question(user_id)
        logging.info(f"Quiz stopped for user {user_id}")
    
    def get_user_quiz_status(self, user_id: str) -> dict:
        """Возвращает статус викторины для пользователя."""
        return {
            "active": user_id in self.active_users,
            "questions_today": get_user_settings(user_id).get("questions_today", 0),
            "daily_goal": get_user_settings(user_id).get("daily_goal", 10),
            "next_possible_question": self._calculate_next_possible_question(user_id)
        }
    
    def _calculate_next_possible_question(self, user_id: str) -> str:
        """Рассчитывает, когда может быть следующий вопрос."""
        if user_id not in self.active_users:
            return "викторина остановлена"
        
        settings = get_user_settings(user_id)
        now = datetime.now()
        
        # Проверяем расписание на сегодня
        weekday = now.strftime("%A").lower()
        day_schedule = settings["schedule"][weekday]
        
        if not day_schedule["enabled"]:
            next_day = self._find_next_available_day(weekday, settings)
            return f"следующий доступный день: {next_day}"
        
        # Проверяем время
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
    
    def _find_next_available_day(self, current_day: str, settings: dict) -> str:
        """Находит следующий доступный день в расписании."""
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
        
        # Ищем следующий доступный день
        for i in range(1, 8):
            next_day_index = (current_index + i) % 7
            next_day = days[next_day_index]
            if settings["schedule"][next_day]["enabled"]:
                return days_ru[next_day]
        
        return "нет доступных дней"