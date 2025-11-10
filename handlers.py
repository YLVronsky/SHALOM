# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# handlers.py

import asyncio
import logging
from maxapi import Bot
import re
from datetime import datetime, time
from maxapi import Dispatcher
from maxapi.types import MessageCreated, Command, MessageCallback, DialogCleared
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton, LinkButton
from quiz_manager import QuizManager

from storage import (
    save_user_qa, get_user_qa, add_user_qa, remove_user_qa,
    get_current_question, remove_current_question,
    get_user_settings, save_user_settings, update_user_settings,
    get_user_stats, update_user_stats, get_question_stats,
    get_default_settings
)
def get_main_menu_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        CallbackButton(text="📚 Мои вопросы", payload="my_qa"),
        CallbackButton(text="➕ Добавить вопрос", payload="add_qa_hint")
    )
    builder.row(
        CallbackButton(text="🎯 Запустить викторину", payload="start_quiz"),
        CallbackButton(text="⏹ Остановить викторину", payload="stop_quiz")
    )
    builder.row(
        CallbackButton(text="⚙️ Настройки", payload="settings"),
        CallbackButton(text="📊 Статистика", payload="stats")
    )
    builder.row(
        CallbackButton(text="❓ Помощь", payload="help")
    )
    return builder.as_markup()

def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="↩️ Назад в меню", payload="main_menu"))
    return builder.as_markup()

