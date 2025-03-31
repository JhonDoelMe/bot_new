import os
from dotenv import load_dotenv

"""
Конфигурационный модуль проекта.
Загружает переменные окружения для бота и API погоды.
"""

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
# Путь можно задавать через переменную окружения с дефолтным значением
CITIES_FILE = os.getenv("CITIES_FILE", "cities.json")

if not BOT_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Необходимо указать BOT_TOKEN и WEATHER_API_KEY в .env файле.")
