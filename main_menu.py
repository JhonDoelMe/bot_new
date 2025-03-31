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

@router.message(F.text.lower() == "погода")
async def go_to_weather(message: types.Message):
    """
    Обработчик кнопки "Погода".
    Перенаправляет пользователя в модуль прогноза погоды.
    """
    from handlers import weather_kb  # Импорт существующей клавиатуры из модуля погоды
    await message.answer(
        "🌤️ Вы перешли в модуль погоды. Выберите действие:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=weather_kb,
            resize_keyboard=True
        )
    )

@router.message(F.text.lower() == "курс валют")
async def go_to_currency(message: types.Message):
    """
    Обработчик кнопки "Курс валют".
    Перенаправляет пользователя в модуль курсов валют.
    """
    await message.answer(
        "💰 Вы перешли в модуль курсов валют (в разработке).",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Назад в меню")]],
            resize_keyboard=True
        )
    )

@router.message(F.text.lower() == "тревога")
async def go_to_alerts(message: types.Message):
    """
    Обработчик кнопки "Тревога".
    Перенаправляет пользователя в модуль тревожных уведомлений.
    """
    await message.answer(
        "🚨 Модуль тревог (в разработке). Здесь можно настроить уведомления.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Назад в меню")]],
            resize_keyboard=True
        )
    )
