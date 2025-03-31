import os
import json
import logging

logger = logging.getLogger(__name__)

REMINDERS_FILE = "reminders.json"  # Файл для сохранения состояний напоминаний
CITIES_FILE = "cities.json"       # Файл для сохранения городов

def load_reminders() -> dict:
    """
    Загружает состояния напоминаний из файла JSON.
    Возвращает словарь, где ключ — это ID пользователя, а значение — состояние.
    """
    if not os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file, ensure_ascii=False, indent=4)
            def load_reminders() -> dict:
    """
    Загружает состояния напоминаний из файла JSON.
    Возвращает словарь, где ключ — это ID пользователя, а значение — состояние.
    """
    if not os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)
        return {}
    try:
        with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при чтении файла {REMINDERS_FILE}: {e}")
        return {}

def save_reminder(reminders: dict) -> None:
    """
    Сохраняет состояния напоминаний в файл JSON.
    """
    try:
        with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
            json.dump(reminders, f, ensure_ascii=False)
        logger.info("Состояния напоминаний успешно сохранены.")
    except OSError as e:
        logger.error(f"Ошибка при записи в файл {REMINDERS_FILE}: {e}")

def load_cities() -> dict:
    """
    Загружает данные о городах из файла JSON.
    Возвращает словарь, где ключ — ID пользователя, а значение — город.
    """
    if not os.path.exists(CITIES_FILE):
        with open(CITIES_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)
        return {}
    try:
        with open(CITIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при чтении файла {CITIES_FILE}: {e}")
        return {}

def save_city(user_id: int, city: str) -> None:
    """
    Сохраняет город для указанного пользователя в файл JSON.
    """
    cities = load_cities()
    cities[str(user_id)] = city.strip()
    try:
        with open(CITIES_FILE, "w", encoding="utf-8") as f:
            json.dump(cities, f, ensure_ascii=False)
        logger.info(f"Город '{city.strip()}' сохранён для пользователя {user_id}.")
    except OSError as e:
        logger.error(f"Ошибка при записи в файл {CITIES_FILE}: {e}")

def get_wind_direction(degrees: float) -> str:
    """
    Определяет направление ветра по углу в градусах.
    Нормализует угол для корректной обработки значений вне диапазона 0-360.
    """
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
