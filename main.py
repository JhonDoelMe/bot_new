import telebot
import sqlite3
import configparser
import weather
import currency
import air_raid
from telebot.types import ReplyKeyboardMarkup, KeyboardButton # Добавляем импорты для меню

# --- Чтение конфигурации из файла config.ini ---
config = configparser.ConfigParser()
config.read('config.ini')
BOT_TOKEN = config['bot']['token']
DATABASE_NAME = "assistant_bot.db"

# --- Инициализация бота ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- Подключение к базе данных ---
def connect_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn, conn.cursor()

# --- Создание таблиц в базе данных (если их нет) ---
def create_tables():
    conn, cursor = connect_db()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        preferred_location TEXT,
        preferred_currencies TEXT,
        notifications_enabled INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location TEXT,
        timestamp TIMESTAMP,
        temperature REAL,
        humidity REAL,
        wind_speed REAL,
        description TEXT,
        raw_data TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS currency_rates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        base_currency TEXT,
        target_currency TEXT,
        rate REAL,
        timestamp TIMESTAMP,
        raw_data TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS air_raid_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        region TEXT,
        status TEXT,
        timestamp TIMESTAMP,
        raw_data TEXT
    )
    """)
    conn.commit()
    conn.close()

# --- Функция для создания основного меню ---
def create_main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_weather = KeyboardButton("Погода")
    btn_exchange = KeyboardButton("Курсы валют")
    btn_alert = KeyboardButton("Воздушная тревога")
    markup.row(btn_weather)
    markup.row(btn_exchange)
    markup.row(btn_alert)
    return markup

# --- Обработчик команды /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    conn, cursor = connect_db()
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        bot.reply_to(message, "Привет! Это универсальный помощник. Выберите пункт меню:", reply_markup=create_main_menu())
    else:
        bot.reply_to(message, "С возвращением! Выберите пункт меню:", reply_markup=create_main_menu())
    conn.close()

# --- Обработчик нажатия на кнопку "Погода" ---
@bot.message_handler(func=lambda message: message.text == "Погода")
def handle_weather_button(message):
    bot.reply_to(message, "Введите название города, для которого вы хотите узнать погоду:")
    # Здесь можно добавить логику для ожидания следующего сообщения от пользователя с названием города
    # Пока что просто выведем подсказку
    pass

# --- Обработчик нажатия на кнопку "Курсы валют" ---
@bot.message_handler(func=lambda message: message.text == "Курсы валют")
def handle_exchange_button(message):
    send_exchange_rates(message) # Используем существующую функцию для обработки команды /exchange

# --- Обработчик нажатия на кнопку "Воздушная тревога" ---
@bot.message_handler(func=lambda message: message.text == "Воздушная тревога")
def handle_alert_button(message):
    send_air_raid_alert(message) # Используем существующую функцию для обработки команды /alert

# --- Обработчик команды /weather ---
@bot.message_handler(commands=['weather'])
def send_weather_info(message):
    try:
        city = message.text.split()[1]  # Получаем название города из сообщения пользователя
        weather_data = weather.get_weather(city)
        if weather_data:
            formatted_weather = weather.format_weather_data(weather_data)
            bot.reply_to(message, formatted_weather)
        else:
            bot.reply_to(message, f"Не удалось получить погоду для города {city}.")
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите название города, например: /weather Днепр")
    except Exception as e:
        print(f"Произошла ошибка при обработке команды /weather: {e}")
        bot.reply_to(message, "Произошла непредвиденная ошибка при получении погоды.")

# --- Обработчик команды /exchange ---
@bot.message_handler(commands=['exchange'])
def send_exchange_rates(message):
    try:
        exchange_rates_data = currency.get_exchange_rates()
        if exchange_rates_data:
            formatted_rates = currency.format_exchange_rates(exchange_rates_data)
            bot.reply_to(message, formatted_rates)
        else:
            bot.reply_to(message, "Не удалось получить курсы валют от НБУ.")
    except Exception as e:
        print(f"Произошла ошибка при обработке команды /exchange: {e}")
        bot.reply_to(message, "Произошла непредвиденная ошибка при получении курсов валют.")

# --- Обработчик команды /alert ---
@bot.message_handler(commands=['alert'])
def send_air_raid_alert(message):
    region = "Дніпропетровська область"  # Указываем регион по умолчанию
    try:
        alert_status = air_raid.get_air_raid_status(region)
        if alert_status is not None:
            formatted_message = air_raid.format_air_raid_message(region, alert_status)
            bot.reply_to(message, formatted_message)
        else:
            bot.reply_to(message, f"Не удалось получить информацию о воздушной тревоге для {region}.")
    except Exception as e:
        print(f"Произошла ошибка при обработке команды /alert: {e}")
        bot.reply_to(message, "Произошла непредвиденная ошибка при получении информации о тревоге.")

# --- Запуск бота ---
if __name__ == '__main__':
    create_tables() # Создаем таблицы при запуске бота
    bot.polling(none_stop=True)