from telebot import TeleBot
from keyboards import create_weather_preference_keyboard, create_weather_menu
import weather
from db_utils import connect_db

def setup_weather_handlers(bot: TeleBot):
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
            from core_handlers import user_states
            user_states[user_id] = "waiting_for_city"

    @bot.message_handler(func=lambda message: message.text == "❌ Нет, ввести другой")
    def handle_weather_preference_no(message):
        user_id = message.from_user.id
        from core_handlers import user_states
        user_states[user_id] = "waiting_for_city"
        bot.reply_to(message, "Введите название города:")

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
            from core_handlers import user_states
            user_states[user_id] = "waiting_for_city"
            bot.reply_to(message, "Введите название города, для которого вы хотите узнать погоду:")

    @bot.message_handler(func=lambda message: message.text == "✏️ Изменить город")
    def handle_change_city(message):
        user_id = message.from_user.id
        from core_handlers import user_states
        user_states[user_id] = "waiting_for_new_city"
        bot.reply_to(message, "Введите название нового города:")

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

def handle_any_message_weather(bot: TeleBot, message):
    user_id = message.from_user.id
    city = message.text
    from core_handlers import user_states
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

def handle_any_message_save_city(bot: TeleBot, message, user_states):
    user_id = message.from_user.id
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

def handle_any_message_new_city(bot: TeleBot, message):
    user_id = message.from_user.id
    city = message.text
    from core_handlers import user_states
    del user_states[user_id]
    conn, cursor = connect_db()
    cursor.execute("UPDATE users SET preferred_location=? WHERE user_id=?", (city, user_id))
    conn.commit()
    conn.close()
    bot.reply_to(message, f"Предпочтительный город изменен на {city}.", reply_markup=create_weather_menu())