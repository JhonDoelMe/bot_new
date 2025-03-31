from aiogram import Router, types
from aiogram.filters import Command
from aiogram import F
from weather import weather_kb  # Импорт клавиатуры из weather.py

router = Router()

# Клавиатура основного меню
main_menu_kb = [
    [types.KeyboardButton(text="Погода")],
    [types.KeyboardButton(text="Курс валют")],
    [types.KeyboardButton(text="Тревога")],
    [types.KeyboardButton(text="Мой город")],  # Добавлена кнопка "Мой город"
    [types.KeyboardButton(text="Изменить город")]  # Добавлена кнопка "Изменить город"
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

@router.message(F.text == "Погода")
async def go_to_weather(message: types.Message):
    """
    Обработчик кнопки "Погода".
    Перенаправляет пользователя в модуль погоды.
    """
    await message.answer(
        "🌤️ Вы перешли в модуль погоды. Выберите действие:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=weather_kb,  # Используем клавиатуру для погоды
            resize_keyboard=True
        )
    )
