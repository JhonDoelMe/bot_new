import telebot
import sqlite3
import configparser
import weather
import currency
import air_raid
from keyboards import create_main_menu, create_weather_preference_keyboard, create_weather_menu, create_exchange_menu, create_alert_menu
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import schedule
import time
import datetime

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
        morning_reminder_enabled INTEGER DEFAULT 0,
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
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN morning_reminder_enabled INTEGER DEFAULT 0")
        conn.commit()
        print("Столбец morning_reminder_enabled успешно добавлен в таблицу users.")
    except sqlite3.OperationalError:
        print("Столбец morning_reminder_enabled уже существует в таблице users.")
    conn.commit()
    conn.close()

# --- Словарь для хранения состояний пользователей ---
user_states = {}

# --- Функция для отправки утреннего напоминания о погоде ---
def send_morning_weather_reminder():
    conn, cursor = connect_db()
    cursor.execute("SELECT user_id, preferred_location FROM users WHERE morning_reminder_enabled=1")
    users_with_reminder = cursor.fetchall()
    conn.close()
    for user_id, preferred_location in users_with_reminder:
        if preferred_location:
            try:
                weather_data = weather.get_weather(preferred_location)
                if weather_data:
                    formatted_weather = weather.format_weather_data(weather_data)
                    bot.send_message(user_id, f"☀️ Доброе утро! Погода в вашем городе ({preferred_location}):\n\n{formatted_weather}")
            except Exception as e:
                print(f"Ошибка при отправке утреннего напоминания погоды для пользователя {user_id}: {e}")

# --- Планирование утреннего напоминания ---
schedule.every().day.at("08:00").do(send_morning_weather_reminder)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

