from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
import aiohttp
from config import WEATHER_API_KEY
from utils import load_cities, save_city, get_wind_direction

# Инициализация роутера
router = Router()

# Клавиатура
main_kb = [
    [types.KeyboardButton(text="Мой город")],
    [types.KeyboardButton(text="Изменить город")]
]

# Команда /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
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

# Обработчик ввода города
@router.message(F.text)
async def process_city_input(message: types.Message):
    user_id = message.from_user.id
    city = message.text.strip()

    if not city.isprintable():
        await message.answer("❌ Название города содержит недопустимые символы.")
        return

    # Проверяем, что город существует в API
    async with aiohttp.ClientSession() as session:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                data = await response.json()
                error_message = data.get("message", "Неизвестная ошибка")
                await message.answer(f"❌ Ошибка: {error_message}")
                return

    # Сохраняем город
    save_city(user_id, city)
    await message.answer(
        f"✅ Город '{city}' успешно сохранён!",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=main_kb,
            resize_keyboard=True
        )
    )

# Обработчик кнопки "Мой город"
@router.message(F.text == "Мой город")
async def my_city_weather(message: types.Message):
    user_id = message.from_user.id
    cities = load_cities()

    if str(user_id) not in cities:
        await message.answer("❌ Город не задан. Пожалуйста, введите название города.")
        return

    city = cities[str(user_id)]

    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    data = await response.json()
                    error_message = data.get("message", "Неизвестная ошибка")
                    await message.answer(f"❌ Ошибка: {error_message}")
                    return

                data = await response.json()

                temp = data["main"]["temp"]
                feels_like = data["main"]["feels_like"]
                humidity = data["main"]["humidity"]
                wind_speed = data["wind"]["speed"]
                wind_deg = data["wind"].get("deg", 0)
                description = data["weather"][0]["description"].capitalize()
                sunrise = datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M")
                sunset = datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")

                wind_direction = get_wind_direction(wind_deg)

                # Отправляем текущую погоду
                await message.answer(
                    f"🌆 Погода в {hbold(city)}:\n\n"
                    f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                    f"💧 Влажность: {humidity}%\n"
                    f"🌬️ Ветер: {wind_direction} {wind_speed} м/с\n"
                    f"🌅 Восход: 🌅 {sunrise}\n"
                    f"🌇 Закат: 🌇 {sunset}\n"
                    f"☁️ Состояние: {description}"
                )

    except Exception as e:
        await message.answer("❌ Не удалось получить данные. Проверьте название города.")

# Обработчик кнопки "Изменить город"
@router.message(F.text == "Изменить город")
async def change_city(message: types.Message):
    await message.answer(
        "Введите новое название города:",
        reply_markup=types.ReplyKeyboardRemove()
    )