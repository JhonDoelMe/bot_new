# bot_new/city_management.py
import logging
from aiogram import Router, types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
import aiohttp

from utils import save_city, get_user_city
from states import CityUpdate
from keyboards import main_menu_kb, cancel_kb
from config import WEATHER_API_KEY # Нужен для проверки города

router = Router()
logger = logging.getLogger(__name__)


@router.message(StateFilter(None), F.text.lower() == "мой город 🏙️")
async def handle_my_city(message: types.Message):
    """
    Обработчик кнопки "Мой город".
    Показывает сохраненный город пользователя.
    """
    user_id = message.from_user.id
    city = get_user_city(user_id)

    if city:
        await message.answer(f"📌 Ваш сохраненный город: <b>{city}</b>", parse_mode="HTML")
    else:
        await message.answer(
            "🏙️ Вы еще не сохранили свой город. "
            "Нажмите 'Изменить город', чтобы установить его.",
            reply_markup=main_menu_kb
        )


@router.message(StateFilter(None), F.text.lower() == "изменить город ✏️")
async def handle_change_city_request(message: types.Message, state: FSMContext):
    """
    Обработчик кнопки "Изменить город".
    Переводит пользователя в состояние ожидания ввода города.
    """
    await message.answer(
        "Введите название города, для которого хотите получать погоду. "
        "Например: <b>Киев</b> или <b>London</b>",
        reply_markup=cancel_kb, # Показываем кнопку Отмена
        parse_mode="HTML"
    )
    await state.set_state(CityUpdate.waiting_for_city_name)


# Обработчик для случая, если пользователь нажал кнопку вместо ввода города
@router.message(CityUpdate.waiting_for_city_name, F.text)
async def handle_city_name_input(message: types.Message, state: FSMContext):
    """
    Обрабатывает введенное пользователем название города,
    проверяет его через API погоды и сохраняет.
    """
    if not message.text or len(message.text) < 2:
         await message.answer("Название города слишком короткое. Попробуйте еще раз.", reply_markup=cancel_kb)
         return

    # Убираем кнопку "Отмена" перед проверкой
    await message.answer("⏳ Проверяю город...", reply_markup=types.ReplyKeyboardRemove())

    city_name = message.text.strip()
    user_id = message.from_user.id

    if not WEATHER_API_KEY:
        logger.warning(f"Нет WEATHER_API_KEY. Сохраняю город '{city_name}' для пользователя {user_id} без проверки.")
        save_city(user_id, city_name)
        await message.answer(
            f"✅ Город <b>{city_name}</b> сохранен!\n"
            f"<i>(Проверка не выполнялась, т.к. ключ API погоды не настроен)</i>",
            reply_markup=main_menu_kb,
            parse_mode="HTML"
        )
        await state.clear()
        return

    # Проверка города через OpenWeatherMap API
    url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city_name,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'ru'
    }
    is_valid_city = False
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    is_valid_city = True
                    # Можно даже получить нормализованное имя города из ответа
                    # data = await response.json()
                    # city_name = data.get('name', city_name) # Обновляем имя на то, что вернул API
                elif response.status == 404:
                    logger.info(f"Город '{city_name}' не найден через API погоды.")
                else:
                    logger.error(f"Ошибка API погоды ({response.status}) при проверке города '{city_name}'.")

    except aiohttp.ClientConnectorError as e:
        logger.error(f"Ошибка соединения при проверке города '{city_name}': {e}")
        await message.answer("❌ Не удалось проверить город из-за ошибки сети. Попробуйте позже.", reply_markup=main_menu_kb)
        await state.clear()
        return
    except Exception as e:
        logger.error(f"Неизвестная ошибка при проверке города '{city_name}': {e}")
        await message.answer("❌ Произошла неизвестная ошибка при проверке города.", reply_markup=main_menu_kb)
        await state.clear()
        return

    if is_valid_city:
        save_city(user_id, city_name)
        await message.answer(
            f"✅ Город <b>{city_name}</b> успешно проверен и сохранен!",
            reply_markup=main_menu_kb,
            parse_mode="HTML"
        )
        await state.clear()
    else:
        await message.answer(
            f"❌ Город <b>{city_name}</b> не найден или не поддерживается. "
            "Пожалуйста, проверьте название и попробуйте еще раз.",
            reply_markup=cancel_kb, # Оставляем кнопку Отмена
            parse_mode="HTML"
        )
        # Не сбрасываем состояние, чтобы пользователь мог попробовать еще раз
        # await state.set_state(CityUpdate.waiting_for_city_name) # Состояние уже установлено

# Обработчик на случай, если пользователь прислал не текст в состоянии ожидания города
@router.message(CityUpdate.waiting_for_city_name)
async def handle_wrong_input_in_city_state(message: types.Message):
    await message.answer(
        "Пожалуйста, введите название города текстом или нажмите 'Отмена ❌'.",
        reply_markup=cancel_kb
    )