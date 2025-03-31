# bot_new/weather.py
import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
import aiohttp
from datetime import datetime

from config import WEATHER_API_KEY
from utils import get_user_city, get_wind_direction
from keyboards import weather_kb, main_menu_kb # Импортируем клавиатуры

router = Router()
logger = logging.getLogger(__name__)

WEATHER_ICONS = {
    "01d": "☀️", "01n": "🌙",
    "02d": "🌤️", "02n": "☁️",
    "03d": "☁️", "03n": "☁️",
    "04d": "☁️", "04n": "☁️",
    "09d": "🌧️", "09n": "🌧️",
    "10d": "🌦️", "10n": "🌧️",
    "11d": "⛈️", "11n": "⛈️",
    "13d": "❄️", "13n": "❄️",
    "50d": "🌫️", "50n": "🌫️",
}


@router.message(StateFilter(None), F.text.lower() == "погода 🌤️")
async def handle_weather_menu(message: types.Message):
    """
    Обработчик кнопки "Погода".
    Переводит пользователя в раздел погоды.
    """
    city = get_user_city(message.from_user.id)
    if not city:
        await message.answer(
            "Сначала выберите город в меню 'Изменить город ✏️', чтобы я мог показать погоду.",
            reply_markup=main_menu_kb # Возврат в главное меню, т.к. без города здесь делать нечего
        )
        return

    await message.answer(
        f"🌤️ Погода для города: <b>{city}</b>\n"
        "Нажмите кнопку ниже, чтобы узнать текущую погоду.",
        reply_markup=weather_kb,
        parse_mode="HTML"
    )

@router.message(StateFilter(None), F.text.lower() == "узнать погоду сейчас 🌦️")
async def handle_get_weather(message: types.Message):
    """
    Обработчик кнопки "Узнать погоду сейчас".
    Запрашивает погоду для сохраненного города пользователя.
    """
    user_id = message.from_user.id
    city = get_user_city(user_id)

    if not city:
        await message.answer(
             "Не могу найти ваш сохраненный город. Пожалуйста, установите его через 'Изменить город ✏️'.",
             reply_markup=main_menu_kb # Возвращаем в главное меню
        )
        return

    if not WEATHER_API_KEY:
        await message.answer(
            "❌ Ключ API погоды не настроен. Не могу получить данные.",
            reply_markup=weather_kb # Оставляем в меню погоды
        )
        logger.warning(f"Попытка получить погоду для {city} без API ключа.")
        return

    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': WEATHER_API_KEY,
        'units': 'metric', # Градусы Цельсия
        'lang': 'ru'       # Язык описания погоды
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                logger.debug(f"Запрос погоды для {city}. Статус: {response.status}") # Отладочное сообщение
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"Ответ API погоды: {data}") # Отладочное сообщение

                    # Извлекаем нужные данные
                    city_name = data.get('name', city) # Используем имя из ответа API
                    temp = data['main']['temp']
                    feels_like = data['main']['feels_like']
                    humidity = data['main']['humidity']
                    pressure_hpa = data['main']['pressure']
                    pressure_mmhg = round(pressure_hpa * 0.750062) # Перевод гПа в мм рт. ст.
                    description = data['weather'][0]['description'].capitalize()
                    icon_code = data['weather'][0]['icon']
                    weather_icon = WEATHER_ICONS.get(icon_code, "❓")
                    wind_speed = data['wind']['speed']
                    wind_deg = data['wind'].get('deg') # Направление ветра может отсутствовать
                    wind_dir_str = get_wind_direction(wind_deg) if wind_deg is not None else ""

                    # Время восхода и заката (UTC -> местное)
                    timezone_offset = data.get('timezone', 0) # Смещение в секундах от UTC
                    sunrise_ts = data['sys']['sunrise'] + timezone_offset
                    sunset_ts = data['sys']['sunset'] + timezone_offset
                    sunrise_time = datetime.utcfromtimestamp(sunrise_ts).strftime('%H:%M')
                    sunset_time = datetime.utcfromtimestamp(sunset_ts).strftime('%H:%M')

                    # Формируем сообщение
                    weather_report = (
                        f"📍 <b>{city_name}</b>\n"
                        f"{weather_icon} {description}\n\n"
                        f"🌡️ Температура: <b>{temp:.1f}°C</b>\n"
                        f"🤔 Ощущается как: {feels_like:.1f}°C\n"
                        f"💧 Влажность: {humidity}%\n"
                        f"🕰️ Давление: {pressure_mmhg} мм рт. ст.\n"
                        f"💨 Ветер: {wind_speed:.1f} м/с {wind_dir_str}\n\n"
                        f"🌅 Восход: {sunrise_time}\n"
                        f"🌇 Закат: {sunset_time}"
                    )

                    await message.answer(weather_report, parse_mode="HTML", reply_markup=weather_kb)

                elif response.status == 404:
                    logger.warning(f"Город '{city}' не найден API погоды (ошибка 404). Возможно, он был удален или изменен.")
                    await message.answer(
                        f"❌ Не удалось найти информацию для города <b>{city}</b>.\n"
                        "Возможно, он был удален или название некорректно. "
                        "Попробуйте изменить город через меню.",
                        parse_mode="HTML",
                        reply_markup=main_menu_kb # Предлагаем вернуться и изменить
                    )
                    # Можно добавить логику удаления некорректного города из cities.json
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка API погоды ({response.status}) для города '{city}': {error_text}")
                    await message.answer(
                        "❌ Произошла ошибка при получении данных о погоде от сервера. Попробуйте позже.",
                        reply_markup=weather_kb
                    )

    except aiohttp.ClientConnectorError as e:
        logger.error(f"Ошибка соединения при получении погоды для '{city}': {e}")
        await message.answer("❌ Не удалось связаться с сервером погоды. Проверьте интернет или попробуйте позже.", reply_markup=weather_kb)
    except TimeoutError:
        logger.error(f"Таймаут при запросе погоды для '{city}'.")
        await message.answer("❌ Сервер погоды не отвечает. Попробуйте позже.", reply_markup=weather_kb)
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при получении погоды для '{city}': {e}") # Используем exception для стектрейса
        await message.answer("❌ Произошла непредвиденная ошибка при обработке запроса погоды.", reply_markup=weather_kb)