import threading
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# --- Обработчик команды /start ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    conn, cursor = connect_db()
    cursor.execute("SELECT preferred_location FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    preferred_location = result[0] if result else None

    if preferred_location:
        bot.reply_to(message, f"Привет! С возвращением! Ваш предпочтительный город для погоды: {preferred_location}. Хотите узнать погоду сейчас?", reply_markup=create_weather_preference_keyboard())
    else:
        bot.reply_to(message, "Привет! Это универсальный помощник. Выберите пункт меню:", reply_markup=create_main_menu())
    conn.close()

# --- Обработчик ответа на предложение погоды для сохраненного города ---
@bot.message_handler(func=lambda message: message.text == "✅ Да, для моего города")
def handle_weather_preference_yes(message):
    user_id = message.from_user.id
    conn, cursor = connect_db()
    cursor.execute("SELECT preferred_location FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    preferred_location = result[0] if result else None
    conn.close()
    if preferred_location:
        try:
            weather_data = weather.get_weather(preferred_location)
            if weather_data:
                formatted_weather = weather.format_weather_data(weather_data)
                bot.reply_to(message, formatted_weather, reply_markup=create_weather_menu())
            else:
                bot.reply_to(message, f"Не удалось получить погоду для города {preferred_location}.")
        except Exception as e:
            print(f"Произошла ошибка при получении погоды: {e}")
            bot.reply_to(message, "Произошла непредвиденная ошибка при получении погоды.")
    else:
        bot.reply_to(message, "Предпочтительный город не найден. Пожалуйста, введите название города.")
        user_states[user_id] = "waiting_for_city"

# --- Обработчик ответа на предложение погоды для сохраненного города ---
@bot.message_handler(func=lambda message: message.text == "❌ Нет, ввести другой")
def handle_weather_preference_no(message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_city"
    bot.reply_to(message, "Введите название города:")

# --- Обработчик нажатия на кнопку "Погода" ---
@bot.message_handler(func=lambda message: message.text == "☀️ Погода")
def handle_weather_button(message):
    user_id = message.from_user.id
    conn, cursor = connect_db()
    cursor.execute("SELECT preferred_location FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    preferred_location = result[0] if result else None
    conn.close()
    if preferred_location:
        bot.reply_to(message, "Выберите действие:", reply_markup=create_weather_menu())
    else:
        user_states[user_id] = "waiting_for_city"
        bot.reply_to(message, "Введите название города, для которого вы хотите узнать погоду:")

# --- Обработчик нажатия на кнопку "Курсы валют" ---
@bot.message_handler(func=lambda message: message.text == "💰 Курсы валют")
def handle_exchange_button(message):
    bot.reply_to(message, "Выберите действие:", reply_markup=create_exchange_menu())

# --- Обработчик нажатия на кнопку "Воздушная тревога" ---
@bot.message_handler(func=lambda message: message.text == "🚨 Воздушная тревога")
def handle_alert_button(message):
    bot.reply_to(message, "Выберите действие:", reply_markup=create_alert_menu())

# --- Обработчик кнопки "⬅️ Назад в меню" ---
@bot.message_handler(func=lambda message: message.text == "⬅️ Назад в меню")
def handle_back_to_menu(message):
    bot.reply_to(message, "Возвращаемся в главное меню:", reply_markup=create_main_menu())

# --- Обработчик кнопки "✏️ Изменить город" ---
@bot.message_handler(func=lambda message: message.text == "✏️ Изменить город")
def handle_change_city(message):
    user_id = message.from_user.id
    user_states[user_id] = "waiting_for_new_city"
    bot.reply_to(message, "Введите название нового города:")

# --- Обработчик кнопки "🔔 Вкл/Выкл напоминание" ---
@bot.message_handler(func=lambda message: message.text == "🔔 Вкл/Выкл напоминание")
def handle_remind_morning(message):
    user_id = message.from_user.id
    conn, cursor = connect_db()
    cursor.execute("SELECT morning_reminder_enabled FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    reminder_enabled = result[0] if result else 0

    new_reminder_status = 1 if reminder_enabled == 0 else 0
    cursor.execute("UPDATE users SET morning_reminder_enabled=? WHERE user_id=?", (new_reminder_status, user_id))
    conn.commit()
    conn.close()

    if new_reminder_status == 1:
        bot.reply_to(message, "Утренние напоминания о погоде включены. Вы будете получать прогноз каждый день в 8:00.", reply_markup=create_weather_menu())
    else:
        bot.reply_to(message, "Утренние напоминания о погоде выключены.", reply_markup=create_weather_menu())

# --- Обработчик кнопки "🔄 Обновить прогноз" ---
@bot.message_handler(func=lambda message: message.text == "🔄 Обновить прогноз")
def handle_refresh_weather(message):
    user_id = message.from_user.id
    conn, cursor = connect_db()
    cursor.execute("SELECT preferred_location FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    preferred_location = result[0] if result else None
    conn.close()
    if preferred_location:
        try:
            weather_data = weather.get_weather(preferred_location)
            if weather_data:
                formatted_weather = weather.format_weather_data(weather_data)
                bot.reply_to(message, formatted_weather, reply_markup=create_weather_menu())
            else:
                bot.reply_to(message, f"Не удалось обновить погоду для города {preferred_location}.")
        except Exception as e:
            print(f"Произошла ошибка при обновлении погоды: {e}")
            bot.reply_to(message, "Произошла непредвиденная ошибка при обновлении погоды.")
    else:
        bot.reply_to(message, "Предпочтительный город не найден. Пожалуйста, введите название города.")

# --- Обработчик кнопки "🔄 Обновить курс" ---
@bot.message_handler(func=lambda message: message.text == "🔄 Обновить курс")
def handle_refresh_exchange(message):
    try:
        exchange_rates_data = currency.get_exchange_rates()
        if exchange_rates_data is not None and len(exchange_rates_data) > 0:
            formatted_rates = currency.format_exchange_rates(exchange_rates_data)
            bot.reply_to(message, formatted_rates, reply_markup=create_exchange_menu())
        else:
            bot.reply_to(message, "Не удалось получить курсы валют от НБУ.")
    except Exception as e:
        print(f"Произошла ошибка при обновлении курсов валют: {e}")
        bot.reply_to(message, "Произошла непредвиденная ошибка при получении курсов валют.")

# --- Обработчик ввода региона для воздушной тревоги и обработка кнопок тревоги ---
@bot.message_handler(func=lambda message: True)
def handle_any_message(message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id] == "waiting_for_alert_region":
        region = message.text
        del user_states[user_id]
        print(f"Получен запрос на тревогу для региона: {region}")
        try:
            alert_status = air_raid.get_air_raid_status(region)
            print(f"Статус тревоги, полученный из air_raid: {alert_status}")
            if alert_status:
                formatted_message = air_raid.format_air_raid_message(region, alert_status)
                print(f"Форматированное сообщение: {formatted_message}")
                bot.reply_to(message, formatted_message, reply_markup=create_alert_menu())
            else:
                print(f"Информация о тревоге для региона '{region}' не найдена.")
                bot.reply_to(message, f"Информация о воздушной тревоге для региона '{region}' не найдена.", reply_markup=create_alert_menu())
        except Exception as e:
            print(f"Произошла ошибка при получении информации о тревоге в main.py: {e}")
            bot.reply_to(message, "Произошла непредвиденная ошибка при получении информации о тревоге.", reply_markup=create_alert_menu())
    elif message.text == "☀️ Погода":
        handle_weather_button(message)
    elif message.text == "💰 Курсы валют":
        handle_exchange_button(message)
    elif message.text == "🚨 Воздушная тревога":
        handle_alert_button(message)
    elif message.text == "⬅️ Назад в меню":
        handle_back_to_menu(message)
    elif message.text == "✏️ Изменить город":
        handle_change_city(message)
    elif message.text == "🔔 Вкл/Выкл напоминание":
        handle_remind_morning(message)
    elif message.text == "🔄 Обновить прогноз":
        handle_refresh_weather(message)
    elif message.text == "🔄 Обновить курс":
        handle_refresh_exchange(message)
    elif message.text == "📄 Список областей":
        alerts_list = air_raid.get_alerts_list_xml()
        bot.reply_to(message, alerts_list, reply_markup=create_alert_menu())
    elif message.text == "🗺️ Показать карту":
        map_image = air_raid.get_alerts_map_image()
        if map_image:
            bot.send_photo(message.chat.id, map_image, reply_markup=create_alert_menu())
        else:
            bot.reply_to(message, "Не удалось загрузить карту тревог.", reply_markup=create_alert_menu())
    elif message.text == "📍 Узнать по региону":
        user_id = message.from_user.id
        bot.reply_to(message, "Введите название региона:", reply_markup=create_alert_menu())
        user_states[user_id] = "waiting_for_alert_region"
    elif user_id in user_states and user_states[user_id] == "waiting_for_city":
        city = message.text
        del user_states[user_id]
        print(f"Тип переменной city: {type(city)}, значение: '{city}'")
        try:
            weather_data = weather.get_weather(city)
            if weather_data:
                formatted_weather = weather.format_weather_data(weather_data)
                markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                btn_yes = KeyboardButton("Да, сохранить")
                btn_no = KeyboardButton("Нет, спасибо")
                markup.row(btn_yes, btn_no)
                bot.reply_to(message, formatted_weather + "\nСохранить этот город как предпочтительный?", reply_markup=markup)
                user_states[str(user_id) + "_city_to_save"] = city
                user_states[user_id] = "waiting_for_save_city"
            else:
                bot.reply_to(message, f"Не удалось получить погоду для города {city}.")
        except Exception as e:
            print(f"Произошла ошибка при получении погоды: {e}")
            bot.reply_to(message, "Произошла непредвиденная ошибка при получении погоды.")
    elif user_id in user_states and user_states[user_id] == "waiting_for_save_city":
        if message.text == "Да, сохранить":
            city_to_save = user_states.get(str(user_id) + "_city_to_save")
            if city_to_save:
                conn, cursor = connect_db()
                cursor.execute("UPDATE users SET preferred_location=? WHERE user_id=?", (city_to_save, user_id))
                conn.commit()
                conn.close()
                bot.reply_to(message, f"Город {city_to_save} сохранен как предпочтительный.", reply_markup=create_weather_menu())
            else:
                bot.reply_to(message, "Произошла ошибка при сохранении города.", reply_markup=create_weather_menu())
        elif message.text == "Нет, спасибо":
            bot.reply_to(message, "Хорошо, не будем сохранять.", reply_markup=create_weather_menu())
        if str(user_id) + "_city_to_save" in user_states:
            del user_states[str(user_id) + "_city_to_save"]
        del user_states[user_id]
    elif user_id in user_states and user_states[user_id] == "waiting_for_new_city":
        city = message.text
        del user_states[user_id]
        conn, cursor = connect_db()
        cursor.execute("UPDATE users SET preferred_location=? WHERE user_id=?", (city, user_id))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"Предпочтительный город изменен на {city}.", reply_markup=create_weather_menu())

# --- Обработчик команды /weather ---
@bot.message_handler(commands=['weather'])
def send_weather_info(message):
    try:
        city = message.text.split()[1]  # Получаем название города из сообщения пользователя
        weather_data = weather.get_weather(city)
        if weather_data:
            formatted_weather = weather.format_weather_data(weather_data)
            bot.reply_to(message, formatted_weather, reply_markup=create_weather_menu())
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
        if exchange_rates_data is not None and len(exchange_rates_data) > 0:
            formatted_rates = currency.format_exchange_rates(exchange_rates_data)
            bot.reply_to(message, formatted_rates, reply_markup=create_exchange_menu())
        else:
            bot.reply_to(message, "Не удалось получить курсы валют от НБУ.")
    except Exception as e:
        print(f"Произошла ошибка при обработке команды /exchange: {e}")
        bot.reply_to(message, "Произошла непредвиденная ошибка при получении курсов валют.")

# --- Обработчик команды /alert ---
@bot.message_handler(commands=['alert'])
def send_air_raid_alert(message):
    try:
        region = message.text.split()[1]  # Получаем название региона из сообщения пользователя
        alert_status = air_raid.get_air_raid_status(region)
        if alert_status:
            formatted_message = air_raid.format_air_raid_message(region, alert_status)
            bot.reply_to(message, formatted_message, reply_markup=create_alert_menu())
        else:
            bot.reply_to(message, f"Информация о воздушной тревоге для региона '{region}' не найдена.")
    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите название региона, например: /alert Днепропетровская область")
    except Exception as e:
        print(f"Произошла ошибка при обработке команды /alert: {e}")
        bot.reply_to(message, "Произошла непредвиденная ошибка при получении информации о тревоге.")

# --- Запуск бота ---
if __name__ == '__main__':
    create_tables() # Создаем таблицы при запуске бота
    bot.polling(none_stop=True)