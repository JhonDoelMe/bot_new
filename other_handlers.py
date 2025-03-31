# bot_new/other_handlers.py
from aiogram import Router, types, F
from aiogram.filters import StateFilter

from keyboards import main_menu_kb # Импортируем клавиатуру

router = Router()

@router.message(StateFilter(None), F.text.lower() == "тревога 🚨")
async def handle_alert_button(message: types.Message):
    """
    Обработчик кнопки "Тревога".
    Пока является заглушкой.
    """
    await message.answer(
        "ℹ️ Функция оповещения о тревогах находится в разработке и будет добавлена позже.",
        reply_markup=main_menu_kb
    )

# Сюда можно добавить другие обработчики для кнопок, не относящихся к основным модулям