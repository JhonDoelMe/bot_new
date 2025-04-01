import requests
import configparser

# --- Чтение конфигурации ---
config = configparser.ConfigParser()
config.read('config.ini')
WEATHER_API_KEY = config['openweathermap']['api_key']
BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

def get_weather(city):
    """
    Получает данные о погоде для указанного города с OpenWeatherMap API.
    """
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric',  # Можно изменить на 'imperial' для градусов Фаренгейта
        'lang': 'ru'       # Можно изменить на другой язык
    }
    try:
        response = requests.get(BASE_WEATHER_URL, params=params)
        response.raise_for_status()  # Проверить, не было ли ошибки в ответе
        weather_data = response.json()
        return weather_data
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API погоды: {e}")
        return None

def format_weather_data(weather_data):
    """
    Форматирует полученные данные о погоде в удобочитаемый вид.
    """
    if weather_data:
        try:
            city_name = weather_data['name']
            temperature = weather_data['main']['temp']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            description = weather_data['weather'][0]['description']
            feels_like = weather_data['main']['feels_like']

            formatted_message = f"Погода в городе: {city_name}\n"
            formatted_message += f"Температура: {temperature}°C (ощущается как {feels_like}°C)\n"
            formatted_message += f"Влажность: {humidity}%\n"
            formatted_message += f"Скорость ветра: {wind_speed} м/с\n"
            formatted_message += f"Описание: {description.capitalize()}"
            return formatted_message
        except KeyError:
            return "Не удалось обработать данные о погоде."
    else:
        return "Не удалось получить данные о погоде для указанного города."

if __name__ == '__main__':
    # Пример использования (можно закомментировать или удалить)
    city = "Днепр"
    weather = get_weather(city)
    if weather:
        formatted_weather = format_weather_data(weather)
        print(formatted_weather)