# bot_new/city_management.py
import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
import aiohttp

from utils import save_city, get_user_city
from states import CityUpdate
# Импортируем ТОЛЬКО клавиатуры и тексты кнопок из keyboards
from keyboards import (
    main_menu_kb, cancel_kb,
    kb_my_city_text, kb_change_city_text, kb_cancel_text # Добавляем kb_cancel_text
)
from config import WEATHER_API_KEY

router = Router()
logger = logging.getLogger(__name__)


# Фильтр для "Мой город"
@router.message(StateFilter(None), F.text == kb_my_city_text)
async def handle_my_city(message: types.Message):
    # ... (логика без изменений) ...
    logger.info(f"Пользователь {message.from_user.id} запросил '{kb_my_city_text}'")
    user_id = message.from_user.id
    city = get_user_city(user_id)
    if city:
        await message.answer(f"📌 Ваш сохраненный город: <b>{city}</b>", parse_mode="HTML")
    else:
        await message.answer(
            f"🏙️ Вы еще не сохранили свой город. Нажмите '{kb_change_city_text}', чтобы установить его.",
            reply_markup=main_menu_kb
        )


# Фильтр для "Изменить город"
@router.message(StateFilter(None), F.text == kb_change_city_text)
async def handle_change_city_request(message: types.Message, state: FSMContext):
    # ... (логика без изменений) ...
    logger.info(f"Пользователь {message.from_user.id} инициировал '{kb_change_city_text}'")
    await message.answer(
        f"Введите название города, для которого хотите получать погоду. Например: <b>Киев</b> или <b>London</b>\n"
        f"Для отмены нажмите '{kb_cancel_text}'",
        reply_markup=cancel_kb,
        parse_mode="HTML"
    )
    await state.set_state(CityUpdate.waiting_for_city_name)


@router.message(CityUpdate.waiting_for_city_name, F.text)
async def handle_city_name_input(message: types.Message, state: FSMContext):
     # Проверяем, не нажал ли пользователь "Отмена"
    if message.text == kb_cancel_text: # Используем переменную
         # Этот случай должен обрабатываться общим хендлером handle_back_to_main_menu_with_state
         logger.info(f"Пользователь {message.from_user.id} отменил ввод города.")
         # await state.clear() # Не нужно здесь, делается в общем хендлере
         # await message.answer("Отменено.", reply_markup=main_menu_kb)
         return # Просто выходим, общий обработчик сделает остальное

    logger.info(f"Пользователь {message.from_user.id} ввел город: '{message.text}'")

    if not message.text or len(message.text.strip()) < 2:
         await message.answer(f"Название города слишком короткое. Попробуйте еще раз или нажмите '{kb_cancel_text}'.", reply_markup=cancel_kb)
         return

    # ... (остальная логика проверки и сохранения города без изменений) ...
    city_name_input = message.text.strip()
    user_id = message.from_user.id

    if not WEATHER_API_KEY:
        # ... (без изменений)
        logger.warning(f"Нет WEATHER_API_KEY. Сохраняю город '{city_name_input}' для пользователя {user_id} без проверки.")
        save_city(user_id, city_name_input)
        await message.answer(
            f"✅ Город <b>{city_name_input}</b> сохранен!\n"
            f"<i>(Проверка не выполнялась, т.к. ключ API погоды не настроен)</i>",
            reply_markup=main_menu_kb,
            parse_mode="HTML"
        )
        await state.clear()
        return

    checking_message = await message.answer("⏳ Проверяю город...", reply_markup=types.ReplyKeyboardRemove())

    # Проверка города через OpenWeatherMap API
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name_input,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    is_valid_city = False
    actual_city_name = city_name_input
    try:
        # ... (блок try/except для API без изменений)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                logger.debug(f"Проверка города '{city_name_input}'. Статус: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    actual_city_name = data.get('name', city_name_input) # Используем имя из API
                    is_valid_city = True
                elif response.status == 404:
                    logger.info(f"Город '{city_name_input}' не найден через API погоды (404).")
                else:
                    logger.error(f"Ошибка API погоды ({response.status}) при проверке города '{city_name_input}'. Ответ: {await response.text()}")

    except aiohttp.ClientConnectorError as e:
        logger.error(f"Ошибка соединения при проверке города '{city_name_input}': {e}")
        await checking_message.edit_text("❌ Не удалось проверить город из-за ошибки сети. Попробуйте позже.", reply_markup=main_menu_kb) # Редактируем сообщение о проверке
        await state.clear()
        return
    except TimeoutError:
        logger.error(f"Таймаут при проверке города '{city_name_input}'.")
        await checking_message.edit_text("❌ Сервер проверки города не отвечает. Попробуйте позже.", reply_markup=main_menu_kb)
        await state.clear()
        return
    except Exception as e:
        logger.error(f"Неизвестная ошибка при проверке города '{city_name_input}': {e}", exc_info=True)
        await checking_message.edit_text("❌ Произошла неизвестная ошибка при проверке города.", reply_markup=main_menu_kb)
        await state.clear()
        return

    if is_valid_city:
        # ... (сохранение без изменений)
        save_city(user_id, actual_city_name) # Сохраняем имя из API
        await checking_message.edit_text( # Редактируем сообщение о проверке
            f"✅ Город <b>{actual_city_name}</b> успешно проверен и сохранен!",
            reply_markup=main_menu_kb,
            parse_mode="HTML"
        )
        await state.clear()
    else:
        # ... (ответ об ошибке без изменений)
        await checking_message.edit_text( # Редактируем сообщение о проверке
            f"❌ Город '<b>{city_name_input}</b>' не найден или не поддерживается.\n"
            "Пожалуйста, проверьте название и попробуйте еще раз.",
            reply_markup=cancel_kb, # Оставляем кнопку Отмена
            parse_mode="HTML"
        )


# Обработчик на случай, если пользователь прислал не текст в состоянии ожидания города
@router.message(CityUpdate.waiting_for_city_name)
async def handle_wrong_input_in_city_state(message: types.Message):
    # ... (логика без изменений) ...
    logger.debug(f"Пользователь {message.from_user.id} прислал не текст в состоянии ожидания города: {message.content_type}")
    await message.answer(
        f"Пожалуйста, введите название города текстом или нажмите '{kb_cancel_text}'.",
        reply_markup=cancel_kb
    )