import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hbold
from dotenv import load_dotenv
import aiohttp
from aiogram import BaseMiddleware
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загрузка конфигурации
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not BOT_TOKEN or not WEATHER_API_KEY:
    raise ValueError("Необходимо указать BOT_TOKEN и WEATHER_API_KEY в .env файле.")

# Middleware для ограничения частоты запросов
class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 5.0):
        """
        :param limit: Минимальное время (в секундах) между запросами
        """
        self.limit = limit
        self.users = {}

    async def __call__(self, handler, event: types.Message, data):
        user_id = event.from_user.id
        current_time = datetime.now()

        # Проверяем, когда пользователь последний раз отправлял запрос
        if user_id in self.users:
            last_time = self.users[user_id]
            if current_time - last_time < timedelta(seconds=self.limit):
                await event.answer("⏳ Пожалуйста, подождите перед следующим запросом.")
                return

        # Обновляем время последнего запроса
        self.users[user_id] = current_time
        return await handler(event, data)

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
    # Добавляем middleware
    throttling_middleware = ThrottlingMiddleware(limit=5.0)  # Ограничение: 1 запрос в 5 секунд
    dp.message.middleware(throttling_middleware)

    logger.info("Бот запущен.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())