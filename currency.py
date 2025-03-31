# bot_new/currency.py
from aiogram import Router, types, F
from aiogram.filters import StateFilter
import aiohttp
import logging
from datetime import datetime

from keyboards import currency_kb # Импортируем клавиатуру

router = Router()
logger = logging.getLogger(__name__)

# Список необходимых валют
FILTER_CURRENCIES = ["USD", "EUR", "GBP", "PLN"] # Убрал RUB, т.к. НБУ не дает его курс к гривне напрямую часто
# Если нужен рубль, то его курс нужно считать кросс-курсом или искать другой источник

@router.message(StateFilter(None), F.text.lower() == "курс валют 💰")
async def handle_currency_request(message: types.Message):
    """
    Обработчик кнопки "Курс валют".
    Перенаправляет пользователя в модуль курса валют и запрашивает данные.
    """
    await message.answer("⏳ Получаю актуальные курсы валют от НБУ...", reply_markup=types.ReplyKeyboardRemove())
    await get_currency_rates(message) # Сразу вызываем функцию получения курса

async def get_currency_rates(message: types.Message):
    """
    Получает курсы валют на текущую дату из API НБУ и отправляет пользователю.
    Выводятся только выбранные валюты.
    """
    try:
        # Форматируем текущую дату для запроса
        today = datetime.now().strftime("%Y%m%d")
        url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={today}&json"

        async with aiohttp.ClientSession() as session:
            # Увеличиваем таймаут и добавляем обработку ClientConnectorError
            async with session.get(url, timeout=15) as response:
                logger.debug(f"Запрос курса валют НБУ. Статус: {response.status}")
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"API НБУ вернул ошибку {response.status}: {error_text}")
                    await message.answer("❌ Ошибка при получении данных от НБУ. Сервер недоступен или вернул ошибку.", reply_markup=currency_kb)
                    return

                # Обрабатываем ответ JSON
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError:
                    logger.error("Ошибка декодирования JSON от API НБУ. Ответ не в формате JSON.")
                    await message.answer("❌ Ошибка: НБУ вернул данные в неверном формате.", reply_markup=currency_kb)
                    return

                if not data:
                    logger.warning("Ответ API НБУ пустой.")
                    await message.answer("⚠️ Не удалось получить информацию о курсах валют от НБУ (пустой ответ).", reply_markup=currency_kb)
                    return

                # Фильтруем данные по нужным валютам
                filtered_data = [item for item in data if item["cc"] in FILTER_CURRENCIES]
                if not filtered_data:
                    await message.answer("⚠️ Не удалось найти курсы для выбранных валют в ответе НБУ.", reply_markup=currency_kb)
                    return

                # Формируем сообщение с курсами валют
                rates_list = []
                for item in sorted(filtered_data, key=lambda x: x['cc']): # Сортируем по коду валюты
                     # Добавим информацию о номинале, если он не 1
                    unit_info = f" за {item['exchangedate']}" if 'exchangedate' in item else ""
                    rates_list.append(
                        f"<b>{item['cc']}</b> ({item['txt']}): {item['rate']:.4f} грн" + unit_info
                    )
                rates = "\n".join(rates_list)

                await message.answer(
                    f"🇺🇦 Курс валют НБУ на <b>{datetime.now().strftime('%d.%m.%Y')}</b>:\n\n{rates}",
                    reply_markup=currency_kb,
                    parse_mode="HTML"
                )

    except aiohttp.ClientConnectorError as e:
         logger.error(f"Ошибка соединения при запросе курсов валют НБУ: {e}")
         await message.answer("❌ Не удалось связаться с сервером НБУ. Проверьте интернет или попробуйте позже.", reply_markup=currency_kb)
    except TimeoutError:
        logger.error("Таймаут при запросе курсов валют НБУ.")
        await message.answer("❌ Сервер НБУ не отвечает. Попробуйте позже.", reply_markup=currency_kb)
    except Exception as e:
        logger.exception(f"Неизвестная ошибка при запросе курсов валют: {e}") # Логируем стектрейс
        await message.answer("❌ Произошла непредвиденная ошибка при получении курсов валют.", reply_markup=currency_kb)