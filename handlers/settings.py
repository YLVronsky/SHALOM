# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# settings.py

import re
from maxapi.types import MessageCreated
from .base import BaseHandler, MessageFormatter
from utils.keyboards import KeyboardManager
from utils.validators import Validators
import datetime

class SettingsHandlers(BaseHandler):
    """Обработчики команд настроек"""
    
    async def show_settings(self, event: MessageCreated):
        """Обработчик команды /settings"""
        user_id = str(event.from_user.user_id)
        settings = self.storage.get_user_settings(user_id)
        stats = self.storage.get_user_stats(user_id)
        qa_count = len(self.storage.get_user_qa(user_id))
        
        formatted_message = MessageFormatter.format_settings_message(settings, stats, qa_count)
        await event.message.answer(formatted_message)

    async def set_daily_goal(self, event: MessageCreated):
        """Обработчик команды /set_daily с валидацией"""
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        parts = text.split()
        if len(parts) < 2:
            await event.message.answer(
                "❌ **Неверный формат!**\n\n"
                "Используй: `/set_daily <число>`\n\n"
                "**Пример:** `/set_daily 15`\n"
                "Это установит цель в 15 вопросов в день."
            )
            return
        
        goal_str = parts[1]
        
        # Валидируем дневную цель
        is_valid, error_msg, goal_value = Validators.validate_daily_goal(goal_str)
        
        if not is_valid:
            await event.message.answer(f"❌ **{error_msg}**")
            return
        
        settings = self.storage.get_user_settings(user_id)
        old_goal = settings["daily_goal"]
        self.storage.update_user_settings(user_id, daily_goal=goal_value)
        
        await event.message.answer(
            f"✅ **Дневная цель изменена!**\n\n"
            f"• Было: **{old_goal}** вопросов в день\n"
            f"• Стало: **{goal_value}** вопросов в день\n\n"
            f"📊 Вопросов сегодня: {settings['questions_today']}/{goal_value}"
        )

    async def set_interval(self, event: MessageCreated):
        """Обработчик команды /set_interval с валидацией"""
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        parts = text.split()
        if len(parts) < 3:
            await event.message.answer(
                "❌ **Неверный формат!**\n\n"
                "Используй: `/set_interval <мин> <макс>`\n\n"
                "**Пример:** `/set_interval 30 120`\n"
                "Это установит интервал от 30 до 120 минут между вопросами."
            )
            return
        
        min_str = parts[1]
        max_str = parts[2]
        
        # Валидируем интервал
        is_valid, error_msg, interval_data = Validators.validate_interval(min_str, max_str)
        
        if not is_valid:
            await event.message.answer(f"❌ **{error_msg}**")
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
            f"✅ **Интервал изменен!**\n\n"
            f"• Было: **{old_min} - {old_max}** минут\n"
            f"• Стало: **{interval_data['min']} - {interval_data['max']}** минут\n\n"
            f"⏰ Вопросы будут приходить случайно в этом интервале."
        )

    async def set_schedule_command(self, event: MessageCreated):
        """Обработчик команды /set_schedule"""
        user_id = str(event.from_user.user_id)
        settings = self.storage.get_user_settings(user_id)
        
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
        
        # Проверяем покрытие расписания
        coverage = Validators.calculate_schedule_coverage(settings["schedule"])
        
        instructions = (
            f"\n📊 **Покрытие расписания:**\n"
            f"• Активных дней: {coverage['enabled_days']}/7\n"
            f"• Часов в неделю: {coverage['total_hours_per_week']:.1f}\n"
            f"• Покрытие: {coverage['coverage_percentage']:.1f}%\n\n"
            "🔧 **Как изменить расписание:**\n\n"
            "Используй команду:\n"
            "`/set_day <день> <начало> <конец> <вкл/выкл>`\n\n"
            "**Параметры:**\n"
            "• `<день>`: mon, tue, wed, thu, fri, sat, sun\n"
            "• `<начало>`, `<конец>`: время в формате HH:MM\n"
            "• `<вкл/выкл>`: on или off\n\n"
            "**Примеры:**\n"
            "• `/set_day mon 09:00 18:00 on`\n"
            "• `/set_day sat 10:00 16:00 off`\n"
            "• `/set_day sun 00:00 00:00 off` - отключить день\n\n"
            "💡 **Совет:** Старайтесь охватить все дни, когда вы обычно активны!"
        )
        
        await event.message.answer(schedule_text + instructions)

    async def set_day_schedule(self, event: MessageCreated):
        """Обработчик команды /set_day"""
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        try:
            parts = text.split()
            day_short = parts[1].lower()
            start_time = parts[2]
            end_time = parts[3]
            enabled = parts[4].lower()
            
            # Валидируем параметры
            is_valid, error_msg, schedule_data = Validators.validate_day_schedule_params(
                day_short, start_time, end_time, enabled
            )
            
            if not is_valid:
                await event.message.answer(f"❌ {error_msg}")
                return
            
            # Обновляем настройки
            settings = self.storage.get_user_settings(user_id)
            settings["schedule"][schedule_data["day_en"]] = {
                "start": schedule_data["start_time"],
                "end": schedule_data["end_time"],
                "enabled": schedule_data["enabled"]
            }
            self.storage.save_user_settings(user_id, settings)
            
            # Проверяем согласованность расписания после изменения
            schedule_valid, schedule_error = Validators.validate_schedule_time_consistency(settings["schedule"])
            if not schedule_valid:
                warning_msg = f"\n\n⚠️ **Внимание:** {schedule_error}"
            else:
                warning_msg = ""
            
            status = "включен" if schedule_data["enabled"] else "отключен"
            await event.message.answer(
                f"✅ **Расписание обновлено!**\n\n"
                f"**{schedule_data['day_ru']}** {status}\n"
                f"Время: {schedule_data['start_time']} - {schedule_data['end_time']}"
                f"{warning_msg}\n\n"
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

    async def reset_settings(self, event: MessageCreated):
        """Обработчик команды /reset_settings"""
        user_id = str(event.from_user.user_id)
        
        # Создаем клавиатуру подтверждения
        confirmation_keyboard = KeyboardManager.get_yes_no_keyboard(
            yes_payload="confirm_reset_settings",
            no_payload="cancel_reset_settings"
        )
        
        await event.message.answer(
            "🔄 **Сброс настроек**\n\n"
            "Вы уверены, что хотите сбросить все настройки к значениям по умолчанию?\n\n"
            "Это действие:\n"
            "• Остановит активную викторину\n"
            "• Сбросит все ваши настройки\n"
            "• Не затронет ваши вопросы и статистику\n\n"
            "Подтвердите действие:",
            attachments=[confirmation_keyboard]
        )

    async def confirm_reset_settings(self, user_id: str, chat_id: str):
        """Подтверждение сброса настроек"""
        # Останавливаем викторину
        self.quiz_manager.stop_quiz_for_user(user_id)
        
        # Сбрасываем настройки к значениям по умолчанию
        default_settings = self.storage.get_default_settings()
        self.storage.save_user_settings(user_id, default_settings)
        
        await self.bot.send_message(
            chat_id=chat_id,
            text=(
                "🔄 **Настройки сброшены!**\n\n"
                "Все настройки возвращены к значениям по умолчанию.\n"
                "Викторина остановлена.\n\n"
                "📋 **Новые настройки:**\n"
                f"• Дневная цель: **{default_settings['daily_goal']}** вопросов\n"
                f"• Интервал: **{default_settings['min_interval']}-{default_settings['max_interval']}** минут\n"
                f"• Активных дней: **{len([d for d in default_settings['schedule'].values() if d['enabled']])}**\n\n"
                "Посмотреть настройки: `/settings`\n"
                "Настроить заново: `/set_schedule`"
            )
        )

    async def cancel_reset_settings(self, user_id: str, chat_id: str):
        """Отмена сброса настроек"""
        await self.bot.send_message(
            chat_id=chat_id,
            text="❌ **Сброс настроек отменен.**\n\nТекущие настройки сохранены."
        )

    async def show_schedule_analysis(self, event: MessageCreated):
        """Показывает анализ текущего расписания"""
        user_id = str(event.from_user.user_id)
        settings = self.storage.get_user_settings(user_id)
        
        coverage = Validators.calculate_schedule_coverage(settings["schedule"])
        
        days_ru = {
            'monday': 'Понедельник',
            'tuesday': 'Вторник', 
            'wednesday': 'Среда',
            'thursday': 'Четверг',
            'friday': 'Пятница',
            'saturday': 'Суббота',
            'sunday': 'Воскресенье'
        }
        
        analysis_text = "📊 **Анализ расписания:**\n\n"
        
        # Общая статистика
        analysis_text += f"• Активных дней: **{coverage['enabled_days']}/7**\n"
        analysis_text += f"• Часов в неделю: **{coverage['total_hours_per_week']:.1f}**\n"
        analysis_text += f"• Покрытие: **{coverage['coverage_percentage']:.1f}%**\n\n"
        
        # Рекомендации
        if coverage['enabled_days'] < 3:
            analysis_text += "⚠️ **Рекомендация:** Мало активных дней. Добавьте больше дней для лучших результатов обучения.\n\n"
        elif coverage['total_hours_per_week'] < 20:
            analysis_text += "⚠️ **Рекомендация:** Небольшое общее время. Увеличьте продолжительность активных периодов.\n\n"
        else:
            analysis_text += "✅ **Отличное расписание!** Продолжайте в том же духе.\n\n"
        
        # Детали по дням
        analysis_text += "📅 **Детали по дням:**\n"
        for day_en, day_ru in days_ru.items():
            schedule = settings["schedule"][day_en]
            status = "✅" if schedule["enabled"] else "❌"
            
            if schedule["enabled"]:
                start = datetime.strptime(schedule["start"], "%H:%M")
                end = datetime.strptime(schedule["end"], "%H:%M")
                duration = (end - start).seconds / 3600
                analysis_text += f"{status} **{day_ru}**: {schedule['start']}-{schedule['end']} ({duration:.1f} ч)\n"
            else:
                analysis_text += f"{status} **{day_ru}**: отключен\n"
        
        await event.message.answer(analysis_text)

    async def set_quick_schedule(self, event: MessageCreated):
        """Быстрая настройка расписания по шаблонам"""
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        
        templates = {
            "workdays": {
                "name": "Рабочие дни",
                "schedule": {
                    "monday": {"start": "09:00", "end": "18:00", "enabled": True},
                    "tuesday": {"start": "09:00", "end": "18:00", "enabled": True},
                    "wednesday": {"start": "09:00", "end": "18:00", "enabled": True},
                    "thursday": {"start": "09:00", "end": "18:00", "enabled": True},
                    "friday": {"start": "09:00", "end": "18:00", "enabled": True},
                    "saturday": {"start": "10:00", "end": "16:00", "enabled": True},
                    "sunday": {"start": "10:00", "end": "16:00", "enabled": True}
                }
            },
            "weekend": {
                "name": "Только выходные", 
                "schedule": {
                    "monday": {"start": "09:00", "end": "18:00", "enabled": False},
                    "tuesday": {"start": "09:00", "end": "18:00", "enabled": False},
                    "wednesday": {"start": "09:00", "end": "18:00", "enabled": False},
                    "thursday": {"start": "09:00", "end": "18:00", "enabled": False},
                    "friday": {"start": "09:00", "end": "18:00", "enabled": False},
                    "saturday": {"start": "10:00", "end": "20:00", "enabled": True},
                    "sunday": {"start": "10:00", "end": "20:00", "enabled": True}
                }
            },
            "everyday": {
                "name": "Каждый день",
                "schedule": {
                    "monday": {"start": "08:00", "end": "22:00", "enabled": True},
                    "tuesday": {"start": "08:00", "end": "22:00", "enabled": True},
                    "wednesday": {"start": "08:00", "end": "22:00", "enabled": True},
                    "thursday": {"start": "08:00", "end": "22:00", "enabled": True},
                    "friday": {"start": "08:00", "end": "22:00", "enabled": True},
                    "saturday": {"start": "09:00", "end": "23:00", "enabled": True},
                    "sunday": {"start": "09:00", "end": "23:00", "enabled": True}
                }
            }
        }
        
        parts = text.split()
        if len(parts) < 2:
            # Показываем доступные шаблоны
            template_keyboard = KeyboardManager.create_custom_keyboard([
                {"text": "🏢 Рабочие дни", "payload": "template_workdays"},
                {"text": "🎉 Выходные", "payload": "template_weekend"},
                {"text": "📅 Каждый день", "payload": "template_everyday"}
            ], columns=2)
            
            await event.message.answer(
                "🚀 **Быстрая настройка расписания**\n\n"
                "Выберите готовый шаблон:\n\n"
                "• **🏢 Рабочие дни** - пн-пт 9:00-18:00, сб-вс 10:00-16:00\n"
                "• **🎉 Выходные** - только сб-вс 10:00-20:00\n"
                "• **📅 Каждый день** - ежедневно 8:00-22:00 (сб-вс до 23:00)\n\n"
                "Или настройте вручную: `/set_schedule`",
                attachments=[template_keyboard]
            )
            return
        
        template_name = parts[1].lower()
        if template_name not in templates:
            await event.message.answer(
                "❌ **Неизвестный шаблон!**\n\n"
                "Доступные шаблоны: workdays, weekend, everyday\n\n"
                "**Пример:** `/quick_schedule workdays`"
            )
            return
        
        template = templates[template_name]
        settings = self.storage.get_user_settings(user_id)
        settings["schedule"] = template["schedule"]
        self.storage.save_user_settings(user_id, settings)
        
        coverage = Validators.calculate_schedule_coverage(settings["schedule"])
        
        await event.message.answer(
            f"✅ **Шаблон '{template['name']}' применен!**\n\n"
            f"📊 **Новое расписание:**\n"
            f"• Активных дней: **{coverage['enabled_days']}/7**\n"
            f"• Часов в неделю: **{coverage['total_hours_per_week']:.1f}**\n\n"
            f"Посмотреть расписание: `/set_schedule`\n"
            f"Настроить детально: `/set_day`"
        )

    def set_bot(self, bot):
        """Устанавливает ссылку на бота для отправки сообщений"""
        self.bot = bot