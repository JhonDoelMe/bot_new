import requests
import json

NBU_EXCHANGE_RATE_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"

def get_exchange_rates():
    """
    Получает курсы валют от Национального банка Украины.
    """
    try:
        response = requests.get(NBU_EXCHANGE_RATE_URL)
        response.raise_for_status()  # Проверить на ошибки HTTP
        try:
            data = response.json()
            return data
        except json.JSONDecodeError:
            print("Ошибка: Ответ от API курсов валют не является JSON.")
            print("Содержимое ответа:", response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе курсов валют: {e}")
        return None

def format_exchange_rates(rates, currencies=('USD', 'EUR', 'PLN', 'RUB')):
    """
    Форматирует полученные курсы валют для отображения.

    Args:
        rates (list): Список словарей с курсами валют от НБУ.
        currencies (tuple): Список валют, которые нужно отобразить.

    Returns:
        str: Отформатированная строка с курсами валют.
    """
    if not rates:
        return "Не удалось получить курсы валют."

    formatted_message = "Курсы валют от НБУ:\n"
    found_currencies = {}

    for item in rates:
        cc = item.get('cc')
        rate = item.get('rate')
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
    exchange_rates = get_exchange_rates()
    if exchange_rates:
        formatted_rates = format_exchange_rates(exchange_rates)
        print(formatted_rates)