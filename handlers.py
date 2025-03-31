from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
import aiohttp
import logging
from datetime import datetime

from config import WEATHER_API_KEY
from utils import load_cities, save_city, get_wind_direction

logger = logging.getLogger(__name__)

router = Router()

# Основная клавиатура
main_kb = [
    [types.KeyboardButton(text="Мой город")],
    [types.KeyboardButton(text="Изменить город")]
]

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start.
    Если город не сохранён, просит ввести название города,
    иначе предлагает выбрать действие.
    """
    user_id = message.from_user.id
    cities = load_cities()

    if str(user_id) not in cities:
        await message.answer(
            "🌤️ Привет! Введите название вашего города:",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "🌤️ Привет! Выберите действие:",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=main_kb,
                resize_keyboard=True
            )
        )

@router.message(F.text.lower() == "мой город")
async def my_city_weather(message: types.Message):
    """
    Обработчик для кнопки "Мой город".
    Выводит текущую погоду для сохранённого пользователем города.
    """
    user_id = message.from_user.id
    cities = load_cities()

    if str(user_id) not in cities:
        await message.answer("❌ Город не задан. Пожалуйста, введите название города.")
        return

    city = cities[str(user_id)]
    logger.info(f"Получен запрос погоды для города: '{city}'")

    try:
        async with aiohttp.ClientSession() as session:
            url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            )
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                if response.status != 200:
                    error_message = data.get("message", "Неизвестная ошибка")
                    await message.answer(f"❌ Ошибка: {error_message}")
                    return

                # Извлекаем необходимые данные
                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                wind_deg = data["wind"].get("deg", 0)
                description = data["weather"][0]["description"].capitalize()
                sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
                sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")

                wind_direction = get_wind_direction(wind_deg)

                await message.answer(
                    f"🌆 Погода в {hbold(city)}:\n\n"
                    f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                    f"💧 Влажность: {humidity}%\n"
                    f"🌬️ Ветер: {wind_direction} {wind_speed} м/с\n"
                    f"🌅 Восход: {sunrise}\n"
                    f"🌇 Закат: {sunset}\n"
                    f"☁️ Состояние: {description}"
                )

    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при запросе данных: {e}")
        await message.answer("❌ Не удалось получить данные. Проверьте название города.")
    except Exception as e:
        logger.error(f"Необработанная ошибка при получении погоды: {e}")
        await message.answer("❌ Что-то пошло не так. Попробуйте позже.")

@router.message(F.text.lower() == "изменить город")
async def change_city(message: types.Message):
    """
    Обработчик для кнопки "Изменить город".
    Запрашивает у пользователя новое название города, сбрасывая текущую клавиатуру.
    """
    await message.answer(
        "Введите новое название города:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@router.message(F.text)  # Обработчик для ввода названия города (если текст не совпадает с командами)
async def process_city_input(message: types.Message):
    """
    Обрабатывает ввод названия города.
    Если текст не совпадает с уже обработанными командами, проверяет корректность города.
    Выполняется запрос к OpenWeatherMap для проверки введённого города, после чего город сохраняется.
    """
    user_id = message.from_user.id
    city = message.text.strip()

    # Данный блок на всякий случай оставляем,
    # но при корректном порядке обработчиков он не должен срабатывать.
    if city.lower() in ["мой город", "изменить город"]:
        return

    async with aiohttp.ClientSession() as session:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        )
        async with session.get(url, timeout=10) as response:
            data = await response.json()
            if response.status != 200:
                error_message = data.get("message", "Неизвестная ошибка")
                await message.answer(f"❌ Ошибка: {error_message}")
                return

    save_city(user_id, city)
    await message.answer(
        f"✅ Город '{city}' успешно сохранён!",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=main_kb,
            resize_keyboard=True
        )
    )