def register_handlers(dp: Dispatcher, quiz_manager: QuizManager):
    """Регистрирует все обработчики сообщений и команд."""

    # --- Основные команды ---

    @dp.message_created(Command('start'))
    async def start_command(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        get_user_settings(user_id)  # инициализация
        get_user_qa(user_id)

        await event.message.answer(
            "🎯 **Добро пожаловать в умную викторину!**\n"
            "Я помогу тебе эффективно запоминать информацию с помощью "
            "интервального повторения и адаптивного алгоритма.\n\n"
            "Выбери действие в меню ниже 👇",
            attachments=[get_main_menu_keyboard()]
        )

    @dp.message_created(Command('help'))
    async def help_command(event: MessageCreated):
        await event.message.answer(
            "📖 **Помощь по командам:**\n\n"
            "**Добавление вопросов:**\n"
            "• /add_qa Вопрос || Ответ - добавить пару\n"
            "• /my_qa - посмотреть все вопросы\n"
            "• /clear_qa - удалить все вопросы\n\n"
            "**Управление викториной:**\n"
            "• /start_quiz - запустить\n"
            "• /stop_quiz - остановить\n"
            "• /settings - текущие настройки\n\n"
            "**Настройки:**\n"
            "• /set_daily <число> - вопросов в день\n"
            "• /set_interval <мин> <макс> - интервал в минутах\n"
            "• /set_schedule - настройка расписания\n\n"
            "**Статистика:**\n"
            "• /stats - общая статистика\n"
            "• /question_stats - статистика по вопросам\n\n"
            "Нужна помощь? Пиши вопросы прямо здесь!"
        )

    # --- Управление вопросами ---

    @dp.message_created(Command('add_qa'))
    async def add_qa_pair(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        if '||' not in text:
            await event.message.answer(
                "❌ **Неверный формат!**\n\n"
                "Используй: `/add_qa Вопрос || Ответ`\n\n"
                "**Пример:**\n"
                "`/add_qa Столица Франции || Париж`"
            )
            return

        parts = text.split('||', 1)
        question = parts[0].replace('/add_qa', '').strip()
        answer = parts[1].strip()

        if not question or not answer:
            await event.message.answer("❌ Вопрос и ответ не могут быть пустыми!")
            return

        if len(question) > 500:
            await event.message.answer("❌ Вопрос слишком длинный (макс. 500 символов)")
            return

        if len(answer) > 200:
            await event.message.answer("❌ Ответ слишком длинный (макс. 200 символов)")
            return

        success = add_user_qa(user_id, question, answer)
        if success:
            qa_list = get_user_qa(user_id)
            await event.message.answer(
                f"✅ **Вопрос добавлен!**\n\n"
                f"**Вопрос:** {question}\n"
                f"**Ответ:** {answer}\n\n"
                f"📊 Всего вопросов: **{len(qa_list)}**"
            )
        else:
            await event.message.answer("❌ Ошибка при сохранении вопроса")

    @dp.message_created(Command('my_qa'))
    async def show_my_qa(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        qa_list = get_user_qa(user_id)
        
        if not qa_list:
            await event.message.answer(
                "📝 **У тебя пока нет вопросов.**\n\n"
                "Добавь первый вопрос:\n"
                "`/add_qa Вопрос || Ответ`"
            )
            return

        # Группируем вопросы по частям для избежания ограничения длины
        text = f"📚 **Твои вопросы ({len(qa_list)}):**\n\n"
        
        for i, qa in enumerate(qa_list, 1):
            question_text = qa['question']
            answer_text = qa['answer']
            qa_id = qa.get('id', i)
            
            qa_entry = f"**{i}. ❓ {question_text}**\n   💡 Ответ: {answer_text}\n   🆔 ID: {qa_id}\n\n"
            
            # Если добавление этого вопроса превысит лимит, отправляем текущую часть
            if len(text) + len(qa_entry) > 3500:
                await event.message.answer(text)
                text = f"📚 **Продолжение ({len(qa_list)}):**\n\n"
            
            text += qa_entry

        text += "\n💡 **Управление вопросами:**\n"
        text += "• `/remove_qa <ID>` - удалить вопрос\n"
        text += "• `/clear_qa` - очистить все вопросы"
        
        await event.message.answer(text)

    @dp.message_created(Command('remove_qa'))
    async def remove_qa_command(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        try:
            qa_id = int(text.split()[1])
        except (IndexError, ValueError):
            await event.message.answer(
                "❌ **Неверный формат!**\n\n"
                "Используй: `/remove_qa <ID>`\n\n"
                "**Пример:** `/remove_qa 3`\n"
                "Посмотреть ID вопросов: `/my_qa`"
            )
            return

        qa_list = get_user_qa(user_id)
        question_to_remove = next((q for q in qa_list if q.get('id') == qa_id), None)
        
        if not question_to_remove:
            await event.message.answer(f"❌ Вопрос с ID {qa_id} не найден")
            return

        success = remove_user_qa(user_id, qa_id)
        if success:
            await event.message.answer(
                f"✅ **Вопрос удален!**\n\n"
                f"**Вопрос:** {question_to_remove['question']}\n"
                f"**Ответ:** {question_to_remove['answer']}\n"
                f"🆔 ID: {qa_id}"
            )
        else:
            await event.message.answer("❌ Ошибка при удалении вопроса")

    @dp.message_created(Command('clear_qa'))
    async def clear_qa(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        qa_list = get_user_qa(user_id)
        
        if not qa_list:
            await event.message.answer("📝 У тебя и так нет вопросов.")
            return

        # Останавливаем викторину, если активна
        quiz_manager.stop_quiz_for_user(user_id)
        update_user_settings(user_id, active=False)
        
        # Очищаем вопросы
        save_user_qa(user_id, [])
        
        await event.message.answer(
            f"🗑 **Все вопросы очищены!**\n\n"
            f"Удалено вопросов: **{len(qa_list)}**\n"
            f"Викторина остановлена.\n\n"
            f"Добавь новые вопросы через `/add_qa`"
        )

    # --- Управление викториной ---

    @dp.message_created(Command('start_quiz'))
    async def start_quiz(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        chat_id = event.chat.chat_id
        
        # Проверяем наличие вопросов
        qa_list = get_user_qa(user_id)
        if not qa_list:
            await event.message.answer(
                "❌ **Сначала добавь вопросы!**\n\n"
                "У тебя пока нет вопросов для викторины.\n"
                "Добавь вопросы через: `/add_qa Вопрос || Ответ`"
            )
            return
        
        settings = get_user_settings(user_id)
        if settings["active"]:
            await event.message.answer(
                "ℹ️ **Викторина уже запущена!**\n\n"
                "Используй `/stop_quiz` чтобы остановить,\n"
                "или `/settings` чтобы изменить настройки."
            )
            return

        # Активируем викторину
        update_user_settings(user_id, active=True)
        
        # Запускаем умный планировщик
        asyncio.create_task(quiz_manager.smart_quiz_scheduler(user_id, chat_id))
        
        # Формируем информацию о расписании
        schedule_text = ""
        enabled_days = [day for day, schedule in settings["schedule"].items() if schedule["enabled"]]
        if enabled_days:
            schedule_text = f"• Дни: {', '.join(enabled_days)}\n"
            sample_day = enabled_days[0]
            schedule_text += f"• Время: {settings['schedule'][sample_day]['start']} - {settings['schedule'][sample_day]['end']}\n"
        
        await event.message.answer(
            "🎯 **Умная викторина запущена!**\n\n"
            f"📊 **Настройки:**\n"
            f"• Дневная цель: **{settings['daily_goal']}** вопросов\n"
            f"• Интервал: **{settings['min_interval']} - {settings['max_interval']}** минут\n"
            f"{schedule_text}"
            f"• Доступно вопросов: **{len(qa_list)}**\n\n"
            "⏰ Вопросы будут приходить в случайное время в указанном интервале.\n"
            "📈 Алгоритм адаптируется под твои результаты!\n\n"
            "**Управление:**\n"
            "• `/stop_quiz` - остановить викторину\n"
            "• `/settings` - изменить настройки\n"
            "• `/stats` - посмотреть статистику"
        )

    @dp.message_created(Command('stop_quiz'))
    async def stop_quiz(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        settings = get_user_settings(user_id)
        
        if not settings["active"]:
            await event.message.answer(
                "ℹ️ **Викторина и так остановлена.**\n\n"
                "Используй `/start_quiz` чтобы запустить."
            )
            return

        # Останавливаем викторину
        quiz_manager.stop_quiz_for_user(user_id)
        update_user_settings(user_id, active=False)
        
        stats = get_user_stats(user_id)
        questions_today = settings["questions_today"]
        
        await event.message.answer(
            "⏹ **Викторина остановлена**\n\n"
            f"📊 **Сегодня:**\n"
            f"• Задано вопросов: **{questions_today}**\n"
            f"• Дневная цель: {settings['daily_goal']}\n\n"
            f"📈 **Общая статистика:**\n"
            f"• Всего ответов: **{stats['total_questions_answered']}**\n"
            f"• Правильных: **{stats['correct_answers']}**\n"
            f"• Текущая серия: **{stats['current_streak']}**\n\n"
            "Чтобы запустить снова: `/start_quiz`"
        )

    # --- Настройки ---

    @dp.message_created(Command('settings'))
    async def show_settings(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        settings = get_user_settings(user_id)
        stats = get_user_stats(user_id)
        qa_count = len(get_user_qa(user_id))
        
        # Форматируем информацию о расписании
        schedule_info = []
        for day, schedule in settings["schedule"].items():
            if schedule["enabled"]:
                status = "✅"
            else:
                status = "❌"
            schedule_info.append(f"{status} {day}: {schedule['start']} - {schedule['end']}")
        
        schedule_text = "\n".join(schedule_info) if schedule_info else "❌ Расписание не настроено"
        
        await event.message.answer(
            "⚙️ **Твои настройки:**\n\n"
            f"📊 **Основные:**\n"
            f"• Статус: **{'🟢 Активна' if settings['active'] else '🔴 Остановлена'}**\n"
            f"• Дневная цель: **{settings['daily_goal']}** вопросов\n"
            f"• Интервал: **{settings['min_interval']} - {settings['max_interval']}** минут\n"
            f"• Вопросов сегодня: **{settings['questions_today']}**\n\n"
            f"📚 **Вопросы:**\n"
            f"• Всего вопросов: **{qa_count}**\n\n"
            f"⏰ **Расписание:**\n{schedule_text}\n\n"
            f"🔧 **Команды для настройки:**\n"
            "• `/set_daily <число>` - изменить цель\n"
            "• `/set_interval <мин> <макс>` - интервал\n"
            "• `/set_schedule` - настроить расписание\n"
            "• `/reset_settings` - сбросить настройки"
        )

    @dp.message_created(Command('set_daily'))
    async def set_daily_goal(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        try:
            goal = int(text.split()[1])
            if goal < 1 or goal > 50:
                await event.message.answer(
                    "❌ **Неверное значение!**\n\n"
                    "Дневная цель должна быть от **1** до **50** вопросов.\n"
                    "**Пример:** `/set_daily 15`"
                )
                return
        except (IndexError, ValueError):
            await event.message.answer(
                "❌ **Неверный формат!**\n\n"
                "Используй: `/set_daily <число>`\n\n"
                "**Пример:** `/set_daily 15`\n"
                "Это установит цель в 15 вопросов в день."
            )
            return
        
        settings = get_user_settings(user_id)
        old_goal = settings["daily_goal"]
        update_user_settings(user_id, daily_goal=goal)
        
        await event.message.answer(
            f"✅ **Дневная цель изменена!**\n\n"
            f"• Было: **{old_goal}** вопросов в день\n"
            f"• Стало: **{goal}** вопросов в день\n\n"
            f"📊 Вопросов сегодня: {settings['questions_today']}/{goal}"
        )

    @dp.message_created(Command('set_interval'))
    async def set_interval(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        try:
            parts = text.split()
            min_int = int(parts[1])
            max_int = int(parts[2])
            
            if min_int < 5 or max_int > 480:  # от 5 минут до 8 часов
                await event.message.answer(
                    "❌ **Неверные значения!**\n\n"
                    "Интервал должен быть:\n"
                    "• Минимум: **5** минут\n"
                    "• Максимум: **480** минут (8 часов)\n\n"
                    "**Пример:** `/set_interval 30 120`"
                )
                return
                
            if min_int >= max_int:
                await event.message.answer(
                    "❌ **Минимум должен быть меньше максимума!**\n\n"
                    "**Пример:** `/set_interval 30 120`\n"
                    "• 30 - минимальный интервал\n"
                    "• 120 - максимальный интервал"
                )
                return
                
        except (IndexError, ValueError):
            await event.message.answer(
                "❌ **Неверный формат!**\n\n"
                "Используй: `/set_interval <мин> <макс>`\n\n"
                "**Пример:** `/set_interval 30 120`\n"
                "Это установит интервал от 30 до 120 минут между вопросами."
            )
            return
        
        settings = get_user_settings(user_id)
        old_min = settings["min_interval"]
        old_max = settings["max_interval"]
        
        update_user_settings(user_id, min_interval=min_int, max_interval=max_int)
        
        await event.message.answer(
            f"✅ **Интервал изменен!**\n\n"
            f"• Было: **{old_min} - {old_max}** минут\n"
            f"• Стало: **{min_int} - {max_int}** минут\n\n"
            f"⏰ Вопросы будут приходить случайно в этом интервале."
        )

    @dp.message_created(Command('set_schedule'))
    async def set_schedule_command(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        settings = get_user_settings(user_id)
        
        # Показываем текущее расписание и инструкции
        days_ru = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник', 
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница',
            'saturday': 'Суббота',
            'sunday': 'Воскресенье'
        }
        
        schedule_text = "📅 **Текущее расписание:**\n\n"
        for day_en, day_ru in days_ru.items():
            schedule = settings["schedule"][day_en]
            status = "✅" if schedule["enabled"] else "❌"
            schedule_text += f"{status} **{day_ru}**: {schedule['start']} - {schedule['end']}\n"
        
        instructions = (
            "\n🔧 **Как изменить расписание:**\n\n"
            "Используй команду:\n"
            "`/set_day <день> <начало> <конец> <вкл/выкл>`\n\n"
            "**Параметры:**\n"
            "• `<день>`: mon, tue, wed, thu, fri, sat, sun\n"
            "• `<начало>`, `<конец>`: время в формате HH:MM\n"
            "• `<вкл/выкл>`: on или off\n\n"
            "**Примеры:**\n"
            "• `/set_day mon 09:00 18:00 on`\n"
            "• `/set_day sat 10:00 16:00 off`\n"
            "• `/set_day sun 00:00 00:00 off` - отключить день"
        )
        
        await event.message.answer(schedule_text + instructions)

    @dp.message_created(Command('set_day'))
    async def set_day_schedule(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        day_map = {
            'mon': 'monday', 'tue': 'tuesday', 'wed': 'wednesday',
            'thu': 'thursday', 'fri': 'friday', 'sat': 'saturday', 'sun': 'sunday'
        }
        
        days_ru = {
            'monday': 'Понедельник', 'tuesday': 'Вторник', 'wednesday': 'Среда',
            'thursday': 'Четверг', 'friday': 'Пятница', 'saturday': 'Суббота', 
            'sunday': 'Воскресенье'
        }
        
        try:
            parts = text.split()
            day_short = parts[1].lower()
            start_time = parts[2]
            end_time = parts[3]
            enabled = parts[4].lower()
            
            # Проверяем день
            if day_short not in day_map:
                await event.message.answer(
                    "❌ **Неверный день!**\n\n"
                    "Доступные дни: mon, tue, wed, thu, fri, sat, sun\n\n"
                    "**Пример:** `/set_day mon 09:00 18:00 on`"
                )
                return
            
            # Проверяем формат времени
            time_pattern = re.compile(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
            if not time_pattern.match(start_time) or not time_pattern.match(end_time):
                await event.message.answer(
                    "❌ **Неверный формат времени!**\n\n"
                    "Используй формат HH:MM (24 часа)\n\n"
                    "**Пример:** `/set_day mon 09:00 18:00 on`"
                )
                return
            
            # Проверяем статус
            if enabled not in ['on', 'off']:
                await event.message.answer(
                    "❌ **Неверный статус!**\n\n"
                    "Используй: 'on' или 'off'\n\n"
                    "**Пример:** `/set_day mon 09:00 18:00 on`"
                )
                return
            
            day_en = day_map[day_short]
            day_ru = days_ru[day_en]
            enabled_bool = enabled == 'on'
            
            # Обновляем настройки
            settings = get_user_settings(user_id)
            settings["schedule"][day_en] = {
                "start": start_time,
                "end": end_time,
                "enabled": enabled_bool
            }
            save_user_settings(user_id, settings)
            
            status = "включен" if enabled_bool else "отключен"
            await event.message.answer(
                f"✅ **Расписание обновлено!**\n\n"
                f"**{day_ru}** {status}\n"
                f"Время: {start_time} - {end_time}\n\n"
                f"Посмотреть всё расписание: `/set_schedule`"
            )
            
        except (IndexError, ValueError):
            await event.message.answer(
                "❌ **Неверный формат!**\n\n"
                "Используй: `/set_day <день> <начало> <конец> <вкл/выкл>`\n\n"
                "**Примеры:**\n"
                "• `/set_day mon 09:00 18:00 on`\n"
                "• `/set_day sat 10:00 16:00 off`\n\n"
                "**Дни:** mon, tue, wed, thu, fri, sat, sun\n"
                "**Статус:** on или off"
            )

    @dp.message_created(Command('reset_settings'))
    async def reset_settings(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        
        # Останавливаем викторину
        quiz_manager.stop_quiz_for_user(user_id)
        
        # Сбрасываем настройки к значениям по умолчанию
        default_settings = get_default_settings()
        save_user_settings(user_id, default_settings)
        
        await event.message.answer(
            "🔄 **Настройки сброшены!**\n\n"
            "Все настройки возвращены к значениям по умолчанию.\n"
            "Викторина остановлена.\n\n"
            "Посмотреть настройки: `/settings`\n"
            "Настроить заново: `/set_schedule`"
        )

    # --- Статистика ---

    @dp.message_created(Command('stats'))
    async def show_stats(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        stats = get_user_stats(user_id)
        settings = get_user_settings(user_id)
        qa_count = len(get_user_qa(user_id))
        
        # Рассчитываем проценты
        total_answered = stats['total_questions_answered']
        if total_answered > 0:
            correct_percent = (stats['correct_answers'] / total_answered) * 100
            avg_response_time = stats['average_response_time']
        else:
            correct_percent = 0
            avg_response_time = 0
        
        # Форматируем время
        if avg_response_time < 60:
            time_text = f"{avg_response_time:.1f} сек"
        else:
            time_text = f"{avg_response_time/60:.1f} мин"
        
        await event.message.answer(
            "📊 **Твоя статистика:**\n\n"
            f"🎯 **Обучение:**\n"
            f"• Всего вопросов: **{qa_count}**\n"
            f"• Вопросов сегодня: **{settings['questions_today']}/{settings['daily_goal']}**\n"
            f"• Статус: **{'🟢 Активно' if settings['active'] else '🔴 Остановлено'}**\n\n"
            f"📈 **Результаты:**\n"
            f"• Всего ответов: **{total_answered}**\n"
            f"• Правильных: **{stats['correct_answers']}** ({correct_percent:.1f}%)\n"
            f"• Текущая серия: **{stats['current_streak']}**\n"
            f"• Лучшая серия: **{stats['best_streak']}**\n"
            f"• Среднее время: **{time_text}**\n\n"
            f"⏱ **Время обучения:**\n"
            f"• Всего: **{stats['total_study_time_minutes']}** минут\n"
            f"• Последнее: {stats['last_study_date'] or 'еще не было'}\n\n"
            f"📋 Детальная статистика: `/question_stats`"
        )

    @dp.message_created(Command('question_stats'))
    async def show_question_stats(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        qa_list = get_user_qa(user_id)
        stats = get_user_stats(user_id)
        
        if not qa_list:
            await event.message.answer("📝 У тебя пока нет вопросов для статистики.")
            return
        
        text = "📋 **Статистика по вопросам:**\n\n"
        
        for i, qa in enumerate(qa_list[:10], 1):  # Показываем первые 10
            qa_id = qa.get('id', i)
            q_stats = get_question_stats(user_id, qa_id)
            
            times_asked = q_stats['times_asked']
            times_correct = q_stats['times_correct']
            
            if times_asked > 0:
                success_rate = (times_correct / times_asked) * 100
                success_emoji = "🟢" if success_rate >= 80 else "🟡" if success_rate >= 50 else "🔴"
                success_text = f"{success_rate:.0f}%"
            else:
                success_emoji = "⚪"
                success_text = "еще не задан"
            
            text += f"{success_emoji} **{qa['question']}**\n"
            text += f"   Успешность: {success_text} ({times_correct}/{times_asked})\n\n"
        
        if len(qa_list) > 10:
            text += f"*... и еще {len(qa_list) - 10} вопросов*\n\n"
        
        text += "💡 **Обозначения:**\n"
        text += "🟢 >80% 🟡 50-80% 🔴 <50% ⚪ не задавался"
        
        await event.message.answer(text)

    # --- Обработка обычных сообщений (ответы на вопросы) ---
    
    @dp.message_created()
    async def handle_regular_message(event: MessageCreated):
        # Игнорируем команды
        if event.message.text and event.message.text.startswith('/'):
            return

        user_id = str(event.from_user.user_id)
        current_qa = get_current_question(user_id)
        
        if not current_qa:
            # Не задан вопрос, можно показать подсказку
            settings = get_user_settings(user_id)
            if settings["active"]:
                await event.message.answer(
                    "💡 Я задам следующий вопрос в случайное время в твоем интервале.\n"
                    "А пока можешь добавить новые вопросы или посмотреть статистику!"
                )
            return

        user_answer = event.message.text.strip()
        correct_answer = current_qa['answer'].strip()
        
        # Простая проверка правильности (можно улучшить)
        is_correct = user_answer.lower() == correct_answer.lower()
        
        # Рассчитываем время ответа
        asked_at = datetime.fromisoformat(current_qa.get('asked_at', datetime.now().isoformat()))
        response_time = (datetime.now() - asked_at).total_seconds()
        
        # Обновляем статистику
        update_user_stats(
            user_id=user_id,
            question_id=current_qa.get('id'),
            correct=is_correct,
            response_time=response_time,
            quality=5 if is_correct and response_time < 30 else 3 if is_correct else 1
        )
        
        if is_correct:
            remove_current_question(user_id)
            await event.message.answer(
                "✅ **Правильно!** 🎉\n\n"
                f"**Вопрос:** {current_qa['question']}\n"
                f"**Твой ответ:** {user_answer}\n"
                f"⏱ Время: {response_time:.1f} сек\n\n"
                "Отличная работа! Следующий вопрос скоро."
            )
        else:
            # Оставляем вопрос активным для повторной попытки
            await event.message.answer(
                "❌ **Пока не верно.**\n\n"
                f"**Вопрос:** {current_qa['question']}\n"
                f"**Твой ответ:** {user_answer}\n\n"
                "Попробуй еще раз! 💪"
            )

    @dp.message_callback()
    async def message_callback(callback: MessageCallback):
        payload = callback.callback.payload  # ← ключевое изменение!

        # Создаём "фейковое" событие для совместимости с вашими командами
        class FakeEvent:
            def __init__(self, message, from_user, chat):
                self.message = message
                self.from_user = from_user
                self.chat = chat

        fake_event = FakeEvent(
            message=callback.message,
            from_user=callback.from_user,
            chat=callback.chat
        )

        match payload:
            case "main_menu":
                await callback.message.answer(
                    "🎯 Вы вернулись в главное меню.",
                    attachments=[get_main_menu_keyboard()]
                )

            case "my_qa":
                await show_my_qa(fake_event)

            case "add_qa_hint":
                @dp.dialog_cleared()
                async def dialog_cleared(event: DialogCleared):
                    print(event.from_user.full_name, 'очистил историю чата с ботом') # type: ignore

                

                await callback.message.answer(
                    "🎯 **Добро пожаловать в умную викторину!**\n"
                    "Я помогу тебе эффективно запоминать информацию с помощью "
                    "интервального повторения и адаптивного алгоритма.\n\n"
                    "Выбери действие в меню ниже 👇",
                    attachments=[get_main_menu_keyboard()]
                )
                
                await callback.message.answer(
                    "📝 Введите вопрос и ответ в формате:\n"
                    "`/add_qa Вопрос || Ответ`\n"
                    "**Пример:**\n"
                    "`/add_qa Столица Франции || Париж`",
                    attachments=[get_back_keyboard()]
                )

            case "start_quiz":
                await start_quiz(fake_event)

            case "stop_quiz":
                await stop_quiz(fake_event)

            case "settings":
                await show_settings(fake_event)

            case "stats":
                await show_stats(fake_event)
            
            case "help":
                await show_stats(fake_event)

            case _:
                await callback.message.answer("❓ Неизвестная команда.")
