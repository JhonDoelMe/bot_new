import os
import json
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Файлы для сохранения данных
REMINDERS_FILE = "reminders.json"  # Файл для хранения напоминаний
CITIES_FILE = "cities.json"       # Файл для хранения городов

def load_json_data(filename: str) -> Dict:
    """
    Загружает данные из JSON-файла.
    Если файл отсутствует или данные повреждены, возвращает пустой словарь.
    """
    if not os.path.exists(filename):
        logger.warning(f"Файл {filename} не найден. Будет использован пустой словарь.")
        return {}
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Ошибка при чтении файла {filename}: {e}")
        return {}

def save_json_data(filename: str, data: Dict) -> None:
    """
    Сохраняет данные в JSON-файл.
    Если происходит ошибка записи, логируется сообщение об ошибке.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Файл {filename} успешно обновлен.")
    except OSError as e:
        logger.error(f"Ошибка при записи в файл {filename}: {e}")

def load_reminders() -> Dict:
    """
    Загружает состояния напоминаний из файла JSON.
    Возвращает словарь, где ключ — ID пользователя, а значение — состояние.
    """
    return load_json_data(REMINDERS_FILE)

def save_reminder(reminders: Dict) -> None:
    """
    Сохраняет состояния напоминаний в файл JSON.
    """
    save_json_data(REMINDERS_FILE, reminders)

def load_cities() -> Dict:
    """
    Загружает данные о городах из файла JSON.
    Возвращает словарь, где ключ — ID пользователя, а значение — город.
    """
    return load_json_data(CITIES_FILE)

def save_city(user_id: str, city: str) -> None:
    """
    Сохраняет город для указанного пользователя в файл JSON.
    При изменении города данные перезаписываются.
    """
    if not city.strip():
        logger.warning(f"Город не может быть пустым. Пользователь {user_id}.")
        return
    
    cities = load_cities()
    cities[user_id] = city.strip()
    save_json_data(CITIES_FILE, cities)
    logger.info(f"Город '{city.strip()}' сохранён для пользователя {user_id}.")

def get_wind_direction(degrees: float) -> str:
    """
    Определяет направление ветра по углу в градусах.
    Нормализует угол и возвращает соответствующее направление.
    """
    directions = [
        "⬆️ Север", "↗️ Северо-восток", "➡️ Восток", "↘️ Юго-восток",
        "⬇️ Юг", "↙️ Юго-запад", "⬅️ Запад", "↖️ Северо-запад"
    ]
    index = round((degrees % 360) / 45) % 8
    return directions[index]
