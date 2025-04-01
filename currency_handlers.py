from telebot import TeleBot
from keyboards import create_exchange_menu
import currency

def setup_currency_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda message: message.text == "💰 Курсы валют")
    def handle_exchange_button(message):
        bot.reply_to(message, "Выберите действие:", reply_markup=create_exchange_menu())

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