# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

# Создаём папку для данных (на случай, если volume не подключён)
RUN mkdir -p /app/bot_data

# Запуск
CMD ["python", "main.py"]