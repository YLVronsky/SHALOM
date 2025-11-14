<<<<<<< HEAD
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseniy
=======
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a

from maxapi import Dispatcher
from maxapi.types import Command
from .commands import CommandHandlers
from .callbacks import CallbackHandlers
from .messages import MessageHandlers
from .settings import SettingsHandlers
from .stats import StatsHandlers

def register_handlers(dp: Dispatcher, quiz_manager, storage):
    """Регистрирует все обработчики в диспетчере"""
    
    commands = CommandHandlers(quiz_manager, storage)
    callbacks = CallbackHandlers(quiz_manager, storage)
    messages = MessageHandlers(quiz_manager, storage)
    settings = SettingsHandlers(quiz_manager, storage)
    stats = StatsHandlers(quiz_manager, storage)
    
    callbacks.set_command_handlers(commands)

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
    
    dp.message_created(Command('settings'))(settings.show_settings)
    dp.message_created(Command('set_schedule'))(settings.set_schedule_command)
    dp.message_created(Command('set_day'))(settings.set_day_schedule)
    dp.message_created(Command('reset_settings'))(settings.reset_settings)
    
    dp.message_created(Command('stats'))(stats.show_stats)
    dp.message_created(Command('question_stats'))(stats.show_question_stats)
    
    dp.message_created()(messages.handle_regular_message)
    dp.message_callback()(callbacks.handle_callback)