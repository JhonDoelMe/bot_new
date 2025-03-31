# bot_new/keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура основного меню
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Погода 🌤️"), KeyboardButton(text="Курс валют 💰")],
        [KeyboardButton(text="Мой город 🏙️"), KeyboardButton(text="Изменить город ✏️")],
        [KeyboardButton(text="Тревога 🚨")], # Пока заглушка
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню:"
)

# Клавиатура модуля "Погода"
weather_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Узнать погоду сейчас 🌦️")],
        [KeyboardButton(text="Назад в меню ↩️")]
    ],
    resize_keyboard=True
)

# Клавиатура модуля "Курс валют"
currency_kb = ReplyKeyboardMarkup(
    keyboard=[
        # Можно добавить другие кнопки, если нужно
        [KeyboardButton(text="Назад в меню ↩️")]
    ],
    resize_keyboard=True
)

# Клавиатура для отмены ввода города
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена ❌")]
    ],
    resize_keyboard=True
)