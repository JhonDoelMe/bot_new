import os
import json
import logging
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv
import aiohttp
from aiogram.client.default import DefaultBotProperties

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not BOT_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Необходимо указать BOT_TOKEN и WEATHER_API_KEY в .env файле.")

# Инициализация бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Путь к файлу с городами
CITIES_FILE = "cities.json"

# Функция для чтения данных из файла
def load_cities():
    if not os.path.exists(CITIES_FILE):
        with open(CITIES_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False)
    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

# Функция для записи данных в файл
def save_city(user_id, city):
    cities = load_cities()
    cities[str(user_id)] = city
    with open(CITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(cities, f, ensure_ascii=False)

# Функция для определения направления ветра
def get_wind_direction(degrees):
    if 337.5 <= degrees <= 360 or 0 <= degrees < 22.5:
        return "⬆️ Север"
    elif 22.5 <= degrees < 67.5:
        return "↗️ Северо-восток"
    elif 67.5 <= degrees < 112.5:
        return "➡️ Восток"
    elif 112.5 <= degrees < 157.5:
        return "↘️ Юго-восток"
    elif 157.5 <= degrees < 202.5:
        return "⬇️ Юг"
    elif 202.5 <= degrees < 247.5:
        return "↙️ Юго-запад"
    elif 247.5 <= degrees < 292.5:
        return "⬅️ Запад"
    elif 292.5 <= degrees < 337.5:
        return "↖️ Северо-запад"

# Клавиатура
main_kb = [
    [types.KeyboardButton(text="Мой город")],
    [types.KeyboardButton(text="Изменить город")]
]

# Команда /start
@dp.message(Command("start"))
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
@dp.message(Text)
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
@dp.message(Text("Мой город"))
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
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Не удалось получить данные. Проверьте название города.")

# Обработчик кнопки "Изменить город"
@dp.message(Text("Изменить город"))
async def change_city(message: types.Message):
    await message.answer(
        "Введите новое название города:",
        reply_markup=types.ReplyKeyboardRemove()
    )

# Запуск бота
async def main():
    logger.info("Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())