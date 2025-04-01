import requests
import json

BASE_ALERTS_URL = "https://ubilling.net.ua/aerialalerts/static/js/map_data.json"

def get_air_raid_status(region):
    """
    Получает статус воздушной тревоги для указанного региона, используя новый источник.

    Args:
        region (str): Название региона.

    Returns:
        str or None: Статус тревоги ("Тривога", "Відбій") или None в случае ошибки или отсутствия региона.
    """
    try:
        response = requests.get(BASE_ALERTS_URL)
        response.raise_for_status()
        data = response.json()
        for item in data:
            if item['region'].lower() == region.lower():
                if item['status'] == 1:
                    return "Тривога"
                elif item['status'] == 0:
                    return "Відбій"
        return None  # Регион не найден
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API тревог: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Ошибка при декодировании JSON от API тревог: {e}")
        return None

def format_air_raid_message(region, status):
    """
    Форматирует сообщение о статусе воздушной тревоги.

    Args:
        region (str): Название региона.
        status (str): Статус тревоги.

    Returns:
        str: Отформатированное сообщение.
    """
    if status == "Тривога":
        return f"🚨 Внимание! В регионе '{region}' объявлена воздушная тревога!"
    elif status == "Відбій":
        return f"✅ В регионе '{region}' отбой воздушной тревоги."
    else:
        return f"Не удалось получить статус воздушной тревоги для региона '{region}'."