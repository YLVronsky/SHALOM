# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# quiz_manager.py

import asyncio
import logging
import random
from maxapi import Bot
from storage import get_user_qa, save_current_question, remove_current_question

# Класс менеджера викторины, требует Bot при инициализации
class QuizManager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_users = set()
    
    async def start_quiz_for_user(self, user_id: str, chat_id: str):
        """Запускает цикл викторины для конкретного пользователя."""
        if user_id in self.active_users:
            logging.info(f"Quiz already running for user {user_id}")
            return

        self.active_users.add(user_id)
        logging.info(f"Quiz started for user {user_id} in chat {chat_id}")

        while user_id in self.active_users:
            await asyncio.sleep(3)  # 5 минут (замените на 3 для тестирования)
            
            if user_id not in self.active_users:
                break

            qa_list = get_user_qa(user_id)
            if not qa_list:
                try:
                    await self.bot.send_message(
                        chat_id=chat_id, 
                        text="📝 У тебя нет вопросов. Добавь через /add_qa"
                    )
                except Exception as e:
                    logging.error(f"Failed to notify user {user_id}: {e}")
                await asyncio.sleep(60)  # Пауза, чтобы не спамить
                continue

            qa = random.choice(qa_list)
            save_current_question(user_id, qa)
            try:
                await self.bot.send_message(
                    chat_id=chat_id, 
                    text=f"❓ Вопрос: {qa['question']}"
                )
                logging.info(f"Sent question to {user_id}: {qa['question']}")
            except Exception as e:
                logging.error(f"Error sending question to {user_id}: {e}")

    def stop_quiz_for_user(self, user_id: str):
        """Останавливает цикл викторины для пользователя."""
        self.active_users.discard(user_id)
        remove_current_question(user_id)

        logging.info(f"Quiz stopped for user {user_id}")
