from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F

router = Router()

# Клавиатура основного меню
main_menu_kb = [
    [types.KeyboardButton(text="Погода")],
    [types.KeyboardButton(text="Курс валют")],
    [types.KeyboardButton(text="Тревога")]
]

@router.message(Command(commands=["start"]))
async def start_command(message: types.Message):
    """
    Обработчик команды /start.
    Показывает приветственное сообщение и основное меню.
    """
    await message.answer(
        "👋 Добро пожаловать! Я ваш помощник. Выберите, чем я могу вам помочь:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=main_menu_kb,
            resize_keyboard=True
        )
    )

@router.message(F.text == "Назад в меню")
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

@router.message(F.text == "Погода")
async def go_to_weather(message: types.Message):
    """
    Обработчик кнопки "Погода".
    Перенаправляет пользователя в модуль погоды.
    """
    from handlers import weather_kb  # Импорт клавиатуры из модуля погоды
    await message.answer(
        "🌤️ Вы перешли в модуль погоды. Выберите действие:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=weather_kb,
            resize_keyboard=True
        )
    )

@router.message(F.text == "Тревога")
async def go_to_alerts(message: types.Message):
    """
    Обработчик кнопки "Тревога".
    Перенаправляет пользователя в модуль тревог.
    """
    await message.answer(
        "🚨 Модуль тревог (в разработке). Здесь можно настроить уведомления.",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text="Назад в меню")]],
            resize_keyboard=True
        )
    )
