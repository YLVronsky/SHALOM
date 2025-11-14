<<<<<<< HEAD
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseniy
=======
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a

import asyncio
from maxapi import Bot, Dispatcher
from services import Storage, QuizManager, AnalyticsService
from core.config import config
<<<<<<< HEAD
from core.logger import logger 
=======
from core.logger import logger
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a

async def shutdown(quiz_manager: QuizManager):
    """Корректное завершение работы."""
    logger.info("Остановка бота...")
    for user_id in list(quiz_manager.active_users):
        quiz_manager.stop_quiz_for_user(user_id)
    logger.info("Викторины остановлены. Бот завершил работу.")

async def main():
    """Главная функция запуска бота."""
    try:
        logger.info("Инициализация сервисов...")
        
        storage = Storage()
        bot = Bot(config.bot.token)
        quiz_manager = QuizManager(bot, storage)
        analytics = AnalyticsService(storage)
        
        dp = Dispatcher()
        
<<<<<<< HEAD
=======
        # Импорт и регистрация обработчиков
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        from handlers import register_handlers
        register_handlers(dp, quiz_manager, storage)
        
        logger.info("Бот запущен. Ожидание событий...")
        await bot.delete_webhook()
        await dp.start_polling(bot)

    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"Bot error: {e}")
    finally:
        if 'quiz_manager' in locals():
            await shutdown(quiz_manager)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")