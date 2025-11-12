# S.H.A.L.O.M. — Помощник для запоминания Теорий по кривой Эббингауза

**Кратко.**  
Проект команды **S.H.A.L.O.M.**, представляющий собой асинхронного Max-бота помощника, созданного для **закрепления знаний и повторения теорий по кривой Эббингауза**.  
Бот помогает пользователю повторять материал с адаптивной периодичностью, анализировать прогресс и формировать устойчивую память.

---

## Основные возможности
- Добавление собственных пар **вопрос–ответ** для запоминания.  
- Автоматическое напоминание и повторение, спомощью алгоритма основанного на **кривой Эббингауза** и **SuperMemo2**.  
- Статистика ответов, дневные цели и гибкое расписание повторений.  
- Полная локальная работа: все данные хранятся в папке `bot_data`.  
- Настройка интервалов и планирования прямо из чата.

---

## Требования
- **Python 3.11.0**  
- Установленные зависимости (см. `requirements.txt`)  
- (Опционально) **Docker** для контейнерного запуска

---

## Быстрый старт (локально)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/YLVronsky/SHALOM
   cd SHALOM
   ```

2. Создайте виртуальное окружение и установите зависимости

3. Создайте `.env` в корне проекта и укажите токен:
   ```bash
   BOT_TOKEN=123456:ABC-DEF...
   ```

4. Запустите бота:
   ```bash
   python main.py
   ```

---

## Запуск в Docker

```bash
docker build -t shalom-bot .
docker run -d --name shalom-bot shalom-bot
docker stop shalom-bot
```

---

## Переменные окружения

| Переменная | Описание |
|-------------|-----------|
| `BOT_TOKEN` | Токен Telegram-бота (обязательно) |
| `DATA_DIR` | Каталог хранения данных (`bot_data` по умолчанию) |
| `EMPTY_QA_INTERVAL` | Интервал по умолчанию между вопросами |
| `BOT_VERSION` | Текущая версия проекта |

Пример `.env`:
```
BOT_TOKEN=123456:ABC-DEF...
DATA_DIR=bot_data
EMPTY_QA_INTERVAL=60
BOT_VERSION=0.4.0
```

---

## Команды

| Команда | Описание |
|----------|-----------|
| `/start` | Приветствие и инициализация пользователя |
| `/add_qa <вопрос> || <ответ>` | Добавить новую пару вопрос–ответ |
| `/my_qa` | Показать свои Q/A |
| `/remove_qa <ID>` | Удалить вопрос по ID |
| `/clear_qa` | Очистить все свои вопросы |
| `/start_quiz` | Начать опрос |
| `/stop_quiz` | Остановить опрос |
| `/set_daily <число>` | Задать дневную цель |
| `/set_interval <мин> <макс>` | Настроить интервалы между вопросами |
| `/set_schedule`, `/set_day` | Настроить расписание |
| `/reset_settings` | Сбросить настройки |
| `/stats` | Общая статистика |
| `/question_stats` | Детальная статистика по вопросам |

---

## Структура проекта
```
SHALOM/
├─ main.py
├─ README.md
├─ core/
│  ├─ config.py
│  └─ logger.py
├─ handlers/
│  ├─ commands.py
│  ├─ settings.py
│  ├─ stats.py
│  ├─ callbacks.py
│  └─ messages.py
├─ services/
│  ├─ storage.py
│  ├─ quiz_manager.py
│  └─ analytics.py
├─ utils/
│  ├─ keyboards.py
│  └─ validators.py
├─ bot_data/
└─ scripts/
   └─ backup.bat
```

---

## Разработка и тестирование
- Все логи пишутся в `DATA_DIR/logs`.  
- Перед запуском убедитесь, что `.env` корректен.  
- Для разработки используйте уровень логов `DEBUG` в `core/logger.py`.  
- Проверка асинхронности и корректности данных выполняется в хендлерах.

---

## Лицензия
MIT License

Copyright (c) 2025 Соловьев Иван, Усенко Евгений, Александров Арсений

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## TODO
- Ответы на "Да" "Нет" при сбросе настроек.
- Презентация и DOCX + Докер
