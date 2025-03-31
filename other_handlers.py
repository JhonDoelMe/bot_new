# bot_new/other_handlers.py
import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter

from keyboards import main_menu_kb # Импортируем клавиатуру

router = Router()
logger = logging.getLogger(__name__)

@router.message(StateFilter(None), F.text == "Тревога 🚨") # Точное совпадение
async def handle_alert_button(message: types.Message):
    """
    Обработчик кнопки "Тревога".
    Пока является заглушкой.
    """
    logger.info(f"Пользователь {message.from_user.id} нажал 'Тревога'")
    await message.answer(
        "ℹ️ Функция оповещения о тревогах находится в разработке и будет добавлена позже.",
        reply_markup=main_menu_kb
    )

# Сюда можно добавить другие обработчики для кнопок, не относящихся к основным модулям