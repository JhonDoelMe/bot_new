import telebot
import sqlite3
import configparser
import weather
import currency  # Добавляем импорт модуля currency

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

# --- Обработчик команды /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    conn, cursor = connect_db()
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
        bot.reply_to(message, "Привет! Это универсальный помощник. Функционал в разработке...")
    else:
        bot.reply_to(message, "С возвращением! Функционал в разработке...")
    conn.close()

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

# --- Запуск бота ---
if __name__ == '__main__':
    create_tables() # Создаем таблицы при запуске бота
    bot.polling(none_stop=True)