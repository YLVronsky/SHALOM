<<<<<<< HEAD
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseniy
=======
# Copyright (c) 2025 Solovev Ivan, Usenko Evgeny, Alexandrov Arseny
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a

from maxapi.types import MessageCreated
from .base import BaseHandler
from datetime import datetime

class StatsHandlers(BaseHandler):
    """Обработчики статистики"""
    
    async def show_stats(self, event: MessageCreated):
        """Обработчик команды /stats"""
        user_id = str(event.from_user.user_id)
        stats = self.storage.get_user_stats(user_id)
        settings = self.storage.get_user_settings(user_id)
        qa_count = len(self.storage.get_user_qa(user_id))
<<<<<<< HEAD
        
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        total_answered = stats['total_questions_answered']
        if total_answered > 0:
            correct_percent = (stats['correct_answers'] / total_answered) * 100
            avg_response_time = stats['average_response_time']
        else:
            correct_percent = 0
            avg_response_time = 0
<<<<<<< HEAD
        
=======

>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        if avg_response_time < 60:
            time_text = f"{avg_response_time:.1f} сек"
        else:
            time_text = f"{avg_response_time/60:.1f} мин"
        
        await event.message.answer(
<<<<<<< HEAD
            "📊 Твоя статистика:\n\n"
=======
            "Твоя статистика:\n\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            f"Обучение:\n"
            f"• Всего вопросов: {qa_count}\n"
            f"• Вопросов сегодня: {settings['questions_today']}/{settings['daily_goal']}\n"
            f"• Статус: {'🟢 Активно' if settings['active'] else '🔴 Остановлено'}\n\n"
<<<<<<< HEAD
            f"📈 Результаты:\n"
=======
            f"Результаты:\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            f"• Всего ответов: {total_answered}\n"
            f"• Правильных: {stats['correct_answers']} ({correct_percent:.1f}%)\n"
            f"• Текущая серия: {stats['current_streak']}\n"
            f"• Лучшая серия: {stats['best_streak']}\n"
            f"• Среднее время: {time_text}\n\n"
<<<<<<< HEAD
            f"⏱ Время обучения:\n"
=======
            f"Время обучения:\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
            f"• Всего: {stats['total_study_time_minutes']} минут\n"
            f"• Последнее: {datetime.fromisoformat(stats['last_study_date']).strftime('%d/%m/%Y, %H:%M') if stats.get('last_study_date') else 'еще не было'}\n\n"
            f" Детальная статистика: `/question_stats`"
        )

    async def show_question_stats(self, event: MessageCreated):
        """Обработчик команды /question_stats"""
        user_id = str(event.from_user.user_id)
        qa_list = self.storage.get_user_qa(user_id)
        stats = self.storage.get_user_stats(user_id)
        
        if not qa_list:
            await event.message.answer("У тебя пока нет вопросов для статистики.")
            return
        
<<<<<<< HEAD
        text = "📋 Статистика по вопросам:\n\n"
=======
        text = "Статистика по вопросам:\n\n"
>>>>>>> 03f41298ba6604709d3ff96baf73c3790ba5f30a
        
        for i, qa in enumerate(qa_list[:10], 1):
            qa_id = qa.get('id', i)
            q_stats = self.storage.get_question_stats(user_id, qa_id)
            
            times_asked = q_stats['times_asked']
            times_correct = q_stats['times_correct']
            
            if times_asked > 0:
                success_rate = (times_correct / times_asked) * 100
                success_emoji = "🟢" if success_rate >= 80 else "🟡" if success_rate >= 50 else "🔴"
                success_text = f"{success_rate:.0f}%"
            else:
                success_emoji = "⚪"
                success_text = "еще не задан"
            
            text += f"{success_emoji} {qa['question']}\n"
            text += f"   Успешность: {success_text} ({times_correct}/{times_asked})\n\n"
        
        if len(qa_list) > 10:
            text += f"*... и еще {len(qa_list) - 10} вопросов*\n\n"
        
        text += "💡 Обозначения:\n"
        text += "🟢 >80% 🟡 50-80% 🔴 <50% ⚪ не задавался"
        
        await event.message.answer(text)