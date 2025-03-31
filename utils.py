import os
import json
import logging
from datetime import datetime
from typing import Dict

logger = logging.getLogger(__name__)
# Используем переменную окружения для пути к файлу, если задана, иначе дефолт "cities.json"
CITIES_FILE = os.getenv("CITIES_FILE", "cities.json")

def load_cities() -> Dict[str, str]:
    """
    Загружает данные о городах из файла JSON.
    Если файла не существует или содержит некорректный JSON, возвращает пустой словарь.
    """
    if not os.path.exists(CITIES_FILE):
        # Создание файла с пустым словарём
        try:
            with open(CITIES_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False)
        except OSError as e:
            logger.error(f"Ошибка при создании файла {CITIES_FILE}: {e}")
            return {}
        return {}

    try:
        with open(CITIES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Ошибка при чтении файла {CITIES_FILE}: {e}")
        data = {}
    logger.info(f"Загружены данные из {CITIES_FILE}: {data}")
    return {k: v.strip() for k, v in data.items()}

def save_city(user_id: int, city: str) -> None:
    """
    Сохраняет название города для пользователя.
    Принимает идентификатор пользователя и название города,
    записывает данные в JSON-файл.
    """
    cities = load_cities()
    cities[str(user_id)] = city.strip()
    try:
        with open(CITIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cities, f, ensure_ascii=False)
        logger.info(f"Сохранён город '{city.strip()}' для пользователя {user_id}")
    except OSError as e:
        logger.error(f"Ошибка при записи в файл {CITIES_FILE}: {e}")

def get_wind_direction(degrees: float) -> str:
    """
    Определяет направление ветра по углу в градусах.
    Нормализует угол для корректной обработки отрицательных значений и значений больше 360.
    """
    # Нормализация градусов в диапазоне 0-360
    degrees = degrees % 360

    if 337.5 <= degrees < 360 or 0 <= degrees < 22.5:
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
    return "Неизвестно"
