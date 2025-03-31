# bot_new/currency.py
import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
import aiohttp
from datetime import datetime

# Импортируем ТОЛЬКО клавиатуры и тексты кнопок из keyboards
from keyboards import (
    currency_kb, main_menu_kb,
    kb_currency_text
)

router = Router()
logger = logging.getLogger(__name__)

FILTER_CURRENCIES = ["USD", "EUR", "GBP", "PLN"]


# Фильтр для "Курс валют"
@router.message(StateFilter(None), F.text == kb_currency_text)
async def handle_currency_request(message: types.Message):
    # ... (логика без изменений) ...
    logger.info(f"Пользователь {message.from_user.id} запросил '{kb_currency_text}'")
    processing_message = await message.answer("⏳ Получаю актуальные курсы валют от НБУ...", reply_markup=types.ReplyKeyboardRemove())
    await get_currency_rates(processing_message)


async def get_currency_rates(processing_message: types.Message):
    # ... (логика получения курса без изменений) ...
    try:
        today = datetime.now().strftime("%Y%m%d")
        url = f"https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?date={today}&json"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=15) as response:
                logger.debug(f"Запрос курса валют НБУ. Статус: {response.status}")
                if response.status != 200:
                    # ... (обработка ошибок без изменений)
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
                     # ... (обработка ошибок без изменений)
                    logger.error("Ошибка декодирования JSON от API НБУ.")
                    await processing_message.edit_text( # Редактируем сообщение
                        "❌ Ошибка: НБУ вернул данные в неверном формате.",
                        reply_markup=main_menu_kb
                    )
                    return

                if not data:
                     # ... (обработка ошибок без изменений)
                    logger.warning("Ответ API НБУ пустой.")
                    await processing_message.edit_text( # Редактируем сообщение
                        "⚠️ Не удалось получить информацию о курсах валют от НБУ (пустой ответ).",
                        reply_markup=currency_kb # Показываем клавиатуру валют
                    )
                    return

                filtered_data = [item for item in data if item["cc"] in FILTER_CURRENCIES]
                if not filtered_data:
                    # ... (обработка ошибок без изменений)
                    await processing_message.edit_text( # Редактируем сообщение
                        "⚠️ Не удалось найти курсы для выбранных валют в ответе НБУ.",
                        reply_markup=currency_kb
                    )
                    return

                rates_list = []
                date_str = filtered_data[0].get('exchangedate', datetime.now().strftime('%d.%m.%Y'))
                for item in sorted(filtered_data, key=lambda x: x['cc']):
                    rates_list.append(
                        f"<b>{item['cc']}</b> ({item['txt']}): {item['rate']:.4f} грн"
                    )
                rates = "\n".join(rates_list)

                # Редактируем сообщение (оставляем эмодзи флага)
                await processing_message.edit_text(
                    f"🇺🇦 Курс валют НБУ на <b>{date_str}</b>:\n\n{rates}",
                    reply_markup=currency_kb,
                    parse_mode="HTML"
                )

    except aiohttp.ClientConnectorError as e:
         # ... (обработка ошибок без изменений)
         logger.error(f"Ошибка соединения при запросе курсов валют НБУ: {e}")
         await processing_message.edit_text( # Редактируем сообщение
             "❌ Не удалось связаться с сервером НБУ. Проверьте интернет или попробуйте позже.",
             reply_markup=main_menu_kb
         )
    except TimeoutError:
        # ... (обработка ошибок без изменений)
        logger.error("Таймаут при запросе курсов валют НБУ.")
        await processing_message.edit_text( # Редактируем сообщение
            "❌ Сервер НБУ не отвечает. Попробуйте позже.",
            reply_markup=main_menu_kb
        )
    except Exception as e:
        # ... (обработка ошибок без изменений)
        logger.exception(f"Неизвестная ошибка при запросе курсов валют: {e}")
        await processing_message.edit_text( # Редактируем сообщение
            "❌ Произошла непредвиденная ошибка при получении курсов валют.",
            reply_markup=main_menu_kb
        )