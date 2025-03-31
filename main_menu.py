from aiogram import Router, types, F

router = Router()

# Клавиатура основного меню
main_menu_kb = [
    [types.KeyboardButton(text="Погода")],
    [types.KeyboardButton(text="Курс валют")],
    [types.KeyboardButton(text="Тревога")]
]

@router.message(F.text.lower() == "назад в меню")
async def back_to_main_menu(message: types.Message):
    """
    Обработчик для кнопки "Назад в меню".
    Возвращает пользователя в главное меню.
    """
    await message.answer(
        "📋 Вы в главном меню. Выберите действие:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=main_menu_kb,
            resize_keyboard=True
        )
    )
