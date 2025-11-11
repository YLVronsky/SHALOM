# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# __init__.py

from maxapi import Dispatcher
from maxapi.types import Command
from .commands import CommandHandlers
from .callbacks import CallbackHandlers
from .messages import MessageHandlers
from .settings import SettingsHandlers
from .stats import StatsHandlers

def register_handlers(dp: Dispatcher, quiz_manager, storage):
    """Регистрирует все обработчики в диспетчере"""
    
    # Создаем экземпляры обработчиков
    commands = CommandHandlers(quiz_manager, storage)
    callbacks = CallbackHandlers(quiz_manager, storage)
    messages = MessageHandlers(quiz_manager, storage)
    settings = SettingsHandlers(quiz_manager, storage)
    stats = StatsHandlers(quiz_manager, storage)
    
    # Настраиваем зависимости между обработчиками
    callbacks.set_command_handlers(commands)
    commands.set_other_handlers(settings, stats)

    # Регистрируем обработчики команд
    dp.message_created(Command('start'))(commands.start_command)
    dp.message_created(Command('help'))(commands.help_command)
    dp.message_created(Command('add_qa'))(commands.add_qa_pair)
    dp.message_created(Command('my_qa'))(commands.show_my_qa)
    dp.message_created(Command('remove_qa'))(commands.remove_qa_command)
    dp.message_created(Command('clear_qa'))(commands.clear_qa)
    dp.message_created(Command('start_quiz'))(commands.start_quiz)
    dp.message_created(Command('stop_quiz'))(commands.stop_quiz)
    dp.message_created(Command('set_daily'))(commands.set_daily_goal)
    dp.message_created(Command('set_interval'))(commands.set_interval)
    
    # Регистрируем обработчики настроек
    dp.message_created(Command('settings'))(settings.show_settings)
    dp.message_created(Command('set_schedule'))(settings.set_schedule_command)
    dp.message_created(Command('set_day'))(settings.set_day_schedule)
    dp.message_created(Command('reset_settings'))(settings.reset_settings)
    
    # Регистрируем обработчики статистики
    dp.message_created(Command('stats'))(stats.show_stats)
    dp.message_created(Command('question_stats'))(stats.show_question_stats)
    
    # Регистрируем обработчики сообщений и callback-ов
    dp.message_created()(messages.handle_regular_message)
    dp.message_callback()(callbacks.handle_callback)