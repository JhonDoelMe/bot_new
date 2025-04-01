import requests
import xml.etree.ElementTree as ET

NBU_EXCHANGE_RATE_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"

def get_exchange_rates():
    """
    Получает курсы валют от Национального банка Украины (XML формат).
    """
    try:
        response = requests.get(NBU_EXCHANGE_RATE_URL)
        response.raise_for_status()  # Проверить на ошибки HTTP
        xml_content = response.text
        root = ET.fromstring(xml_content)
        return root
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе курсов валют: {e}")
        return None
    except ET.ParseError as e:
        print(f"Ошибка при парсинге XML: {e}")
        return None

def format_exchange_rates(xml_root, currencies=('USD', 'EUR', 'PLN', 'RUB')):
    """
    Форматирует полученные курсы валют из XML для отображения.

    Args:
        xml_root (Element): Корневой элемент XML с курсами валют от НБУ.
        currencies (tuple): Список валют, которые нужно отобразить.

    Returns:
        str: Отформатированная строка с курсами валют.
    """
    if xml_root is None:
        return "Не удалось получить курсы валют."

    formatted_message = "Курсы валют от НБУ:\n"
    found_currencies = {}

    for currency_element in xml_root.findall('currency'):
        r030 = currency_element.find('r030').text
        txt = currency_element.find('txt').text
        rate = float(currency_element.find('rate').text)
        cc = currency_element.find('cc').text
        exchangedate = currency_element.find('exchangedate').text

        if cc in currencies:
            found_currencies[cc] = rate

    if not found_currencies:
        return f"Не найдены курсы для запрошенных валют: {', '.join(currencies)}"

    for currency, rate in found_currencies.items():
        formatted_message += f"{currency}/UAH: {rate:.2f}\n"

    formatted_message += "\nДанные предоставлены Национальным банком Украины."
    return formatted_message

if __name__ == '__main__':
    # Пример использования (можно закомментировать или удалить)
    exchange_rates_xml = get_exchange_rates()
    if exchange_rates_xml is not None:
        formatted_rates = format_exchange_rates(exchange_rates_xml)
        print(formatted_rates)