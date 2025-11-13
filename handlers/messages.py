# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny

import logging
from datetime import datetime
from maxapi.types import MessageCreated
from .base import BaseHandler

class MessageHandlers(BaseHandler):
    """Обработчики обычных сообщений"""
    
    async def handle_regular_message(self, event: MessageCreated):
        """Обработчик обычных сообщений (ответы на вопросы)"""
        msg = event.message

        text = (msg.body.text or "").strip()
        if text.startswith("/") or getattr(msg, "command", None):
            logging.debug("Пропущено сообщение-команда: %r", text)
            return


        user_id = str(event.from_user.user_id)
        current_qa = self.storage.get_current_question(user_id)
        
        if not current_qa:

            settings = self.storage.get_user_settings(user_id)
            if settings["active"]:
                await event.message.answer(
                    "Я задам следующий вопрос в случайное время в твоем интервале.\n"
                    "А пока можешь добавить новые вопросы или посмотреть статистику!"
                )
            return

        user_answer = event.message.body.text.strip()
        correct_answer = current_qa['answer'].strip()

        is_correct = user_answer.lower() == correct_answer.lower()

        asked_at = datetime.fromisoformat(current_qa.get('asked_at', datetime.now().isoformat()))
        response_time = (datetime.now() - asked_at).total_seconds()

        self.storage.update_user_stats(
            user_id=user_id,
            question_id=current_qa.get('id'),
            correct=is_correct,
            response_time=response_time,
            quality=5 if is_correct and response_time < 30 else 3 if is_correct else 1
        )
        
        if is_correct:
            self.storage.remove_current_question(user_id)
            await event.message.answer(
                "✅ Правильно!\n\n"
                f"Вопрос: {current_qa['question']}\n"
                f"Твой ответ: {user_answer}\n"
                f"Время: {response_time:.1f} сек\n\n"
                "Отличная работа! Следующий вопрос скоро."
            )
        else:
            await event.message.answer(
                "❌ Пока не верно.\n\n"
                f"Вопрос: {current_qa['question']}\n"
                f"Твой ответ: {user_answer}\n\n"
                "Попробуй еще раз!"
            )