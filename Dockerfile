# Используем официальный Python-образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы проекта
COPY . /app
COPY .env /app/.env


# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем локаль (если нужно выводить кириллицу)
ENV PYTHONIOENCODING=utf-8

# Запускаем бота
CMD ["python", "main.py"]
