from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
import aiohttp
from datetime import datetime, timedelta
import logging

from config import WEATHER_API_KEY
from utils import load_cities, save_city, get_wind_direction, load_reminders, save_reminder

logger = logging.getLogger(__name__)

router = Router()

# Клавиатура модуля "Погода"
weather_kb = [
    [types.KeyboardButton(text="Мой город")],
    [types.KeyboardButton(text="Изменить город")],
    [types.KeyboardButton(text="Напоминать утром")],
    [types.KeyboardButton(text="Отключить напоминание")],
    [types.KeyboardButton(text="Назад в меню")]
]

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start.
    Если город не сохранён, просит ввести название города,
    иначе предлагает выбрать действие в модуле "Погода".
    """
    user_id = message.from_user.id
    cities = load_cities()

    if str(user_id) not in cities:
        await message.answer(
            "🌤️ Привет! Введите название вашего города:",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            "🌤️ Привет! Выберите действие:",
            reply_markup=types.ReplyKeyboardMarkup(
                keyboard=weather_kb,
                resize_keyboard=True
            )
        )

@router.message(F.text.lower() == "мой город")
async def my_city_weather(message: types.Message):
    """
    Обработчик для кнопки "Мой город".
    Выводит текущую погоду для сохранённого пользователем города и прогноз на завтра.
    """
    user_id = message.from_user.id
    cities = load_cities()

    if str(user_id) not in cities:
        await message.answer("❌ Город не задан. Пожалуйста, введите название города.")
        return

    city = cities[str(user_id)]
    logger.info(f"Получен запрос погоды для города: '{city}'")

    try:
        async with aiohttp.ClientSession() as session:
            # Запрос текущей погоды
            current_weather_url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            )

            # Запрос прогноза на несколько дней (на завтра)
            forecast_url = (
                f"https://api.openweathermap.org/data/2.5/forecast?"
                f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            )

            # Выполняем оба запроса параллельно
            async with session.get(current_weather_url, timeout=10) as current_response, \
                       session.get(forecast_url, timeout=10) as forecast_response:

                current_data = await current_response.json()
                forecast_data = await forecast_response.json()

                # Проверка ответа для текущей погоды
                if current_response.status != 200:
                    error_message = current_data.get("message", "Неизвестная ошибка")
                    await message.answer(f"❌ Ошибка: {error_message}")
                    return

                # Проверка ответа для прогноза
                if forecast_response.status != 200:
                    error_message = forecast_data.get("message", "Неизвестная ошибка")
                    await message.answer(f"❌ Ошибка при получении прогноза: {error_message}")
                    return

                # Формируем сообщение для текущей погоды
                temp = current_data["main"]["temp"]
                feels_like = current_data["main"]["feels_like"]
                humidity = current_data["main"]["humidity"]
                wind_speed = current_data["wind"]["speed"]
                wind_deg = current_data["wind"].get("deg", 0)
                description = current_data["weather"][0]["description"].capitalize()
                sunrise = datetime.fromtimestamp(current_data["sys"]["sunrise"]).strftime("%H:%M")
                sunset = datetime.fromtimestamp(current_data["sys"]["sunset"]).strftime("%H:%M")

                wind_direction = get_wind_direction(wind_deg)

                await message.answer(
                    f"🌆 Погода в {hbold(city)} сегодня:\n\n"
                    f"🌡️ Температура: {temp}°C (ощущается как {feels_like}°C)\n"
                    f"💧 Влажность: {humidity}%\n"
                    f"🌬️ Ветер: {wind_direction} {wind_speed} м/с\n"
                    f"🌅 Восход: {sunrise}\n"
                    f"🌇 Закат: {sunset}\n"
                    f"☁️ Состояние: {description}"
                )

                # Формируем сообщение для прогноза на завтра
                tomorrow_data = None
                today = datetime.now().date()

                # Ищем данные для завтрашнего дня (только по времени 12:00)
                for forecast in forecast_data["list"]:
                    forecast_time = datetime.fromtimestamp(forecast["dt"])
                    if forecast_time.date() == today + timedelta(days=1) and forecast_time.hour == 12:
                        tomorrow_data = forecast
                        break

                if tomorrow_data:
                    temp_tomorrow = tomorrow_data["main"]["temp"]
                    feels_like_tomorrow = tomorrow_data["main"]["feels_like"]
                    humidity_tomorrow = tomorrow_data["main"]["humidity"]
                    wind_speed_tomorrow = tomorrow_data["wind"]["speed"]
                    wind_deg_tomorrow = tomorrow_data["wind"].get("deg", 0)
                    description_tomorrow = tomorrow_data["weather"][0]["description"].capitalize()

                    wind_direction_tomorrow = get_wind_direction(wind_deg_tomorrow)

                    await message.answer(
                        f"🌆 Погода в {hbold(city)} завтра (время: 12:00):\n\n"
                        f"🌡️ Температура: {temp_tomorrow}°C (ощущается как {feels_like_tomorrow}°C)\n"
                        f"💧 Влажность: {humidity_tomorrow}%\n"
                        f"🌬️ Ветер: {wind_direction_tomorrow} {wind_speed_tomorrow} м/с\n"
                        f"☁️ Состояние: {description_tomorrow}"
                    )
                else:
                    await message.answer("⚠️ Не удалось получить прогноз на завтра.")

    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при запросе данных: {e}")
        await message.answer("❌ Не удалось получить данные. Проверьте название города.")
    except Exception as e:
        logger.error(f"Необработанная ошибка при получении погоды: {e}")
        await message.answer("❌ Что-то пошло не так. Попробуйте позже.")

@router.message(F.text.lower() == "напоминать утром")
async def enable_reminder(message: types.Message):
    """
    Обработчик для кнопки "Напоминать утром".
    Включает напоминания для пользователя.
    """
    user_id = message.from_user.id
    reminders = load_reminders()
    reminders[str(user_id)] = True
    save_reminder(reminders)
    await message.answer("✅ Напоминания включены! Каждый день в 8:00 вы будете получать прогноз погоды.")

@router.message(F.text.lower() == "отключить напоминание")
async def disable_reminder(message: types.Message):
    """
    Обработчик для кнопки "Отключить напоминание".
    Отключает напоминания для пользователя.
    """
    user_id = message.from_user.id
    reminders = load_reminders()
    if str(user_id) in reminders:
        del reminders[str(user_id)]
        save_reminder(reminders)
        await message.answer("❌ Напоминания отключены.")
    else:
        await message.answer("⚠️ Напоминания уже отключены.")

@router.message(F.text.lower() == "изменить город")
async def change_city(message: types.Message):
    """
    Обработчик для кнопки "Изменить город".
    Запрашивает у пользователя новое название города, сбрасывая текущую клавиатуру.
    """
    await message.answer(
        "Введите новое название города:",
        reply_markup=types.ReplyKeyboardRemove()
    )

@router.message(F.text.lower() == "назад в меню")
async def back_to_main_menu(message: types.Message):
    """
    Обработчик для кнопки "Назад в меню".
    Возвращает пользователя в главное меню.
    """
    from main_menu import main_menu_kb  # Импорт клавиатуры основного меню
    await message.answer(
        "📋 Вы в главном меню. Выберите действие:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=main_menu_kb,
            resize_keyboard=True
        )
    )
