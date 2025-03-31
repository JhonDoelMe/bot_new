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
            current_weather_url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            )
            forecast_url = (
                f"https://api.openweathermap.org/data/2.5/forecast?"
                f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            )

            async with session.get(current_weather_url, timeout=10) as current_response, \
                       session.get(forecast_url, timeout=10) as forecast_response:

                current_data = await current_response.json()
                forecast_data = await forecast_response.json()

                # Проверка успешности запросов
                if current_response.status != 200:
                    error_message = current_data.get("message", "Неизвестная ошибка")
                    await message.answer(f"❌ Ошибка: {error_message}")
                    return

                if forecast_response.status != 200:
                    error_message = forecast_data.get("message", "Неизвестная ошибка")
                    await message.answer(f"❌ Ошибка при получении прогноза: {error_message}")
                    return

                # Формирование сообщения о текущей погоде
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

                # Формирование сообщения о прогнозе на завтра
                tomorrow_data = None
                today = datetime.now().date()
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
                    await message.answer("⚠️ Прогноз на завтра недоступен.")

    except Exception as e:
        logger.error(f"Ошибка при запросе данных: {e}")
        await message.answer("❌ Не удалось получить данные. Проверьте название города.")

@router.message(F.text.lower() == "изменить город")
async def change_city_request(message: types.Message):
    """
    Запрашивает название нового города.
    """
    await message.answer("Введите название нового города:", reply_markup=types.ReplyKeyboardRemove())

@router.message()
async def save_city_handler(message: types.Message):
    """
    Сохраняет введённый пользователем город в JSON файл.
    """
    user_id = message.from_user.id
    city = message.text.strip()

    if not city:
        await message.answer("❌ Пожалуйста, введите название города.")
        return

    try:
        save_city(user_id=user_id, city=city)
        await message.answer(f"✅ Ваш город был успешно изменён на {hbold(city)}.",
                             reply_markup=types.ReplyKeyboardMarkup(weather_kb, resize_keyboard=True))
    except Exception as e:
        logger.error(f"Ошибка при изменении города: {e}")
        await message.answer("❌ Не удалось сохранить новый город. Попробуйте позже.")

@router.message(F.text.lower() == "напоминать утром")
async def enable_reminder(message: types.Message):
    """
    Включает утренние напоминания.
    """
    user_id = message.from_user.id
    reminders = load_reminders()
    reminders[str(user_id)] = True
    save_reminder(reminders)
    await message.answer("✅ Утренние напоминания включены!")

@router.message(F.text.lower() == "отключить напоминание")
async def disable_reminder(message: types.Message):
    """
    Отключает напоминания.
    """
    user_id = message.from_user.id
    reminders = load_reminders()
    if str(user_id) in reminders:
        del reminders[str(user_id)]
        save_reminder(reminders)
        await message.answer("❌ Напоминания отключены.")
    else:
        await message.answer("⚠️ У вас уже отключены напоминания.")

@router.message(F.text.lower() == "назад в меню")
async def back_to_main_menu(message: types.Message):
    """
    Возвращает пользователя в главное меню.
    """
    from main_menu import main_menu_kb
    await message.answer("📋 Главное меню:", reply_markup=types.ReplyKeyboardMarkup(main_menu_kb, resize_keyboard=True))
