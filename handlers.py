# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# handlers.py

import asyncio
from maxapi import Dispatcher
from maxapi.types import MessageCreated, Command
from quiz_manager import QuizManager
from storage import (
    save_user_qa, get_user_qa, user_qa_file, 
    get_current_question, remove_current_question
)

def register_handlers(dp: Dispatcher, quiz_manager: QuizManager):
    """Регистрирует все обработчики сообщений и команд."""

    # --- Команды ---

    @dp.message_created(Command('start'))
    async def start_command(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        # Инициализируем файл, если его нет
        if not user_qa_file(user_id).exists():
            save_user_qa(user_id, [])
        await event.message.answer(
            "🎯 Добро пожаловать в бот-викторину!\n\n"
            "Доступные команды:\n"
            "/add_qa - добавить вопрос-ответ\n"
            "/my_qa - посмотреть свои вопросы\n"
            "/start_quiz - запустить викторину\n"
            "/stop_quiz - остановить викторину\n"
            "/clear_qa - очистить все вопросы\n"
            "/stats - показать статистику"
        )

    @dp.message_created(Command('add_qa'))
    async def add_qa_pair(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        text = event.message.body.text
        if '||' not in text:
            await event.message.answer("❌ Используй: /add_qa Вопрос || Ответ")
            return

        parts = text.split('||', 1)
        question = parts[0].replace('/add_qa', '').strip()
        answer = parts[1].strip()

        if not question or not answer:
            await event.message.answer("❌ Вопрос и ответ не могут быть пустыми")
            return

        qa_list = get_user_qa(user_id)
        qa_list.append({"question": question, "answer": answer})
        save_user_qa(user_id, qa_list)
        await event.message.answer(f"✅ Добавлен вопрос: **{question}**")

    @dp.message_created(Command('my_qa'))
    async def show_my_qa(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        qa_list = get_user_qa(user_id)
        if not qa_list:
            await event.message.answer("📝 У тебя пока нет вопросов.")
            return

        text = "📚 Твои вопросы:\n\n"
        for i, qa in enumerate(qa_list, 1):
            text += f"{i}. ❓ **{qa['question']}**\n   💡 Ответ: {qa['answer']}\n\n"

        # Разбивка на части
        for part in [text[i:i+4000] for i in range(0, len(text), 4000)]:
            await event.message.answer(part)

    @dp.message_created(Command('clear_qa'))
    async def clear_qa(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        quiz_manager.stop_quiz_for_user(user_id) # Останавливаем викторину, если активна
        save_user_qa(user_id, [])
        await event.message.answer("🗑 Все вопросы очищены. Викторина остановлена.")

    @dp.message_created(Command('stats'))
    async def show_stats(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        qa_count = len(get_user_qa(user_id))
        active_status = "активна" if user_id in quiz_manager.active_users else "остановлена"
        next_question_time = "5 минут" if user_id in quiz_manager.active_users else "—"
        await event.message.answer(
            f"📊 **Статистика**:\n"
            f"• Вопросов: **{qa_count}**\n"
            f"• Викторина: **{active_status}**\n"
            f"• Следующий вопрос через: {next_question_time}"
        )

    @dp.message_created(Command('start_quiz'))
    async def start_quiz(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        chat_id = event.chat.chat_id
        if not get_user_qa(user_id):
            await event.message.answer("❌ Сначала добавь вопросы через /add_qa")
            return
        
        if user_id in quiz_manager.active_users:
            await event.message.answer("ℹ️ Викторина уже запущена!")
            return

        # Запускаем задачу в фоновом режиме
        asyncio.create_task(quiz_manager.start_quiz_for_user(user_id, chat_id))
        
        await event.message.answer(
            "🎯 **Викторина запущена!** Каждые 5 минут я буду задавать случайный вопрос.\n"
            "Чтобы остановить: /stop_quiz"
        )

    @dp.message_created(Command('stop_quiz'))
    async def stop_quiz(event: MessageCreated):
        user_id = str(event.from_user.user_id)
        if user_id not in quiz_manager.active_users:
            await event.message.answer("ℹ️ Викторина и так остановлена.")
            return

        quiz_manager.stop_quiz_for_user(user_id)
        await event.message.answer("⏹ **Викторина остановлена**")

    # --- Обработка обычных сообщений (ответы) ---
    
    @dp.message_created()
    async def handle_regular_message(event: MessageCreated):
        # Игнорируем команды
        if event.message.text and event.message.text.startswith('/'):
            return

        user_id = str(event.from_user.user_id)
        current = get_current_question(user_id)
        
        if not current:
            # Не задан вопрос, игнорируем
            return

        user_answer = event.message.text.strip().lower()
        correct = current['answer'].strip().lower()

        # Очень простая проверка: полное совпадение
        if user_answer == correct:
            await event.message.answer("✅ **Правильно!** 🎉")
            remove_current_question(user_id)
        else:
            # Опционально: можно дать подсказку или просто игнорировать

            await event.message.answer("❌ Неверно. Попробуй ещё раз.")
