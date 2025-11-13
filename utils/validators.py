# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny

import re
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

class Validators:
    """Класс валидаторов для проверки входных данных"""
    
    # Регулярные выражения
    TIME_PATTERN = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_time_format(time_str: str) -> bool:
        """Проверяет формат времени HH:MM"""
        return bool(Validators.TIME_PATTERN.match(time_str))

    @staticmethod
    def validate_time_range(start_time: str, end_time: str) -> Tuple[bool, Optional[str]]:
        """
        Проверяет корректность временного диапазона
        
        Returns:
            Tuple[bool, Optional[str]]: (Успех, Сообщение об ошибке)
        """
        if not Validators.validate_time_format(start_time):
            return False, "Неверный формат времени начала"
        
        if not Validators.validate_time_format(end_time):
            return False, "Неверный формат времени окончания"
        
        start = datetime.strptime(start_time, "%H:%M")
        end = datetime.strptime(end_time, "%H:%M")
        
        if start >= end:
            return False, "Время начала должно быть раньше времени окончания"
        
        return True, None

    @staticmethod
    def validate_question_answer_format(text: str) -> Tuple[bool, Optional[str], Optional[Dict[str, str]]]:
        """
        Валидирует формат вопроса-ответа
        
        Args:
            text: Текст в формате "Вопрос || Ответ"
            
        Returns:
            Tuple[bool, Optional[str], Optional[Dict]]: 
            (Успех, Сообщение об ошибке, Данные {question, answer})
        """
        if '||' not in text:
            return False, "Используйте формат: 'Вопрос || Ответ'", None
        
        parts = text.split('||', 1)
        question = parts[0].strip()
        answer = parts[1].strip()
        
        if not question:
            return False, "Вопрос не может быть пустым", None
        
        if not answer:
            return False, "Ответ не может быть пустым", None
        
        if len(question) > 500:
            return False, "Вопрос слишком длинный (макс. 500 символов)", None
        
        if len(answer) > 200:
            return False, "Ответ слишком длинный (макс. 200 символов)", None
        
        return True, None, {"question": question, "answer": answer}

    @staticmethod
    def validate_daily_goal(goal: Any) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Валидирует дневную цель
        
        Returns:
            Tuple[bool, Optional[str], Optional[int]]: 
            (Успех, Сообщение об ошибке, Числовое значение)
        """
        try:
            goal_int = int(goal)
        except (ValueError, TypeError):
            return False, "Цель должна быть числом", None
        
        if goal_int < 1:
            return False, "Цель должна быть не менее 1 вопроса", None
        
        if goal_int > 50:
            return False, "Цель не может превышать 50 вопросов", None
        
        return True, None, goal_int

    @staticmethod
    def validate_interval(min_interval: Any, max_interval: Any) -> Tuple[bool, Optional[str], Optional[Dict[str, int]]]:
        """
        Валидирует интервал времени
        
        Returns:
            Tuple[bool, Optional[str], Optional[Dict]]: 
            (Успех, Сообщение об ошибке, Данные {min, max})
        """
        try:
            min_int = int(min_interval)
            max_int = int(max_interval)
        except (ValueError, TypeError):
            return False, "Интервалы должны быть числами", None
        
        if min_int < 1:
            return False, "Минимальный интервал - 5 минут", None
        
        if max_int > 480:
            return False, "Максимальный интервал - 480 минут (8 часов)", None
        
        if min_int >= max_int:
            return False, "Минимальный интервал должен быть меньше максимального", None
        
        return True, None, {"min": min_int, "max": max_int}

    @staticmethod
    def validate_day_schedule_params(day_short: str, start_time: str, 
                                   end_time: str, enabled: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Валидирует параметры настройки дня расписания
        """
        day_map = {
            'mon': 'monday', 'tue': 'tuesday', 'wed': 'wednesday',
            'thu': 'thursday', 'fri': 'friday', 'sat': 'saturday', 'sun': 'sunday'
        }
        
        days_ru = {
            'monday': 'Понедельник', 'tuesday': 'Вторник', 'wednesday': 'Среда',
            'thursday': 'Четверг', 'friday': 'Пятница', 'saturday': 'Суббота', 
            'sunday': 'Воскресенье'
        }
        

        if day_short not in day_map:
            return False, "Неверный день. Используйте: mon, tue, wed, thu, fri, sat, sun", None
        

        if not Validators.validate_time_format(start_time):
            return False, "Неверный формат времени начала (используйте HH:MM)", None
        
        if not Validators.validate_time_format(end_time):
            return False, "Неверный формат времени окончания (используйте HH:MM)", None
        

        time_valid, time_error = Validators.validate_time_range(start_time, end_time)
        if not time_valid:
            return False, time_error, None
        
        if enabled not in ['on', 'off']:
            return False, "Статус должен быть 'on' или 'off'", None
        
        day_en = day_map[day_short]
        day_ru = days_ru[day_en]
        enabled_bool = enabled == 'on'
        
        return True, None, {
            "day_en": day_en,
            "day_ru": day_ru,
            "start_time": start_time,
            "end_time": end_time,
            "enabled": enabled_bool
        }

    @staticmethod
    def validate_question_id(qa_id: Any, qa_list: list) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        Валидирует ID вопроса
        
        Returns:
            Tuple[bool, Optional[str], Optional[Dict]]: 
            (Успех, Сообщение об ошибке, Данные вопроса)
        """
        try:
            qa_id_int = int(qa_id)
        except (ValueError, TypeError):
            return False, "ID вопроса должен быть числом", None
        
        question = next((q for q in qa_list if q.get('id') == qa_id_int), None)
        if not question:
            return False, f"Вопрос с ID {qa_id_int} не найден", None
        
        return True, None, question

    @staticmethod
    def validate_email(email: str) -> bool:
        """Проверяет валидность email адреса"""
        return bool(Validators.EMAIL_PATTERN.match(email))

    @staticmethod
    def sanitize_text(text: str, max_length: int = 500) -> str:
        """
        Очищает текст от потенциально опасных символов и обрезает до максимальной длины
        """
        sanitized = ' '.join(text.strip().split())
        
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length-3] + "..."
        
        return sanitized

    @staticmethod
    def validate_schedule_time_consistency(schedule: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Проверяет согласованность расписания (например, нет пересечений)
        """
        
        enabled_days = [day for day, day_schedule in schedule.items() 
                       if day_schedule.get("enabled", False)]
        
        if not enabled_days:
            return False, "Хотя бы один день должен быть включен"

        for day in enabled_days:
            day_schedule = schedule[day]
            start_time = day_schedule.get("start")
            end_time = day_schedule.get("end")
            
            if not start_time or not end_time:
                return False, f"День {day} имеет неполное расписание"
            
            valid, error = Validators.validate_time_range(start_time, end_time)
            if not valid:
                return False, f"Ошибка в расписании дня {day}: {error}"
        
        return True, None

    @staticmethod
    def calculate_schedule_coverage(schedule: Dict[str, Any]) -> Dict[str, Any]:
        """
        Рассчитывает покрытие расписания
        
        Returns:
            Dict с информацией о покрытии расписания
        """
        enabled_days = [day for day, day_schedule in schedule.items() 
                       if day_schedule.get("enabled", False)]
        
        total_hours = 0
        for day in enabled_days:
            day_schedule = schedule[day]
            start = datetime.strptime(day_schedule["start"], "%H:%M")
            end = datetime.strptime(day_schedule["end"], "%H:%M")
            hours = (end - start).seconds / 3600
            total_hours += hours
        
        return {
            "enabled_days": len(enabled_days),
            "total_hours_per_week": total_hours,
            "coverage_percentage": (len(enabled_days) / 7) * 100
        }

    @staticmethod
    def validate_user_input(text: str, input_type: str = "text") -> Tuple[bool, Optional[str]]:
        """
        Общая валидация пользовательского ввода
        
        Args:
            text: Введенный текст
            input_type: Тип ввода (text, number, time, etc.)
        """
        if not text or not text.strip():
            return False, "Ввод не может быть пустым"
        
        text = text.strip()
        
        if input_type == "number":
            if not text.isdigit():
                return False, "Введите число"
                
        elif input_type == "time":
            if not Validators.validate_time_format(text):
                return False, "Используйте формат HH:MM"
                
        elif input_type == "email":
            if not Validators.validate_email(text):
                return False, "Неверный формат email"
        
        if input_type == "text" and len(text) > 1000:
            return False, "Текст слишком длинный (макс. 1000 символов)"
        
        return True, None