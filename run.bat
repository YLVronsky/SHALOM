chcp 65001
@echo off
title Запуск бота SHALOM
echo.
echo 🚀 Запуск бота "Умная викторина"...
echo.

:: Проверяем, установлен ли Docker
where docker >nul
if %errorlevel% neq 0 (
    echo ❌ Docker не найден!
    echo.
    echo Пожалуйста, установите Docker Desktop:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b
)

:: Загружаем образ
echo ▶ Загрузка образа...
docker load -i shalom-bot.tar

:: Создаём папку для данных (если не существует)
if not exist bot_data mkdir bot_data

:: Запускаем контейнер
echo ▶ Запуск бота...
docker run -d ^
  --name shalom-bot ^
  -v "%cd%\bot_/app/bot_data" ^
  shalom-bot

:: Показываем статус
echo.
echo ✅ Бот запущен! Проверьте логи:
echo docker logs shalom-bot
echo.
echo 🔗 Скопируйте этот URL в браузер, чтобы увидеть инструкцию:
echo https://dev.max.ru/docs
echo.
echo 💬 Откройте мессенджер MAX, найдите бота @t75_hakaton_bot и напишите /start
echo.
pause