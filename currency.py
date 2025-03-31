# bot_new/currency.py
from aiogram import Router, types, F
from aiogram.filters import StateFilter
import aiohttp
import logging
from datetime import datetime

from keyboards import currency_kb, main_menu_kb # Импортируем клавиатуры

router = Router()
logger = logging.getLogger(__name__)

# ... (FILTER_CURRENCIES остается без изменений)
FILTER_CURRENCIES = ["USD", "EUR", "GBP", "PLN"]


@router.message(StateFilter(None), F.text == "Курс валют 💰") # Точное совпадение
async def handle_currency_request(message: types.Message):
    """
    Обработчик кнопки "Курс валют".
    Перенаправляет пользователя в модуль курса валют и запрашивает данные.
    """
    logger.info(f"Пользователь {message.from_user.id} запросил курс валют")
    # Сразу показываем сообщение об ожидании и убираем клавиатуру
    processing_message = await message.answer("⏳ Получаю актуальные курсы валют от НБУ...", reply_markup=types.ReplyKeyboardRemove())
    await get_currency_rates(processing_message) # Передаем сообщение для редактирования


async def get_currency_rates(processing_message: types.Message): # Принимает сообщение для редактирования
    """
    Получает курсы валют на текущую дату из API НБУ и отправляет пользователю.
    Выводятся только выбранные валюты.
    Редактирует переданное сообщение processing_message.
    """
    try:
        today = datetime.now().strftime("%Y%m%d")
        url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={today}&json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as response:
                logger.debug(f"Запрос курса валют НБУ. Статус: {response.status}")
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API НБУ вернул ошибку {response.status}: {error_text}")
                    await processing_message.edit_text( # Редактируем сообщение
                        "❌ Ошибка при получении данных от НБУ. Сервер недоступен или вернул ошибку.",
                        reply_markup=main_menu_kb # Возвращаем в главное меню при ошибке
                    )
                    return

                try:
                    data = await response.json()
                except aiohttp.ContentTypeError:
                    logger.error("Ошибка декодирования JSON от API НБУ.")
                    await processing_message.edit_text( # Редактируем сообщение
                        "❌ Ошибка: НБУ вернул данные в неверном формате.",
                        reply_markup=main_menu_kb
                    )
                    return

                if not data:
                    logger.warning("Ответ API НБУ пустой.")
                    await processing_message.edit_text( # Редактируем сообщение
                        "⚠️ Не удалось получить информацию о курсах валют от НБУ (пустой ответ).",
                        reply_markup=currency_kb # Показываем клавиатуру валют
                    )
                    return

                filtered_data = [item for item in data if item["cc"] in FILTER_CURRENCIES]
                if not filtered_data:
                    await processing_message.edit_text( # Редактируем сообщение
                        "⚠️ Не удалось найти курсы для выбранных валют в ответе НБУ.",
                        reply_markup=currency_kb
                    )
                    return

                rates_list = []
                # Получаем дату из первого элемента ответа (она должна быть одинаковой)
                date_str = filtered_data[0].get('exchangedate', datetime.now().strftime('%d.%m.%Y'))

                for item in sorted(filtered_data, key=lambda x: x['cc']):
                     # Используем поле exchangedate для даты курса
                    rates_list.append(
                        f"<b>{item['cc']}</b> ({item['txt']}): {item['rate']:.4f} грн"
                    )
                rates = "\n".join(rates_list)

                # Редактируем сообщение
                await processing_message.edit_text(
                    f"🇺🇦 Курс валют НБУ на <b>{date_str}</b>:\n\n{rates}",
                    reply_markup=currency_kb,
                    parse_mode="HTML"
                )

    except aiohttp.ClientConnectorError as e:
         logger.error(f"Ошибка соединения при запросе курсов валют НБУ: {e}")
         await processing_message.edit_text( # Редактируем сообщение
             "❌ Не удалось связаться с сервером НБУ. Проверьте интернет или попробуйте позже.",
             reply_markup=main_menu_kb
         )
    except TimeoutError:
        logger.error("Таймаут при запросе курсов валют НБУ.")
        await processing_message.edit_text( # Редактируем сообщение
            "❌ Сервер НБУ не отвечает. Попробуйте позже.",
            reply_markup=main_menu_kb
        )
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при запросе курсов валют: {e}")
        await processing_message.edit_text( # Редактируем сообщение
            "❌ Произошла непредвиденная ошибка при получении курсов валют.",
            reply_markup=main_menu_kb
        )