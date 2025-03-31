import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from aiogram.utils.rate_limit import rate_limit
from dotenv import load_dotenv
import aiohttp

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
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Клавиатура
weather_kb = [
    [types.KeyboardButton(text="Москва")],
    [types.KeyboardButton(text="Санкт-Петербург")],
    [types.KeyboardButton(text="Киев")]
]

# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"🌤️ Привет, {hbold(message.from_user.full_name)}!\n"
        "Отправь мне название города или выбери из кнопок:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=weather_kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите город"
        )
    )

# Обработчик погоды
@rate_limit(limit=5, key="weather")
@dp.message()
async def get_weather(message: types.Message):
    city = message.text.strip()
    if not city.isprintable():
        await message.answer("❌ Название города содержит недопустимые символы.")
        return

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
                wind = data["wind"]["speed"]
                description = data["weather"][0]["description"].capitalize()

                await message.answer(
                    f"🌆 Погода в {hbold(city)}:\n\n"
                    f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                    f"💧 Влажность: {humidity}%\n"
                    f"🌬️ Ветер: {wind} м/с\n"
                    f"☁️ Состояние: {description}"
                )
    except asyncio.TimeoutError:
        await message.answer("❌ Превышено время ожидания ответа от сервера.")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await message.answer("❌ Не удалось получить данные. Проверьте название города.")

# Запуск бота
async def main():
    logger.info("Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())