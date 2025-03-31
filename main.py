import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import logging

from config import BOT_TOKEN
from main_menu import router as main_menu_router  # Основное меню
from handlers import router as weather_router     # Модуль "Погода"
from currency import router as currency_router    # Модуль "Курс валют"

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()

# Регистрация маршрутов
dp.include_router(main_menu_router)  # Основное меню
dp.include_router(weather_router)   # Модуль "Погода"
dp.include_router(currency_router)  # Модуль "Курс валют"

async def main():
    """
    Основная функция запуска бота.
    """
    try:
        logger.info("Бот успешно запущен.")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка в процессе запуска бота: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен.")

if __name__ == "__main__":
    asyncio.run(main())
