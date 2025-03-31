# bot_new/keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура основного меню
# Убедитесь, что здесь НЕТ лишних пробелов в конце текста кнопок
main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Погода 🌤️"), KeyboardButton(text="Курс валют 💰")],
        [KeyboardButton(text="Мой город 🏙️"), KeyboardButton(text="Изменить город ✏️")],
        [KeyboardButton(text="Тревога 🚨")], # Проверьте, что эмодзи корректный
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню:"
)

# Клавиатура модуля "Погода"
weather_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Узнать погоду сейчас 🌦️")], # Проверьте отсутствие пробелов
        [KeyboardButton(text="Назад в меню ↩️")]      # Проверьте отсутствие пробелов
    ],
    resize_keyboard=True
)

# Клавиатура модуля "Курс валют"
currency_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад в меню ↩️")] # Проверьте отсутствие пробелов
    ],
    resize_keyboard=True
)

# Клавиатура для отмены ввода города
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отмена ❌")] # Проверьте отсутствие пробелов
    ],
    resize_keyboard=True
)