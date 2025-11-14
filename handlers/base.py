<<<<<<< HEAD
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseniy
=======
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a

import logging
from typing import List, Dict, Any
from utils.keyboards import KeyboardManager
from utils.validators import Validators

class BaseHandler:
    """Базовый класс для всех обработчиков"""
    
    def __init__(self, quiz_manager, storage):
        self.quiz_manager = quiz_manager
        self.storage = storage
        self.keyboard_manager = KeyboardManager
        self.validators = Validators
        self.logger = logging.getLogger(self.__class__.__name__)

class MessageFormatter:
    """Форматирование сообщений с использованием валидаторов"""
    
    @staticmethod
    def format_qa_list(qa_list: List[Dict]) -> str:
        """Форматирует список вопросов-ответов"""
        if not qa_list:
<<<<<<< HEAD
            return "📝 У тебя пока нет вопросов.\n\nДобавь первый вопрос:\n`/add_qa Вопрос || Ответ`"

        text = f"📚 Твои вопросы ({len(qa_list)}):\n\n"
=======
            return "У тебя пока нет вопросов.\n\nДобавь первый вопрос:\n`/add_qa Вопрос || Ответ`"

        text = f"Твои вопросы ({len(qa_list)}):\n\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        
        for i, qa in enumerate(qa_list, 1):
            question_text = Validators.sanitize_text(qa['question'], 100)
            answer_text = Validators.sanitize_text(qa['answer'], 50)
            qa_id = qa.get('id', i)
            
<<<<<<< HEAD
            qa_entry = f"{i}. ❓ {question_text}\n    Ответ: {answer_text}\n   ID: {qa_id}\n\n"
=======
            qa_entry = f"{i}. {question_text}\n   Ответ: {answer_text}\n   ID: {qa_id}\n\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            
            if len(text) + len(qa_entry) > 3500:
                break
            
            text += qa_entry

<<<<<<< HEAD
        text += "\n Управление вопросами:\n"
=======
        text += "\nУправление вопросами:\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        text += "• `/remove_qa <ID>` - удалить вопрос\n"
        text += "• `/clear_qa` - очистить все вопросы"
        
        return text

    @staticmethod
    def format_schedule(settings: Dict[str, Any]) -> str:
        """Форматирует информацию о расписании с валидацией"""
        days_ru = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник', 
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница',
            'saturday': 'Суббота',
            'sunday': 'Воскресенье'
        }
        
        schedule_info = []
        for day, schedule in settings["schedule"].items():
<<<<<<< HEAD
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            start_time = schedule["start"]
            end_time = schedule["end"]
            
            if not Validators.validate_time_format(start_time) or not Validators.validate_time_format(end_time):
                status = "❌"
                time_display = "некорректное время"
            else:
                status = "✅" if schedule["enabled"] else "❌"
                time_display = f"{start_time} - {end_time}"
            
            schedule_info.append(f"{status} {days_ru[day]}: {time_display}")
        
        return "\n".join(schedule_info) if schedule_info else "❌ Расписание не настроено"

    @staticmethod
    def format_quiz_start_message(settings: Dict[str, Any], qa_count: int) -> str:
        """Форматирует сообщение о запуске викторины"""
<<<<<<< HEAD
        daily_goal = settings['daily_goal']
        min_interval = settings['min_interval']
        max_interval = settings['max_interval']
        
=======

        daily_goal = settings['daily_goal']
        min_interval = settings['min_interval']
        max_interval = settings['max_interval']

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        interval_valid, interval_error, _ = Validators.validate_interval(min_interval, max_interval)
        if not interval_valid:
            interval_display = "❌ некорректный интервал"
        else:
            interval_display = f"{min_interval} - {max_interval} минут"

        schedule_text = ""
        enabled_days = [day for day, schedule in settings["schedule"].items() if schedule["enabled"]]
        if enabled_days:
            days_ru = {
                'monday': 'Пн', 'tuesday': 'Вт', 'wednesday': 'Ср',
                'thursday': 'Чт', 'friday': 'Пт', 'saturday': 'Сб', 'sunday': 'Вс'
            }
            schedule_days = [days_ru[day] for day in enabled_days]
            schedule_text = f"• Дни: {', '.join(schedule_days)}\n"
<<<<<<< HEAD
            
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            sample_day = enabled_days[0]
            start_time = settings['schedule'][sample_day]['start']
            end_time = settings['schedule'][sample_day]['end']
            
            if Validators.validate_time_format(start_time) and Validators.validate_time_format(end_time):
                schedule_text += f"• Время: {start_time} - {end_time}\n"
        
        return (
<<<<<<< HEAD
            " Умная викторина запущена!\n\n"
            f"📊 Настройки:\n"
=======
            "Умная викторина запущена!\n\n"
            f"Настройки:\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            f"• Дневная цель: {daily_goal} вопросов\n"
            f"• Интервал: {interval_display}\n"
            f"{schedule_text}"
            f"• Доступно вопросов: {qa_count}\n\n"
<<<<<<< HEAD
            "⏰ Вопросы будут приходить в случайное время в указанном интервале.\n"
            "📈 Алгоритм адаптируется под твои результаты!\n\n"
=======
            "Вопросы будут приходить в случайное время в указанном интервале.\n"
            "Алгоритм адаптируется под твои результаты!\n\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            "Управление:\n"
            "• `/stop_quiz` - остановить викторину\n"
            "• `/settings` - изменить настройки\n"
            "• `/stats` - посмотреть статистику"
        )

    @staticmethod
    def format_settings_message(settings: Dict[str, Any], stats: Dict[str, Any], qa_count: int) -> str:
        """Форматирует сообщение с настройками"""
        schedule_text = MessageFormatter.format_schedule(settings)
<<<<<<< HEAD
        
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        daily_goal = settings['daily_goal']
        goal_valid, goal_error, _ = Validators.validate_daily_goal(daily_goal)
        goal_display = f"{daily_goal}" if goal_valid else f"❌ {daily_goal} (некорректно)"
        
        min_interval = settings['min_interval']
        max_interval = settings['max_interval']
        interval_valid, interval_error, _ = Validators.validate_interval(min_interval, max_interval)
        interval_display = f"{min_interval} - {max_interval}" if interval_valid else f"❌ {min_interval}-{max_interval} (некорректно)"
        
        return (
<<<<<<< HEAD
            "⚙️ Твои настройки:\n\n"
            f"📊 Основные:\n"
=======
            "Твои настройки:\n\n"
            f"Основные:\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            f"• Статус: {'🟢 Активна' if settings['active'] else '🔴 Остановлена'}\n"
            f"• Дневная цель: {goal_display} вопросов\n"
            f"• Интервал: {interval_display} минут\n"
            f"• Вопросов сегодня: {settings['questions_today']}\n\n"
<<<<<<< HEAD
            f"📚 Вопросы:\n"
            f"• Всего вопросов: {qa_count}\n\n"
            f"⏰ Расписание:\n{schedule_text}\n\n"
            f"🔧 Команды для настройки:\n"
=======
            f"Вопросы:\n"
            f"• Всего вопросов: {qa_count}\n\n"
            f"Расписание:\n{schedule_text}\n\n"
            f"Команды для настройки:\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            "• `/set_daily <число>` - изменить цель\n"
            "• `/set_interval <мин> <макс>` - интервал\n"
            "• `/set_schedule` - настроить расписание\n"
            "• `/reset_settings` - сбросить настройки"
        )