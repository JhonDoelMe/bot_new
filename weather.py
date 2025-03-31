# bot_new/weather.py
import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
import aiohttp
from datetime import datetime

from config import WEATHER_API_KEY
from utils import get_user_city, get_wind_direction
# Импортируем ТОЛЬКО клавиатуры и тексты кнопок из keyboards
from keyboards import (
    weather_kb, main_menu_kb,
    kb_weather_text, kb_get_weather_now_text, kb_change_city_text # Добавляем kb_change_city_text
)


router = Router()
logger = logging.getLogger(__name__)

# Иконки теперь не нужны для фильтров, но оставляем для вывода
WEATHER_ICONS = {
    "01d": "☀️", "01n": "🌙", "02d": "🌤️", "02n": "☁️", "03d": "☁️", "03n": "☁️",
    "04d": "☁️", "04n": "☁️", "09d": "🌧️", "09n": "🌧️", "10d": "🌦️", "10n": "🌧️",
    "11d": "⛈️", "11n": "⛈️", "13d": "❄️", "13n": "❄️", "50d": "🌫️", "50n": "🌫️",
}


# Фильтр для "Погода"
@router.message(StateFilter(None), F.text == kb_weather_text)
async def handle_weather_menu(message: types.Message):
    # ... (логика без изменений) ...
    logger.info(f"Пользователь {message.from_user.id} нажал '{kb_weather_text}'")
    city = get_user_city(message.from_user.id)
    if not city:
        await message.answer(
            f"Сначала выберите город в меню '{kb_change_city_text}', чтобы я мог показать погоду.",
            reply_markup=main_menu_kb
        )
        return
    await message.answer(
        f"🌤️ Погода для города: <b>{city}</b>\n" # Оставим эмодзи в тексте ответа
        f"Нажмите кнопку '{kb_get_weather_now_text}', чтобы узнать текущую погоду.",
        reply_markup=weather_kb,
        parse_mode="HTML"
    )


# Фильтр для "Узнать погоду сейчас"
@router.message(StateFilter(None), F.text == kb_get_weather_now_text)
async def handle_get_weather(message: types.Message):
    # ... (логика получения погоды без изменений) ...
    logger.info(f"Пользователь {message.from_user.id} запросил '{kb_get_weather_now_text}'")
    user_id = message.from_user.id
    city = get_user_city(user_id)

    if not city:
        # ... (ответ без изменений)
        await message.answer(
             f"Не могу найти ваш сохраненный город. Пожалуйста, установите его через '{kb_change_city_text}'.",
             reply_markup=main_menu_kb # Возвращаем в главное меню
        )
        return

    if not WEATHER_API_KEY:
         # ... (ответ без изменений)
        await message.answer(
            "❌ Ключ API погоды не настроен. Не могу получить данные.",
            reply_markup=weather_kb # Оставляем в меню погоды
        )
        logger.warning(f"Попытка получить погоду для {city} без API ключа.")
        return

    processing_message = await message.answer("⏳ Получаю данные о погоде...", reply_markup=types.ReplyKeyboardRemove())
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric', 'lang': 'ru'
    }

    try:
        # ... (блок try/except для API без изменений, включая форматирование вывода с эмодзи)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                logger.debug(f"Запрос погоды для {city}. Статус: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    logger.debug(f"Ответ API погоды: {data}")

                    # Извлекаем нужные данные
                    city_name = data.get('name', city)
                    temp = data['main']['temp']
                    feels_like = data['main']['feels_like']
                    humidity = data['main']['humidity']
                    pressure_hpa = data['main']['pressure']
                    pressure_mmhg = round(pressure_hpa * 0.750062)
                    description = data['weather'][0]['description'].capitalize()
                    icon_code = data['weather'][0]['icon']
                    weather_icon = WEATHER_ICONS.get(icon_code, "❓") # Оставляем эмодзи в выводе
                    wind_speed = data['wind']['speed']
                    wind_deg = data['wind'].get('deg')
                    wind_dir_str = get_wind_direction(wind_deg) if wind_deg is not None else ""
                    timezone_offset = data.get('timezone', 0)
                    sunrise_ts = data['sys']['sunrise'] + timezone_offset
                    sunset_ts = data['sys']['sunset'] + timezone_offset
                    sunrise_time = datetime.utcfromtimestamp(sunrise_ts).strftime('%H:%M')
                    sunset_time = datetime.utcfromtimestamp(sunset_ts).strftime('%H:%M')

                    weather_report = (
                        f"📍 <b>{city_name}</b>\n"
                        f"{weather_icon} {description}\n\n" # Оставляем эмодзи в выводе
                        f"🌡️ Температура: <b>{temp:.1f}°C</b>\n"
                        f"🤔 Ощущается как: {feels_like:.1f}°C\n"
                        f"💧 Влажность: {humidity}%\n"
                        f"🕰️ Давление: {pressure_mmhg} мм рт. ст.\n"
                        f"💨 Ветер: {wind_speed:.1f} м/с {wind_dir_str}\n\n"
                        f"🌅 Восход: {sunrise_time}\n"
                        f"🌇 Закат: {sunset_time}"
                    )
                    # Редактируем сообщение об ожидании, заменяя его на результат
                    await processing_message.edit_text(weather_report, parse_mode="HTML", reply_markup=weather_kb)

                elif response.status == 404:
                    logger.warning(f"Город '{city}' не найден API погоды (404).")
                    await processing_message.edit_text(
                        f"❌ Не удалось найти информацию для города <b>{city}</b>.\n"
                        "Возможно, он был удален или название некорректно. "
                        "Попробуйте изменить город через меню.",
                        parse_mode="HTML",
                        reply_markup=main_menu_kb
                    )
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка API погоды ({response.status}) для города '{city}': {error_text}")
                    await processing_message.edit_text(
                        "❌ Произошла ошибка при получении данных о погоде от сервера. Попробуйте позже.",
                        reply_markup=weather_kb
                    )

    except aiohttp.ClientConnectorError as e:
        logger.error(f"Ошибка соединения при получении погоды для '{city}': {e}")
        await processing_message.edit_text("❌ Не удалось связаться с сервером погоды. Проверьте интернет или попробуйте позже.", reply_markup=weather_kb)
    except TimeoutError:
        logger.error(f"Таймаут при запросе погоды для '{city}'.")
        await processing_message.edit_text("❌ Сервер погоды не отвечает. Попробуйте позже.", reply_markup=weather_kb)
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при получении погоды для '{city}': {e}")
        await processing_message.edit_text("❌ Произошла непредвиденная ошибка при обработке запроса погоды.", reply_markup=weather_kb)