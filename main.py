# Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений
# main.py

import asyncio
import logging
import signal
from maxapi import Bot, Dispatcher
from quiz_manager import QuizManager
from handlers import register_handlers
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# --- Инициализация ---

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
quiz_manager = QuizManager(bot)

# Регистрация всех обработчиков
register_handlers(dp, quiz_manager)

# --- Запуск и завершение работы ---

async def shutdown():
    """Корректное завершение работы."""
    logging.info("Остановка бота...")
    # Остановка всех активных викторин
    for user_id in list(quiz_manager.active_users):
        quiz_manager.stop_quiz_for_user(user_id)
    logging.info("Викторины остановлены. Бот завершил работу.")

async def main():
    """Главная функция запуска бота."""
    try:
        logging.info("Бот запущен. Ожидание событий...")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        pass # Обработаем в finally
    except Exception as e:
        logging.error(f"Bot error: {e}")
    finally:
        await shutdown()

if __name__ == '__main__':
    # Обработка сигнала прерывания (Ctrl+C)
    signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(shutdown()))
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Это может произойти, если Ctrl+C нажат до async.run

        pass
