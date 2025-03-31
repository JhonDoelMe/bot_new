import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from handlers import router

logger = logging.getLogger(__name__)

# Инициализация бота с настройками по умолчанию
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()
dp.include_router(router)

async def main():
    """
    Основная функция запуска бота.
    Реализована обработка исключений и корректное завершение работы с закрытием сессии.
    """
    try:
        logger.info("Бот запущен и начинает polling.")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Polling завершился с ошибкой: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен и сессия закрыта.")

if __name__ == "__main__":
    asyncio.run(main())
