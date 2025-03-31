import os
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

# --- Загрузка токенов ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# --- Клавиатура с кнопками городов ---
weather_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
weather_kb.add(
    KeyboardButton("Москва"),
    KeyboardButton("Санкт-Петербург"),
    KeyboardButton("Киев"),
    KeyboardButton("Минск")
)

# --- Команда /start ---
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply(
        "🌤️ Привет! Я бот погоды.\n"
        "Выбери город или напиши свой:",
        reply_markup=weather_kb
    )

# --- Обработка текстовых сообщений ---
@dp.message_handler()
async def get_weather(message: types.Message):
    city = message.text.strip().lower()
    
    try:
        # Запрос к API OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()

        # Проверка статуса ответа
        if response.status_code != 200:
            await message.reply("❌ Ошибка API. Попробуй позже.")
            return

        # Парсинг данных
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        weather_desc = data["weather"][0]["description"]
        icon_code = data["weather"][0]["icon"]

        # Иконки погоды
        icons = {
            "01": "☀️",  # ясно
            "02": "⛅",  # мало облаков
            "03": "☁️",  # облачно
            "04": "☁️",  # пасмурно
            "09": "🌧️",  # дождь
            "10": "🌦️",  # дождь с солнцем
            "11": "⛈️",  # гроза
            "13": "❄️",  # снег
            "50": "🌫️"   # туман
        }
        weather_icon = icons.get(icon_code[:2], "🌡️")

        # Формируем ответ
        await message.reply(
            f"{weather_icon} Погода в {city.capitalize()}:\n"
            f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
            f"💧 Влажность: {humidity}%\n"
            f"🌬️ Ветер: {wind_speed} м/с\n"
            f"☁️ Состояние: {weather_desc}"
        )
    except Exception as e:
        print(f"Ошибка: {e}")  # Для отладки
        await message.reply("❌ Город не найден или произошла ошибка.")

# --- Запуск бота ---
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)