# bot_new/other_handlers.py
import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter

# Импортируем ТОЛЬКО клавиатуры и тексты кнопок из keyboards
from keyboards import (
    main_menu_kb,
    kb_alert_text
)

router = Router()
logger = logging.getLogger(__name__)

# Фильтр для "Тревога"
@router.message(StateFilter(None), F.text == kb_alert_text)
async def handle_alert_button(message: types.Message):
    # ... (логика без изменений) ...
    logger.info(f"Пользователь {message.from_user.id} нажал '{kb_alert_text}'")
    await message.answer(
        "ℹ️ Функция оповещения о тревогах находится в разработке и будет добавлена позже.",
        reply_markup=main_menu_kb
    )