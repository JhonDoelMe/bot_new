import json
import logging
from datetime import datetime

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Путь к файлу с городами
CITIES_FILE = "cities.json"

# Функция для чтения данных из файла
def load_cities():
    if not os.path.exists(CITIES_FILE):
        with open(CITIES_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)
    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        logger.info(f"Загружены данные из cities.json: {data}")
        return {k: v.strip() for k, v in data.items()}  # Очищаем значения от пробелов

# Функция для записи данных в файл
def save_city(user_id, city):
    cities = load_cities()
    cities[str(user_id)] = city.strip()  # Сохраняем город без лишних пробелов
    with open(CITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False)
    logger.info(f"Сохранён город '{city.strip()}' для пользователя {user_id}")

# Функция для определения направления ветра
def get_wind_direction(degrees):
    if 337.5 <= degrees <= 360 or 0 <= degrees < 22.5:
        return "⬆️ Север"
    elif 22.5 <= degrees < 67.5:
        return "↗️ Северо-восток"
    elif 67.5 <= degrees < 112.5:
        return "➡️ Восток"
    elif 112.5 <= degrees < 157.5:
        return "↘️ Юго-восток"
    elif 157.5 <= degrees < 202.5:
        return "⬇️ Юг"
    elif 202.5 <= degrees < 247.5:
        return "↙️ Юго-запад"
    elif 247.5 <= degrees < 292.5:
        return "⬅️ Запад"
    elif 292.5 <= degrees < 337.5:
        return "↖️ Северо-запад"