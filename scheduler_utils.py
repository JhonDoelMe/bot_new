import schedule
import time
from db_utils import connect_db
import weather
from telebot import TeleBot
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
BOT_TOKEN = config['bot']['token']
bot = TeleBot(BOT_TOKEN)

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

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)