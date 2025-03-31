# bot_new/config.py
import os
from dotenv import load_dotenv
import logging

"""
Конфигурационный модуль проекта.
Загружает переменные окружения для бота и API погоды.
"""

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
# Путь можно задавать через переменную окружения с дефолтным значением
CITIES_FILE = os.getenv("CITIES_FILE", "cities.json")
REMINDERS_FILE = os.getenv("REMINDERS_FILE", "reminders.json")

# Проверка наличия обязательных переменных
if not BOT_TOKEN:
    logging.critical("Ошибка: BOT_TOKEN не найден в .env файле!")
    raise ValueError("Необходимо указать BOT_TOKEN в .env файле.")

if not WEATHER_API_KEY:
    logging.warning("Внимание: WEATHER_API_KEY не найден в .env файле. Функционал погоды будет недоступен.")
    # Можно не падать, а просто деактивировать фичу погоды,
    # но пока оставим как есть - без ключа погода не заработает.
    # raise ValueError("Необходимо указать WEATHER_API_KEY в .env файле для работы модуля погоды.")