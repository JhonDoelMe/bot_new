import requests
import json
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
WEATHER_API_KEY = config['weather']['api_key']
BASE_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?"

def get_weather(city):
    """
    Получает данные о погоде для указанного города с OpenWeatherMap.
    """
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    try:
        response = requests.get(BASE_WEATHER_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе погоды: {e}")
        return None

def format_weather_data(weather_data):
    """
    Форматирует полученные данные о погоде в желаемый вид.

    Args:
        weather_data (dict): Словарь с данными о погоде.

    Returns:
        str: Отформатированная строка с информацией о погоде.
    """
    city = weather_data.get('name', 'Неизвестно')
    temperature = weather_data.get('main', {}).get('temp')
    feels_like = weather_data.get('main', {}).get('feels_like')
    humidity = weather_data.get('main', {}).get('humidity')
    wind_speed = weather_data.get('wind', {}).get('speed')
    wind_deg = weather_data.get('wind', {}).get('deg')
    description = weather_data.get('weather', [{}])[0].get('description', 'Нет данных')
    sunrise_timestamp = weather_data.get('sys', {}).get('sunrise')
    sunset_timestamp = weather_data.get('sys', {}).get('sunset')

    # Переводим время восхода и заката в формат HH:MM
    import datetime
    sunrise_time = datetime.datetime.fromtimestamp(sunrise_timestamp).strftime('%H:%M') if sunrise_timestamp else 'Нет данных'
    sunset_time = datetime.datetime.fromtimestamp(sunset_timestamp).strftime('%H:%M') if sunset_timestamp else 'Нет данных'

    # Определяем направление ветра (упрощенно)
    wind_direction = ""
    if wind_deg is not None:
        if 0 <= wind_deg < 22.5 or 337.5 <= wind_deg < 360:
            wind_direction = "⬆️ Север"
        elif 22.5 <= wind_deg < 67.5:
            wind_direction = "↗️ Северо-восток"
        elif 67.5 <= wind_deg < 112.5:
            wind_direction = "➡️ Восток"
        elif 112.5 <= wind_deg < 157.5:
            wind_direction = "↘️ Юго-восток"
        elif 157.5 <= wind_deg < 202.5:
            wind_direction = "⬇️ Юг"
        elif 202.5 <= wind_deg < 247.5:
            wind_direction = "↙️ Юго-запад"
        elif 247.5 <= wind_deg < 292.5:
            wind_direction = "⬅️ Запад"
        elif 292.5 <= wind_deg < 337.5:
            wind_direction = "↖️ Северо-запад"
        else:
            wind_direction = f"{wind_deg}°" # Если не попадает в основные направления

    formatted_message = f"🌆 Погода в {city} сегодня:\n\n"
    formatted_message += f"🌡️ Температура: {temperature:.2f}°C (ощущается как {feels_like:.2f}°C)\n"
    formatted_message += f"💧 Влажность: {humidity}%\n"
    formatted_message += f"🌬️ Ветер: {wind_direction} {wind_speed:.2f} м/с\n"
    formatted_message += f"🌅 Восход: {sunrise_time}\n"
    formatted_message += f"🌇 Закат: {sunset_time}\n"
    formatted_message += f"☁️ Состояние: {description.capitalize()}\n"

    return formatted_message