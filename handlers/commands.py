# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny

import asyncio
from datetime import datetime
from core.logger import logger
from maxapi.types import MessageCreated
from .base import BaseHandler, MessageFormatter
from utils.keyboards import KeyboardManager
from utils.validators import Validators

class CommandHandlers(BaseHandler):
    """Обработчики команд бота с использованием валидаторов"""
    
    async def start_command(self, event: MessageCreated):
        logger.info(f"Получена команда /start от user_id={event.from_user.user_id}")
        """Обработчик команды /start"""
        user_id = str(event.from_user.user_id)

        self.storage.get_user_settings(user_id)
        self.storage.get_user_qa(user_id)

        await event.message.answer(
            "Добро пожаловать в умную викторину!\n"
            "Я помогу тебе эффективно запоминать информацию с помощью "
            "интервального повторения и адаптивного алгоритма.\n\n"
            "Выбери действие в меню ниже",
            attachments=[KeyboardManager.get_main_menu_keyboard()]
        )

    async def help_command(self, event: MessageCreated):
        """Обработчик команды /help"""
        logger.info(f"Получена команда /help от user_id={event.from_user.user_id}")
        await event.message.answer(
            "Помощь по командам:\n\n"
            "Добавление вопросов:\n"
            "• /add_qa Вопрос || Ответ - добавить пару\n"
            "• /my_qa - посмотреть все вопросы\n"
            "• /clear_qa - удалить все вопросы\n\n"
            "Управление викториной:\n"
            "• /start_quiz - запустить\n"
            "• /stop_quiz - остановить\n"
            "• /settings - текущие настройки\n\n"
            "Настройки:\n"
            "• /set_daily <число> - вопросов в день\n"
            "• /set_interval <мин> <макс> - интервал в минутах\n"
            "• /set_schedule - настройка расписания\n"
            "• /reset_settings - сбросить настройки\n\n"
            "Статистика:\n"
            "• /stats - общая статистика\n"
            "• /question_stats - статистика по вопросам\n\n"
            "Нужна помощь? Пиши вопросы прямо здесь!"
        )

    async def add_qa_pair(self, event: MessageCreated):
        """Обработчик команды /add_qa с валидацией"""
        logger.info(f"Получена команда /add_qa от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        text = event.message.body.text

        command_text = text.replace('/add_qa', '').strip()

        is_valid, error_msg, qa_data = Validators.validate_question_answer_format(command_text)
        
        if not is_valid:
            await event.message.answer(
                f"❌ {error_msg}\n\n"
                "Используй: `/add_qa Вопрос || Ответ`\n\n"
                "Пример:\n"
                "`/add_qa Столица Франции || Париж`"
            )
            return

        question = Validators.sanitize_text(qa_data["question"], 500)
        answer = Validators.sanitize_text(qa_data["answer"], 200)

        success = self.storage.add_user_qa(user_id, question, answer)
        if success:
            qa_list = self.storage.get_user_qa(user_id)
            await event.message.answer(
                f"Вопрос добавлен!\n\n"
                f"Вопрос: {question}\n"
                f"Ответ: {answer}\n\n"
                f"Всего вопросов: {len(qa_list)}"
            )
        else:
            await event.message.answer("❌ Ошибка при сохранении вопроса")

    async def show_my_qa(self, event: MessageCreated):
        """Обработчик команды /my_qa"""
        logger.info(f"Получена команда /my_qa от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        qa_list = self.storage.get_user_qa(user_id)
        
        formatted_text = MessageFormatter.format_qa_list(qa_list)
        await event.message.answer(formatted_text)

    async def remove_qa_command(self, event: MessageCreated):
        """Обработчик команды /remove_qa с валидацией"""
        logger.info(f"Получена команда /remove_qa от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        parts = text.split()
        if len(parts) < 2:
            await event.message.answer(
                "❌ Неверный формат!\n\n"
                "Используй: `/remove_qa <ID>`\n\n"
                "Пример: `/remove_qa 3`\n"
                "Посмотреть ID вопросов: `/my_qa`"
            )
            return
        
        qa_id_str = parts[1]
        qa_list = self.storage.get_user_qa(user_id)
        

        is_valid, error_msg, question_data = Validators.validate_question_id(qa_id_str, qa_list)
        
        if not is_valid:
            await event.message.answer(f"❌ {error_msg}")
            return

        success = self.storage.remove_user_qa(user_id, int(qa_id_str))
        if success:
            await event.message.answer(
                f"Вопрос удален!\n\n"
                f"Вопрос: {question_data['question']}\n"
                f"Ответ: {question_data['answer']}\n"
                f"ID: {qa_id_str}"
            )
        else:
            await event.message.answer("❌ Ошибка при удалении вопроса")

    async def clear_qa(self, event: MessageCreated):
        """Обработчик команды /clear_qa"""
        logger.info(f"Получена команда /clear_qa от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        qa_list = self.storage.get_user_qa(user_id)
        
        if not qa_list:
            await event.message.answer("У тебя и так нет вопросов.")
            return


        self.quiz_manager.stop_quiz_for_user(user_id)
        self.storage.update_user_settings(user_id, active=False)

        self.storage.save_user_qa(user_id, [])
        
        await event.message.answer(
            f"Все вопросы очищены!\n\n"
            f"Удалено вопросов: {len(qa_list)}\n"
            f"Викторина остановлена.\n\n"
            f"Добавь новые вопросы через `/add_qa`"
        )

    async def start_quiz(self, event: MessageCreated):
        """Обработчик команды /start_quiz с валидацией настроек"""
        logger.info(f"Получена команда /start_quiz от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        chat_id = event.chat.chat_id

        qa_list = self.storage.get_user_qa(user_id)
        if not qa_list:
            await event.message.answer(
                "❌ Сначала добавь вопросы!\n\n"
                "У тебя пока нет вопросов для викторины.\n"
                "Добавь вопросы через: `/add_qa Вопрос || Ответ`"
            )
            return
        
        settings = self.storage.get_user_settings(user_id)
        if settings["active"]:
            await event.message.answer(
                "ℹ️ Викторина уже запущена!\n\n"
                "Используй `/stop_quiz` чтобы остановить,\n"
                "или `/settings` чтобы изменить настройки."
            )
            return

        daily_goal_valid, daily_error, _ = Validators.validate_daily_goal(settings["daily_goal"])
        interval_valid, interval_error, _ = Validators.validate_interval(
            settings["min_interval"], settings["max_interval"]
        )
        
        if not daily_goal_valid:
            await event.message.answer(
                f"❌ Некорректная дневная цель: {settings['daily_goal']}\n\n"
                f"Исправь настройки: `/set_daily <число>`"
            )
            return
            
        if not interval_valid:
            await event.message.answer(
                f"❌ Некорректный интервал: {settings['min_interval']}-{settings['max_interval']}\n\n"
                f"Исправь настройки: `/set_interval <мин> <макс>`"
            )
            return

        self.storage.update_user_settings(user_id, active=True, last_study_date=datetime.now().isoformat())

        asyncio.create_task(self.quiz_manager.smart_quiz_scheduler(user_id, chat_id))

        message = MessageFormatter.format_quiz_start_message(settings, len(qa_list))
        await event.message.answer(message)

    async def stop_quiz(self, event: MessageCreated):
        """Обработчик команды /stop_quiz"""
        logger.info(f"Получена команда /stop_quiz от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        settings = self.storage.get_user_settings(user_id)
        
        if not settings["active"]:
            await event.message.answer(
                "ℹ️ Викторина и так остановлена.\n\n"
                "Используй `/start_quiz` чтобы запустить."
            )
            return

        self.quiz_manager.stop_quiz_for_user(user_id)
        self.storage.update_user_settings(user_id, active=False)
        
        stats = self.storage.get_user_stats(user_id)
        questions_today = settings["questions_today"]
        
        await event.message.answer(
            "Викторина остановлена\n\n"
            f"Сегодня:\n"
            f"• Задано вопросов: {questions_today}\n"
            f"• Дневная цель: {settings['daily_goal']}\n\n"
            f"Общая статистика:\n"
            f"• Всего ответов: {stats['total_questions_answered']}\n"
            f"• Правильных: {stats['correct_answers']}\n"
            f"• Текущая серия: {stats['current_streak']}\n\n"
            "Чтобы запустить снова: `/start_quiz`"
        )

    async def show_settings(self, event: MessageCreated):
        """Обработчик команды /settings"""
        logger.info(f"Получена команда /settings от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        settings = self.storage.get_user_settings(user_id)
        stats = self.storage.get_user_stats(user_id)
        qa_count = len(self.storage.get_user_qa(user_id))
        
        formatted_message = MessageFormatter.format_settings_message(settings, stats, qa_count)
        await event.message.answer(formatted_message)

    async def set_daily_goal(self, event: MessageCreated):
        """Обработчик команды /set_daily с валидацией"""
        logger.info(f"Получена команда /set_daily от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        parts = text.split()
        if len(parts) < 2:
            await event.message.answer(
                "❌ Неверный формат!\n\n"
                "Используй: `/set_daily <число>`\n\n"
                "Пример: `/set_daily 15`\n"
                "Это установит цель в 15 вопросов в день."
            )
            return
        
        goal_str = parts[1]

        is_valid, error_msg, goal_value = Validators.validate_daily_goal(goal_str)
        
        if not is_valid:
            await event.message.answer(f"❌ {error_msg}")
            return
        
        settings = self.storage.get_user_settings(user_id)
        old_goal = settings["daily_goal"]
        self.storage.update_user_settings(user_id, daily_goal=goal_value)
        
        await event.message.answer(
            f"✅ Дневная цель изменена!\n\n"
            f"• Было: {old_goal} вопросов в день\n"
            f"• Стало: {goal_value} вопросов в день\n\n"
            f"Вопросов сегодня: {settings['questions_today']}/{goal_value}"
        )

    async def set_interval(self, event: MessageCreated):
        """Обработчик команды /set_interval с валидацией"""
        logger.info(f"Получена команда /set_interval от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        parts = text.split()
        if len(parts) < 3:
            await event.message.answer(
                "❌ Неверный формат!\n\n"
                "Используй: `/set_interval <мин> <макс>`\n\n"
                "Пример: `/set_interval 30 120`\n"
                "Это установит интервал от 30 до 120 минут между вопросами."
            )
            return
        
        min_str = parts[1]
        max_str = parts[2]

        is_valid, error_msg, interval_data = Validators.validate_interval(min_str, max_str)
        
        if not is_valid:
            await event.message.answer(f"❌ {error_msg}")
            return
        
        settings = self.storage.get_user_settings(user_id)
        old_min = settings["min_interval"]
        old_max = settings["max_interval"]
        
        self.storage.update_user_settings(
            user_id, 
            min_interval=interval_data["min"], 
            max_interval=interval_data["max"]
        )
        
        await event.message.answer(
            f"✅ Интервал изменен!\n\n"
            f"• Было: {old_min} - {old_max} минут\n"
            f"• Стало: {interval_data['min']} - {interval_data['max']} минут\n\n"
            f"Вопросы будут приходить случайно в этом интервале."
        )

    async def set_schedule_command(self, event: MessageCreated):
        """Обработчик команды /set_schedule"""
        logger.info(f"Получена команда /set_schedule от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        settings = self.storage.get_user_settings(user_id)

        days_ru = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник', 
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница',
            'saturday': 'Суббота',
            'sunday': 'Воскресенье'
        }
        
        schedule_text = "Текущее расписание:\n\n"
        for day_en, day_ru in days_ru.items():
            schedule = settings["schedule"][day_en]
            status = "✅" if schedule["enabled"] else "❌"
            schedule_text += f"{status} {day_ru}: {schedule['start']} - {schedule['end']}\n"
        
        instructions = (
            "\nКак изменить расписание:\n\n"
            "Используй команду:\n"
            "`/set_day <день> <начало> <конец> <вкл/выкл>`\n\n"
            "Параметры:\n"
            "• `<день>`: mon, tue, wed, thu, fri, sat, sun\n"
            "• `<начало>`, `<конец>`: время в формате HH:MM\n"
            "• `<вкл/выкл>`: on или off\n\n"
            "Примеры:\n"
            "• `/set_day mon 09:00 18:00 on`\n"
            "• `/set_day sat 10:00 16:00 off`\n"
            "• `/set_day sun 00:00 00:00 off` - отключить день"
        )
        
        await event.message.answer(schedule_text + instructions)

    async def set_day_schedule(self, event: MessageCreated):
        """Обработчик команды /set_day"""
        logger.info(f"Получена команда /set_day от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        try:
            parts = text.split()
            day_short = parts[1].lower()
            start_time = parts[2]
            end_time = parts[3]
            enabled = parts[4].lower()

            is_valid, error_msg, schedule_data = Validators.validate_day_schedule_params(
                day_short, start_time, end_time, enabled
            )
            
            if not is_valid:
                await event.message.answer(f"❌ {error_msg}")
                return

            settings = self.storage.get_user_settings(user_id)
            settings["schedule"][schedule_data["day_en"]] = {
                "start": schedule_data["start_time"],
                "end": schedule_data["end_time"],
                "enabled": schedule_data["enabled"]
            }
            self.storage.save_user_settings(user_id, settings)
            
            status = "включен" if schedule_data["enabled"] else "отключен"
            await event.message.answer(
                f"✅ Расписание обновлено!\n\n"
                f"{schedule_data['day_ru']} {status}\n"
                f"Время: {schedule_data['start_time']} - {schedule_data['end_time']}\n\n"
                f"Посмотреть всё расписание: `/set_schedule`"
            )
            
        except (IndexError, ValueError):
            await event.message.answer(
                "❌ Неверный формат!\n\n"
                "Используй: `/set_day <день> <начало> <конец> <вкл/выкл>`\n\n"
                "Примеры:\n"
                "• `/set_day mon 09:00 18:00 on`\n"
                "• `/set_day sat 10:00 16:00 off`\n\n"
                "Дни: mon, tue, wed, thu, fri, sat, sun\n"
                "Статус: on или off"
            )

    async def confirm_reset_settings(self, event: MessageCreated):
        """Обработчик команды /reset_settings"""
        user_id = str(event.from_user.user_id)

        self.quiz_manager.stop_quiz_for_user(user_id)

        default_settings = self.storage.get_default_settings()
        self.storage.save_user_settings(user_id, default_settings)
        
        await event.message.answer(
            "🔄 Настройки сброшены!\n\n"
            "Все настройки возвращены к значениям по умолчанию.\n"
            "Викторина остановлена.\n\n"
            "Посмотреть настройки: `/settings`\n"
            "Настроить заново: `/set_schedule`"
        )

    async def cancel_reset_settings(self, event: MessageCreated):
        """Отмена сброса настроек"""
        await event.message.answer(
            "❌ Сброс настроек отменён.\n\n"
            "Ваши текущие настройки сохранены.",
            attachments=[KeyboardManager.get_main_menu_keyboard()]
    )

    async def show_stats(self, event: MessageCreated):
        """Обработчик команды /stats"""
        logger.info(f"Получена команда /stats от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        stats = self.storage.get_user_stats(user_id)
        settings = self.storage.get_user_settings(user_id)
        qa_count = len(self.storage.get_user_qa(user_id))

        total_answered = stats['total_questions_answered']
        if total_answered > 0:
            correct_percent = (stats['correct_answers'] / total_answered) * 100
            avg_response_time = stats['average_response_time']
        else:
            correct_percent = 0
            avg_response_time = 0

        if avg_response_time < 60:
            time_text = f"{avg_response_time:.1f} сек"
        else:
            time_text = f"{avg_response_time/60:.1f} мин"
        
        await event.message.answer(
            "Твоя статистика:\n\n"
            f"Обучение:\n"
            f"• Всего вопросов: {qa_count}\n"
            f"• Вопросов сегодня: {settings['questions_today']}/{settings['daily_goal']}\n"
            f"• Статус: {'🟢 Активно' if settings['active'] else '🔴 Остановлено'}\n\n"
            f"Результаты:\n"
            f"• Всего ответов: {total_answered}\n"
            f"• Правильных: {stats['correct_answers']} ({correct_percent:.1f}%)\n"
            f"• Текущая серия: {stats['current_streak']}\n"
            f"• Лучшая серия: {stats['best_streak']}\n"
            f"• Среднее время: {time_text}\n\n"
            f"Время обучения:\n"
            f"• Всего: {stats['total_study_time_minutes']} минут\n"
            f"• Последнее: {datetime.fromisoformat(stats['last_study_date']).strftime('%d/%m/%Y, %H:%M') if stats.get('last_study_date') else 'еще не было'}\n\n"
            f"Детальная статистика: `/question_stats`"
        )

    async def show_question_stats(self, event: MessageCreated):
        """Обработчик команды /question_stats"""
        logger.info(f"Получена команда /question_stats от user_id={event.from_user.user_id}")
        user_id = str(event.from_user.user_id)
        qa_list = self.storage.get_user_qa(user_id)
        
        if not qa_list:
            await event.message.answer("У тебя пока нет вопросов для статистики.")
            return
        
        text = "Статистика по вопросам:\n\n"
        
        for i, qa in enumerate(qa_list[:10], 1):
            qa_id = qa.get('id', i)
            q_stats = self.storage.get_question_stats(user_id, qa_id)
            
            times_asked = q_stats['times_asked']
            times_correct = q_stats['times_correct']
            
            if times_asked > 0:
                success_rate = (times_correct / times_asked) * 100
                success_emoji = "🟢" if success_rate >= 80 else "🟡" if success_rate >= 50 else "🔴"
                success_text = f"{success_rate:.0f}%"
            else:
                success_emoji = "⚪"
                success_text = "еще не задан"
            
            text += f"{success_emoji} {qa['question']}\n"
            text += f"   Успешность: {success_text} ({times_correct}/{times_asked})\n\n"
        
        if len(qa_list) > 10:
            text += f"*... и еще {len(qa_list) - 10} вопросов*\n\n"
        
        text += "Обозначения:\n"
        text += "🟢 >80% 🟡 50-80% 🔴 <50% ⚪ не задавался"
        
        await event.message.answer(text)

    def set_other_handlers(self, settings_handlers, stats_handlers):
        """Устанавливает ссылки на другие обработчики для callback-ов"""
        pass