# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseniy

from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from maxapi.types import CallbackButton, LinkButton
from typing import List, Optional

class KeyboardManager:
    """Менеджер клавиатур для бота"""
    
    @staticmethod
    def get_main_menu_keyboard() -> dict:
        """Главное меню бота"""
        builder = InlineKeyboardBuilder()
        builder.row(
            CallbackButton(text="📚 Мои вопросы", payload="my_qa"),
            CallbackButton(text="➕ Добавить вопрос", payload="add_qa_hint")
        )
        builder.row(
            CallbackButton(text="▶️Запустить викторину", payload="start_quiz"),
            CallbackButton(text="⏹️Остановить викторину", payload="stop_quiz")
        )
        builder.row(
            CallbackButton(text="⚙️ Настройки", payload="settings"),
            CallbackButton(text="📊 Статистика", payload="stats")
        )
        builder.row(
            CallbackButton(text="❓ Помощь", payload="help")
        )
        return builder.as_markup()

    @staticmethod
    def get_back_keyboard() -> dict:
        """Клавиатура с кнопкой 'Назад'"""
        builder = InlineKeyboardBuilder()
        builder.row(CallbackButton(text="↩️ Назад в меню", payload="main_menu"))
        return builder.as_markup()

    @staticmethod
    def get_quiz_control_keyboard() -> dict:
        """Клавиатура управления викториной"""
        builder = InlineKeyboardBuilder()
        builder.row(
            CallbackButton(text="▶️ Запустить", payload="start_quiz"),
            CallbackButton(text="⏸️ Пауза", payload="pause_quiz")
        )
        builder.row(
            CallbackButton(text="⏹️ Остановить", payload="stop_quiz"),
            CallbackButton(text="⚙️ Настройки", payload="settings")
        )
        return builder.as_markup()

    @staticmethod
    def get_settings_keyboard() -> dict:
        """Клавиатура настроек"""
        builder = InlineKeyboardBuilder()
        builder.row(
            CallbackButton(text="Дневная цель", payload="set_daily"),
            CallbackButton(text="⏰ Интервал", payload="set_interval")
        )
        builder.row(
            CallbackButton(text="📅 Расписание", payload="set_schedule"),
            CallbackButton(text="🔄 Сбросить", payload="reset_settings")
        )
        builder.row(
            CallbackButton(text="↩️ Назад", payload="main_menu")
        )
        return builder.as_markup()

    @staticmethod
    def get_qa_management_keyboard() -> dict:
        """Клавиатура управления вопросами"""
        builder = InlineKeyboardBuilder()
        builder.row(
            CallbackButton(text="👀 Просмотреть", payload="my_qa"),
            CallbackButton(text="➕ Добавить", payload="add_qa_hint")
        )
        builder.row(
            CallbackButton(text="🗑 Очистить все", payload="clear_qa"),
            CallbackButton(text="↩️ Назад", payload="main_menu")
        )
        return builder.as_markup()

    @staticmethod
    def get_stats_keyboard() -> dict:
        """Клавиатура статистики"""
        builder = InlineKeyboardBuilder()
        builder.row(
            CallbackButton(text="📈 Общая", payload="stats"),
            CallbackButton(text="📊 По вопросам", payload="question_stats")
        )
        builder.row(
            CallbackButton(text="📋 Аналитика", payload="analytics"),
            CallbackButton(text="↩️ Назад", payload="main_menu")
        )
        return builder.as_markup()

    @staticmethod
    def get_yes_no_keyboard(yes_payload: str = "yes", no_payload: str = "no") -> dict:
        """Клавиатура Да/Нет"""
        builder = InlineKeyboardBuilder()
        builder.row(
            CallbackButton(text="✅ Да", payload=yes_payload),
            CallbackButton(text="❌ Нет", payload=no_payload)
        )
        return builder.as_markup()

    @staticmethod
    def get_schedule_days_keyboard() -> dict:
        """Клавиатура выбора дней недели для расписания"""
        builder = InlineKeyboardBuilder()
        builder.row(
            CallbackButton(text="Пн", payload="set_day_mon"),
            CallbackButton(text="Вт", payload="set_day_tue"),
            CallbackButton(text="Ср", payload="set_day_wed")
        )
        builder.row(
            CallbackButton(text="Чт", payload="set_day_thu"),
            CallbackButton(text="Пт", payload="set_day_fri"),
            CallbackButton(text="Сб", payload="set_day_sat")
        )
        builder.row(
            CallbackButton(text="Вс", payload="set_day_sun"),
            CallbackButton(text="↩️ Назад", payload="settings")
        )
        return builder.as_markup()

    @staticmethod
    def get_day_schedule_keyboard(day: str) -> dict:
        """Клавиатура настройки расписания для конкретного дня"""
        builder = InlineKeyboardBuilder()
        builder.row(
            CallbackButton(text="🕘 Утро", payload=f"set_time_{day}_morning"),
            CallbackButton(text="🕛 День", payload=f"set_time_{day}_day")
        )
        builder.row(
            CallbackButton(text="🕖 Вечер", payload=f"set_time_{day}_evening"),
            CallbackButton(text="❌ Выключить", payload=f"disable_day_{day}")
        )
        builder.row(
            CallbackButton(text="↩️ Назад к дням", payload="set_schedule")
        )
        return builder.as_markup()

    @staticmethod
    def get_pagination_keyboard(current_page: int, total_pages: int, 
                              prev_payload: str, next_payload: str,
                              back_payload: str = "main_menu") -> dict:
        """Клавиатура пагинации"""
        builder = InlineKeyboardBuilder()
        
        buttons = []
        if current_page > 1:
            buttons.append(CallbackButton(text="⬅️ Назад", payload=prev_payload))
        
        buttons.append(CallbackButton(text=f"{current_page}/{total_pages}", payload="current_page"))
        
        if current_page < total_pages:
            buttons.append(CallbackButton(text="Вперед ➡️", payload=next_payload))
        
        builder.row(*buttons)
        builder.row(CallbackButton(text="↩️ Назад", payload=back_payload))
        
        return builder.as_markup()

    @staticmethod
    def create_custom_keyboard(buttons: List[dict], columns: int = 2) -> dict:
        """
        Создает кастомную клавиатуру из списка кнопок
        
        Args:
            buttons: Список словарей с текстом и payload
            columns: Количество колонок
        """
        builder = InlineKeyboardBuilder()
        
        row = []
        for button in buttons:
            row.append(CallbackButton(text=button['text'], payload=button['payload']))
            
            if len(row) == columns:
                builder.row(*row)
                row = []
        
        if row: 
            builder.row(*row)
        
        return builder.as_markup()

    @staticmethod
    def get_quick_actions_keyboard() -> dict:
        """Клавиатура быстрых действий"""
        builder = InlineKeyboardBuilder()
        builder.row(
            CallbackButton(text="Викторина", payload="quick_quiz"),
            CallbackButton(text="📚 Вопросы", payload="quick_qa")
        )
        builder.row(
            CallbackButton(text="⚙️ Настройки", payload="quick_settings"),
            CallbackButton(text="📊 Статистика", payload="quick_stats")
        )
        return builder.as_markup()