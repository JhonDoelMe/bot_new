import os
import logging
import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
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

# Клавиатура
weather_kb = [
    [types.KeyboardButton(text="Москва")],
    [types.KeyboardButton(text="Санкт-Петербург")],
    [types.KeyboardButton(text="Киев")]
]

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
@dp.message()
async def get_weather(message: types.Message):
    city = message.text.strip()
    if not city.isprintable():
        await message.answer("❌ Название города содержит недопустимые символы.")
        return

    try:
        # Текущая погода
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

        # Прогноз на завтра
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        async with session.get(forecast_url, timeout=10) as forecast_response:
            if forecast_response.status != 200:
                await message.answer("❌ Не удалось получить прогноз погоды.")
                return

            forecast_data = await forecast_response.json()
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_date = tomorrow.strftime("%Y-%m-%d")

            # Ищем прогноз на завтра
            for item in forecast_data["list"]:
                forecast_time = item["dt_txt"].split()[0]
                if forecast_time == tomorrow_date:
                    temp_tomorrow = item["main"]["temp"]
                    feels_like_tomorrow = item["main"]["feels_like"]
                    description_tomorrow = item["weather"][0]["description"].capitalize()
                    break
            else:
                await message.answer("❌ Прогноз на завтра недоступен.")
                return

            # Отправляем прогноз на завтра
            await message.answer(
                f" прогноз на завтра ({tomorrow_date}):\n\n"
                f"🌡️ Температура: {temp_tomorrow}°C (ощущается как {feels_like_tomorrow}°C)\n"
                f"☁️ Состояние: {description_tomorrow}"
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