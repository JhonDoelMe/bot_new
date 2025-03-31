import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from datetime import datetime
import logging
import aiohttp

from config import BOT_TOKEN, WEATHER_API_KEY
from handlers import router
from utils import load_reminders, load_cities

logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.include_router(router)

async def send_morning_reminders(bot: Bot):
    """
    Ежедневная задача для отправки напоминаний пользователям.
    Отправляет прогноз погоды в 8:00 утра по городам, сохранённым у пользователей.
    """
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:  # Проверяем, что сейчас 8:00
            reminders = load_reminders()
            cities = load_cities()

            for user_id, active in reminders.items():
                if active and str(user_id) in cities:
                    city = cities[str(user_id)]
                    try:
                        async with aiohttp.ClientSession() as session:
                            url = (
                                f"https://api.openweathermap.org/data/2.5/weather?"
                                f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
                            )
                            async with session.get(url, timeout=10) as response:
                                data = await response.json()
                                if response.status == 200:
                                    temp = data["main"]["temp"]
                                    description = data["weather"][0]["description"].capitalize()
                                    message = (
                                        f"🌤️ Доброе утро!\n"
                                        f"Погода в {city} сегодня:\n"
                                        f"🌡️ Температура: {temp}°C\n"
                                        f"☁️ Состояние: {description}"
                                    )
                                    await bot.send_message(chat_id=user_id, text=message)
                    except Exception as e:
                        logger.error(f"Ошибка отправки напоминания пользователю {user_id}: {e}")
        await asyncio.sleep(60)  # Проверяем каждые 60 секунд

async def main():
    """
    Основная функция для запуска бота и напоминаний.
    """
    try:
        logger.info("Бот запущен.")
        asyncio.create_task(send_morning_reminders(bot))
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка в основном процессе: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен.")

if __name__ == "__main__":
    asyncio.run(main())
