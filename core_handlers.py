from telebot import TeleBot
from keyboards import create_main_menu
from db_utils import connect_db
from weather_handlers import setup_weather_handlers, handle_any_message_weather, handle_any_message_save_city, handle_any_message_new_city
from currency_handlers import setup_currency_handlers

user_states = {}

def setup_core_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        bot.reply_to(message, "Привет! Это универсальный помощник. Выберите пункт меню:", reply_markup=create_main_menu())

    @bot.message_handler(func=lambda message: message.text == "⬅️ Назад в меню")
    def handle_back_to_menu(message):
        bot.reply_to(message, "Возвращаемся в главное меню:", reply_markup=create_main_menu())

    @bot.message_handler(func=lambda message: True)
    def handle_any_message(message):
        user_id = message.from_user.id
        if user_id in user_states:
            if user_states[user_id] == "waiting_for_city":
                handle_any_message_weather(bot, message)
            elif user_states[user_id] == "waiting_for_save_city":
                handle_any_message_save_city(bot, message, user_states)
            elif user_states[user_id] == "waiting_for_new_city":
                handle_any_message_new_city(bot, message)
        elif message.text == "☀️ Погода":
            from weather_handlers import handle_weather_button
            handle_weather_button(message)
        elif message.text == "💰 Курсы валют":
            from currency_handlers import handle_exchange_button
            handle_exchange_button(message)
        elif message.text == "⬅️ Назад в меню":
            handle_back_to_menu(message)
        elif message.text == "✏️ Изменить город":
            from weather_handlers import handle_change_city
            handle_change_city(message)
        elif message.text == "🔔 Вкл/Выкл напоминание":
            from weather_handlers import handle_remind_morning
            handle_remind_morning(message)
        elif message.text == "🔄 Обновить прогноз":
            from weather_handlers import handle_refresh_weather
            handle_refresh_weather(message)
        elif message.text == "🔄 Обновить курс":
            from currency_handlers import handle_refresh_exchange
            handle_refresh_exchange(message)
        elif message.text.startswith('/'):
            pass # Игнорируем другие команды, если они не обработаны явно

    @bot.message_handler(commands=['alert'])
    def send_air_raid_alert(message):
        bot.reply_to(message, "Функция временно отключена.", reply_markup=create_main_menu())