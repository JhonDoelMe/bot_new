from telebot.types import ReplyKeyboardMarkup, KeyboardButton

def create_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_weather = KeyboardButton("☀️ Погода")
    btn_exchange = KeyboardButton("💰 Курсы валют")
    btn_alert = KeyboardButton("🚨 Воздушная тревога")
    markup.row(btn_weather)
    markup.row(btn_exchange)
    markup.row(btn_alert)
    return markup

def create_weather_preference_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_yes = KeyboardButton("✅ Да, для моего города")
    btn_no = KeyboardButton("❌ Нет, ввести другой")
    markup.row(btn_yes, btn_no)
    return markup

def create_weather_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_change_city = KeyboardButton("✏️ Изменить город")
    btn_remind_morning = KeyboardButton("⏰ Напоминать утром")
    btn_back_to_menu = KeyboardButton("⬅️ Назад в меню")
    markup.row(btn_change_city)
    markup.row(btn_remind_morning)
    markup.row(btn_back_to_menu)
    return markup

def create_exchange_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back_to_menu = KeyboardButton("⬅️ Назад в меню")
    markup.row(btn_back_to_menu)
    return markup

def create_alert_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back_to_menu = KeyboardButton("⬅️ Назад в меню")
    markup.row(btn_back_to_menu)
    return markup