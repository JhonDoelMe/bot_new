import requests
import json
import logging
import xml.etree.ElementTree as ET
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Настройка базового логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_ALERTS_URL = "http://ubilling.net.ua/aerialalerts/"

def get_air_raid_status(region):
    """
    Получает статус воздушной тревоги для указанного региона.
    """
    try:
        response = requests.get(BASE_ALERTS_URL)
        response.raise_for_status()
        data = response.json()
        if 'states' in data:
            for state_name, state_params in data['states'].items():
                if state_name.lower() == region.lower():
                    if state_params['alertnow']:
                        return "Тривога"
                    else:
                        return "Відбій"
        else:
            logging.warning("Ключ 'states' не найден в JSON-ответе.")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к API тревог: {e}")
        return None
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка при декодировании JSON от API тревог: {e}")
        return None

def format_air_raid_message(region, status):
    """
    Форматирует сообщение о статусе воздушной тревоги.
    """
    if status == "Тривога":
        return f"🚨 Внимание! В регионе '{region}' объявлена воздушная тревога!"
    elif status == "Відбій":
        return f"✅ В регионе '{region}' отбой воздушной тревоги."
    else:
        return f"Не удалось получить статус воздушной тревоги для региона '{region}'."

def get_alerts_list_xml():
    """
    Получает список областей и их статус из XML.
    """
    try:
        xml_url = "https://ubilling.net.ua/aerialalerts/?xml=true"
        response = requests.get(xml_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        alerts_list = "Статус воздушных тревог по областям:\n"
        for state in root.findall('state'):
            name_element = state.find('name')
            alert_element = state.find('alertnow')
            if name_element is not None and alert_element is not None:
                name = name_element.text
                alert = alert_element.text == 'true'
                alerts_list += f"- {name}: {'🚨 Тривога' if alert else '✅ Відбій'}\n"
        return alerts_list
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе к XML: {e}")
        return "Не удалось получить список областей."
    except ET.ParseError as e:
        logging.error(f"Ошибка при парсинге XML: {e}")
        return "Не удалось обработать список областей."

def get_alerts_map_image():
    """
    Получает изображение карты воздушных тревог (использует Selenium для скриншота).
    """
    try:
        map_url = "https://ubilling.net.ua/aerialalerts/?map=true"
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Запуск браузера в фоновом режиме
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(map_url)
        # Даем время на загрузку карты (может потребоваться настройка)
        driver.implicitly_wait(5)
        # Получаем скриншот элемента с картой (может потребоваться определить точный селектор)
        map_element = driver.find_element("xpath", "//div[@id='map']")  # Примерный XPATH, может отличаться
        image_bytes = map_element.screenshot_as_png
        driver.quit()
        return BytesIO(image_bytes)
    except Exception as e:
        logging.error(f"Ошибка при получении изображения карты: {e}")
        return None