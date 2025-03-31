from aiogram import Router, types
from aiogram.filters import Command

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

@router.message(types.Text("Назад в меню"))
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
