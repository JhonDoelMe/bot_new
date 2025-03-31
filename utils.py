# bot_new/utils.py
import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Пути к файлам из конфига
# Импортируем их здесь, чтобы избежать циклических зависимостей с config.py
# но предполагаем, что config.py уже загрузил переменные
from config import CITIES_FILE, REMINDERS_FILE


def load_json_data(filename: str) -> Dict[str, Any]:
    """
    Загружает данные из JSON-файла.
    Если файл отсутствует, пуст или данные повреждены, возвращает пустой словарь
    и логирует предупреждение/ошибку.
    Создает пустой файл, если он не существует.
    """
    if not os.path.exists(filename):
        logger.warning(f"Файл {filename} не найден. Создаю новый пустой файл.")
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump({}, f)
            return {}
        except OSError as e:
            logger.error(f"Не удалось создать файл {filename}: {e}")
            return {} # Возвращаем пустой словарь в случае ошибки создания

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                logger.warning(f"Файл {filename} пуст. Возвращаю пустой словарь.")
                return {}
            return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка декодирования JSON в файле {filename}: {e}. Содержимое файла будет перезаписано при следующем сохранении.")
        return {} # Возвращаем пустой словарь при ошибке декодирования
    except OSError as e:
        logger.error(f"Ошибка чтения файла {filename}: {e}")
        return {}


def save_json_data(filename: str, data: Dict[str, Any]) -> None:
    """
    Сохраняет данные в JSON-файл с отступами для читаемости.
    Если происходит ошибка записи, логируется сообщение об ошибке.
    """
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # logger.info(f"Данные успешно сохранены в файл {filename}.") # Можно раскомментировать для отладки
    except OSError as e:
        logger.error(f"Ошибка при записи в файл {filename}: {e}")
    except TypeError as e:
         logger.error(f"Ошибка сериализации данных для файла {filename}: {e}")


def load_reminders() -> Dict[str, Any]:
    """
    Загружает состояния напоминаний из файла REMINDERS_FILE.
    """
    return load_json_data(REMINDERS_FILE)

def save_reminders(reminders: Dict[str, Any]) -> None:
    """
    Сохраняет состояния напоминаний в файл REMINDERS_FILE.
    """
    save_json_data(REMINDERS_FILE, reminders)


def load_cities() -> Dict[str, str]:
    """
    Загружает данные о городах пользователей из файла CITIES_FILE.
    Ключ - user_id (строка), значение - город (строка).
    """
    # Указываем тип возвращаемого значения более конкретно
    return load_json_data(CITIES_FILE) # type: ignore

def save_city(user_id: int, city: str) -> None:
    """
    Сохраняет или обновляет город для указанного пользователя (по ID) в файле CITIES_FILE.
    ID пользователя конвертируется в строку для использования как ключ JSON.
    """
    cities = load_cities()
    cities[str(user_id)] = city.strip() # Используем строковый ID как ключ JSON
    save_json_data(CITIES_FILE, cities)
    logger.info(f"Город '{city.strip()}' сохранён для пользователя {user_id}.")

def get_user_city(user_id: int) -> str | None:
    """
    Получает сохраненный город для пользователя.
    Возвращает город или None, если город не найден.
    """
    cities = load_cities()
    return cities.get(str(user_id))


def get_wind_direction(degrees: float) -> str:
    """
    Определяет направление ветра по углу в градусах.
    Нормализует угол для корректной обработки значений вне диапазона 0-360.
    """
    degrees = degrees % 360

    directions = {
        (337.5, 22.5): "⬆️ Северный",
        (22.5, 67.5): "↗️ Северо-восточный",
        (67.5, 112.5): "➡️ Восточный",
        (112.5, 157.5): "↘️ Юго-восточный",
        (157.5, 202.5): "⬇️ Южный",
        (202.5, 247.5): "↙️ Юго-западный",
        (247.5, 292.5): "⬅️ Западный",
        (292.5, 337.5): "↖️ Северо-западный",
    }

    for (lower, upper), direction in directions.items():
        if lower <= degrees < upper:
            return direction
    # Особый случай для диапазона, пересекающего 0/360 градусов (Север)
    if 337.5 <= degrees < 360 or 0 <= degrees < 22.5:
        return "⬆️ Северный"

    return "❓ Неизвестно"