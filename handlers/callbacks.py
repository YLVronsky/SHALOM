# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# callbacks.py

from maxapi.types import MessageCallback
from .base import BaseHandler
from utils.keyboards import KeyboardManager

class CallbackHandlers(BaseHandler):
    """Обработчики callback-ов от инлайн кнопок"""
    
    async def handle_callback(self, callback: MessageCallback):
        """Основной обработчик callback-ов"""
        payload = callback.callback.payload

        # Создаём "фейковое" событие для совместимости с обработчиками команд
        fake_event = self._create_fake_event(callback)

        match payload:
            case "main_menu":
                await self._main_menu(callback)
            case "my_qa":
                await self.commands.show_my_qa(fake_event)
            case "add_qa_hint":
                await self._add_qa_hint(callback)
            case "start_quiz":
                await self.commands.start_quiz(fake_event)
            case "stop_quiz":
                await self.commands.stop_quiz(fake_event)
            case "settings":
                await self.commands.show_settings(fake_event)
            case "stats":
                await self.commands.show_stats(fake_event)
            case "help":
                await self.commands.help_command(fake_event)
            case "confirm_reset_settings":
                await self.commands.confirm_reset_settings(fake_event)
            case "cancel_reset_settings":
                await self.commands.cancel_reset_settings(fake_event)
            case _:
                await callback.message.answer("❓ Неизвестная команда.")

    def _create_fake_event(self, callback):
        """Создает фейковое событие для совместимости с обработчиками команд"""
        class FakeUser:
            def __init__(self, user):
                self.user_id = getattr(user, "user_id", None) or getattr(user, "id", None)

        class FakeEvent:
            def __init__(self, message, from_user, chat):
                self.message = message
                self.from_user = from_user
                self.chat = chat

        return FakeEvent(
            message=callback.message,
            from_user=FakeUser(callback.from_user),
            chat=callback.chat
        )


    async def _main_menu(self, callback: MessageCallback):
        """Обработчик возврата в главное меню"""
        await callback.message.answer(
            "🎯 Вы вернулись в главное меню.",
            attachments=[KeyboardManager.get_main_menu_keyboard()]
        )

    async def _add_qa_hint(self, callback: MessageCallback):
        """Обработчик подсказки добавления вопроса"""
        await callback.message.answer(
            "📝 Введите вопрос и ответ в формате:\n"
            "`/add_qa Вопрос || Ответ`\n"
            "**Пример:**\n"
            "`/add_qa Столица Франции || Париж`",
            attachments=[KeyboardManager.get_back_keyboard()]
        )

    def set_command_handlers(self, commands):
        """Устанавливает ссылки на обработчики команд"""
        self.commands = commands