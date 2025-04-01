from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def create_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_weather = KeyboardButton("☀️ Погода")
    btn_exchange = KeyboardButton("💰 Курсы валют")
    # btn_alert = KeyboardButton("🚨 Воздушная тревога") # Временно отключаем кнопку тревоги
    markup.row(btn_weather)
    markup.row(btn_exchange)
    # markup.row(btn_alert) # Временно отключаем кнопку тревоги
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
    btn_refresh_weather = KeyboardButton("🔄 Обновить прогноз")
    btn_remind_morning = KeyboardButton("🔔 Вкл/Выкл напоминание")
    btn_back_to_menu = KeyboardButton("⬅️ Назад в меню")
    markup.row(btn_change_city)
    markup.row(btn_refresh_weather)
    markup.row(btn_remind_morning)
    markup.row(btn_back_to_menu)
    return markup

def create_exchange_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_refresh_exchange = KeyboardButton("🔄 Обновить курс")
    btn_back_to_menu = KeyboardButton("⬅️ Назад в меню")
    markup.row(btn_refresh_exchange)
    markup.row(btn_back_to_menu)
    return markup

# def create_alert_menu(): # Временно отключаем меню тревог
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     btn_show_map = KeyboardButton("🗺️ Показать карту")
#     btn_region_list = KeyboardButton("📄 Список областей")
#     btn_check_region = KeyboardButton("📍 Узнать по региону")
#     btn_back_to_menu = KeyboardButton("⬅️ Назад в меню")
#     markup.row(btn_check_region)
#     markup.row(btn_show_map, btn_region_list)
#     markup.row(btn_back_to_menu)
#     return markup