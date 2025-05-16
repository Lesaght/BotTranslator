#!/usr/bin/env python3
"""
Основной файл для запуска Telegram-бота.
"""
import sys
import os
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Проверка и установка токена Telegram
if not os.environ.get('TELEGRAM_BOT_TOKEN'):
    telegram_token = "7912439045:AAFM7Kow1olQrvAvHfoQkY0VFeUQoTWyVAg"
    os.environ['TELEGRAM_BOT_TOKEN'] = telegram_token
    print(f"Установлен токен TELEGRAM_BOT_TOKEN")

# Инициализация базы данных
from database import init_db
init_db()

# Для обратной совместимости с workflow, который пытается запустить Flask-приложение
# Создаем заглушку для gunicorn
class DummyApp:
    def __call__(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [b"WARNING: Web interface has been removed from this project.\nOnly Telegram bot is available now."]

# Для gunicorn и других WSGI-серверов
app = DummyApp()

# Импорт функции main из модуля bot
from bot import main

if __name__ == "__main__":
    # Запускаем основную функцию из bot.py
    sys.exit(main())