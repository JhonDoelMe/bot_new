# bot_new/keyboards.py
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

logger = logging.getLogger(__name__)

# --- ОСНОВНОЕ МЕНЮ ---
kb_weather_text = "Погода"
kb_currency_text = "Курс валют"
kb_my_city_text = "Мой город"
kb_change_city_text = "Изменить город"
kb_alert_text = "Тревога" # Оставляем текст, но без эмодзи

main_menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=kb_weather_text), KeyboardButton(text=kb_currency_text)],
        [KeyboardButton(text=kb_my_city_text), KeyboardButton(text=kb_change_city_text)],
        [KeyboardButton(text=kb_alert_text)],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню:"
)
# Логируем текст кнопок при создании, чтобы убедиться, что он правильный
logger.debug(f"main_menu_kb defined. Button texts: "
             f"'{kb_weather_text}', '{kb_currency_text}', '{kb_my_city_text}', "
             f"'{kb_change_city_text}', '{kb_alert_text}'")


# --- ОБЩИЕ КНОПКИ ---
kb_back_text = "Назад в меню"
kb_cancel_text = "Отмена"


# --- ПОГОДА ---
kb_get_weather_now_text = "Узнать погоду сейчас"

weather_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=kb_get_weather_now_text)],
        [KeyboardButton(text=kb_back_text)] # Используем общую кнопку
    ],
    resize_keyboard=True
)
logger.debug(f"weather_kb defined. Button texts: '{kb_get_weather_now_text}', '{kb_back_text}'")


# --- КУРС ВАЛЮТ ---
currency_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=kb_back_text)] # Используем общую кнопку
    ],
    resize_keyboard=True
)
logger.debug(f"currency_kb defined. Button text: '{kb_back_text}'")


# --- ОТМЕНА FSM ---
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=kb_cancel_text)] # Используем общую кнопку
    ],
    resize_keyboard=True
)
logger.debug(f"cancel_kb defined. Button text: '{kb_cancel_text}'")