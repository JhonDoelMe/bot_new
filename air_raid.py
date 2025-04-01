import requests
import json

BASE_ALERTS_URL = "https://alerts.ubilling.net.ua/alerts"

def get_air_raid_status(region):
    """
    Получает статус воздушной тревоги для указанного региона.

    Args:
        region (str): Название региона на украинском языке (например, "Дніпропетровська область").

    Returns:
        bool or None: True, если объявлена тревога, False - если нет, None - в случае ошибки.
    """
    params = {'region': region}
    try:
        response = requests.get(BASE_ALERTS_URL, params=params)
        response.raise_for_status()
        data = response.json()
        # API возвращает список. Проверим, есть ли активная тревога для нашего региона.
        for alert in data:
            if alert.get('region') == region:
                return alert.get('status') == 'Тривога'
        return False # Если для нашего региона нет записи или статус не "Тривога", считаем, что тревоги нет
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе статуса воздушной тревоги: {e}")
        return None

def format_air_raid_message(region, status):
    """
    Форматирует сообщение о статусе воздушной тревоги для пользователя.

    Args:
        region (str): Название региона.
        status (bool): Статус тревоги (True/False).

    Returns:
        str: Отформатированное сообщение.
    """
    if status is True:
        return f"⚠️ Внимание! В {region} объявлена воздушная тревога! ⚠️"
    elif status is False:
        return f"✅ В {region} воздушная тревога отменена."
    else:
        return f"Не удалось получить информацию о воздушной тревоге для {region}."

if __name__ == '__main__':
    # Пример использования (для Днепропетровской области)
    region_name = "Дніпропетровська область"
    alert_status = get_air_raid_status(region_name)
    print(format_air_raid_message(region_name, alert_status))