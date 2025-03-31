# bot_new/main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage # Добавили хранилище FSM

# Импортируем конфиг и роутеры
from config import BOT_TOKEN
from common_handlers import router as common_router
from city_management import router as city_router
from weather import router as weather_router
from currency import router as currency_router
from other_handlers import router as other_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)
logger = logging.getLogger(__name__)


async def main():
    """
    Основная функция запуска бота.
    """
    if not BOT_TOKEN:
        logger.critical("Невозможно запустить бота без BOT_TOKEN!")
        return

    # Инициализация хранилища FSM (в памяти)
    # Для продакшена лучше использовать RedisStorage или другое персистентное хранилище
    storage = MemoryStorage()

    # Инициализация бота
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage) # Передаем хранилище в диспетчер

    # Регистрация роутеров
    # Порядок важен: сначала более специфичные, потом общие
    dp.include_router(common_router)      # Общие команды (/start, Назад)
    dp.include_router(city_router)        # Управление городом (включая FSM)
    dp.include_router(weather_router)     # Модуль "Погода"
    dp.include_router(currency_router)    # Модуль "Курс валют"
    dp.include_router(other_router)       # Прочие кнопки ("Тревога")
    # Роутер для неизвестных команд должен идти последним, если он есть в common_handlers

    # Удаляем вебхук перед запуском поллинга (на всякий случай)
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Запуск бота...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        # allowed_updates помогает обрабатывать только нужные типы апдейтов
    except Exception as e:
        logger.critical(f"Критическая ошибка при работе бота: {e}", exc_info=True)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Завершение работы бота по команде.")