import requests
import json
import logging

# Настройка базового логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_ALERTS_URL = "http://ubilling.net.ua/aerialalerts/"

def get_air_raid_status(region):
    """
    Получает статус воздушной тревоги для указанного региона с логированием.

    Args:
        region (str): Название региона.

    Returns:
        str or None: Статус тревоги ("Тривога", "Відбій") или None в случае ошибки или отсутствия региона.
    """
    logging.info(f"Запрошен статус тревоги для региона: '{region}'")
    try:
        response = requests.get(BASE_ALERTS_URL)
        response.raise_for_status()
        raw_json = response.text
        logging.info(f"Получен JSON от API: {raw_json}")
        data = json.loads(raw_json)
        if 'states' in data:
            for state_name, state_params in data['states'].items():
                logging.info(f"Сравнение: API регион '{state_name.lower()}' с запрошенным '{region.lower()}'")
                if state_name.lower() == region.lower():
                    if state_params['alertnow']:
                        return "Тривога"
                    else:
                        return "Відбій"
        else:
            logging.warning("Ключ 'states' не найден в JSON-ответе.")
        return None  # Регион не найден
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к API тревог: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка при декодировании JSON от API тревог: {e}")
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