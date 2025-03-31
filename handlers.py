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
    try:
        # Запросы к API OpenWeather
        async with aiohttp.ClientSession() as session:
            current_weather_url = (
                f"https://api.openweathermap.org/data/2.5/weather?"
                f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            )
            forecast_url = (
                f"https://api.openweathermap.org/data/2.5/forecast?"
                f"q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
            )
            async with session.get(current_weather_url) as response_current, \
                       session.get(forecast_url) as response_forecast:

                current_data = await response_current.json()
                forecast_data = await response_forecast.json()

                if response_current.status != 200 or response_forecast.status != 200:
                    await message.answer("❌ Ошибка при запросе погоды.")
                    return

                # Формируем сообщение о текущей погоде
                temp = current_data["main"]["temp"]
                description = current_data["weather"][0]["description"].capitalize()
                await message.answer(f"🌡️ Температура в {city}: {temp}°C\n☁️ {description}")

                # Прогноз на завтра
                tomorrow_data = None
                today = datetime.now().date()
                for item in forecast_data["list"]:
                    forecast_time = datetime.fromtimestamp(item["dt"])
                    if forecast_time.date() == today + timedelta(days=1) and forecast_time.hour == 12:
                        tomorrow_data = item
                        break

                if tomorrow_data:
                    temp_tomorrow = tomorrow_data["main"]["temp"]
                    description_tomorrow = tomorrow_data["weather"][0]["description"].capitalize()
                    await message.answer(f"🌆 Прогноз на завтра:\n🌡️ {temp_tomorrow}°C\n☁️ {description_tomorrow}")
                else:
                    await message.answer("⚠️ Прогноз на завтра недоступен.")
    except Exception as e:
        logger.error(f"Ошибка при запросе погоды: {e}")
        await message.answer("❌ Не удалось получить данные.")

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
        save_city(user_id, city)
        await message.answer(f"✅ Ваш город был успешно изменён на {city}.",
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
