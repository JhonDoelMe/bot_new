import telebot
import configparser
import schedule
import time
import threading
from db_utils import connect_db, create_tables
from scheduler_utils import send_morning_weather_reminder, run_scheduler
from weather_handlers import setup_weather_handlers
from currency_handlers import setup_currency_handlers
from core_handlers import setup_core_handlers, user_states
from keyboards import create_main_menu

# --- Чтение конфигурации из файла config.ini ---
config = configparser.ConfigParser()
config.read('config.ini')
BOT_TOKEN = config['bot']['token']

# --- Инициализация бота ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- Создание таблиц в базе данных ---
create_tables()

# --- Планирование утреннего напоминания ---
schedule.every().day.at("08:00").do(send_morning_weather_reminder)

# --- Запуск планировщика в отдельном потоке ---
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# --- Настройка обработчиков ---
setup_core_handlers(bot)
setup_weather_handlers(bot)
setup_currency_handlers(bot)

# --- Запуск бота ---
if __name__ == '__main__':
    bot.polling(none_stop=True)