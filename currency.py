from aiogram import Router, types, F
import aiohttp
import logging
from datetime import datetime

router = Router()
logger = logging.getLogger(__name__)

# Клавиатура модуля "Курс валют"
currency_kb = [
    [types.KeyboardButton(text="Назад в меню")]
]

@router.message(F.text.lower() == "курс валют")
async def get_currency_rates(message: types.Message):
    """
    Обработчик кнопки "Курс валют".
    Получает курсы валют на текущую дату из API НБУ и отправляет пользователю.
    """
    try:
        today = datetime.now().strftime("%Y%m%d")  # Формат текущей даты для запроса API НБУ
        url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={today}&json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    await message.answer("❌ Ошибка при получении данных от НБУ.")
                    return

                # Получаем и обрабатываем данные JSON
                data = await response.json()
                if not data:
                    await message.answer("⚠️ Не удалось получить информацию о курсах валют.")
                    return

                # Формируем список курсов валют для отображения
                rates = "\n".join([
                    f"{item['txt']} ({item['cc']}): {item['rate']} грн за {item['unit']} единиц"
                    for item in data
                ])

                await message.answer(
                    f"💰 Курсы валют на сегодня:\n\n{rates}",
                    reply_markup=types.ReplyKeyboardMarkup(
                        keyboard=currency_kb,
                        resize_keyboard=True
                    )
                )
    except Exception as e:
        logger.error(f"Ошибка при запросе курсов валют: {e}")
        await message.answer("❌ Не удалось получить данные. Попробуйте позже.")

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
