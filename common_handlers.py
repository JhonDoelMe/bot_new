# bot_new/common_handlers.py
import logging
from aiogram import Router, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

# Импортируем ТОЛЬКО клавиатуры и тексты кнопок из keyboards
from keyboards import (
    main_menu_kb, weather_kb, currency_kb, cancel_kb,
    kb_back_text, kb_cancel_text, kb_weather_text, kb_currency_text,
    kb_my_city_text, kb_change_city_text, kb_alert_text
)


router = Router()
logger = logging.getLogger(__name__)

# Собираем тексты кнопок из переменных
main_menu_button_texts = [
    kb_weather_text, kb_currency_text, kb_my_city_text,
    kb_change_city_text, kb_alert_text
]


@router.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext):
    # ... (логика без изменений) ...
    current_state = await state.get_state()
    if current_state is not None:
        logger.info(f"Сброс состояния {current_state} для пользователя {message.from_user.id} при команде /start")
        await state.clear()
    logger.info(f"Пользователь {message.from_user.id} запустил бота (/start)")
    await message.answer(
        f"👋 Привет, {message.from_user.full_name}! Я ваш многофункциональный помощник.\n"
        "Выберите действие:",
        reply_markup=main_menu_kb
    )


# Фильтр для "Назад в меню"
@router.message(StateFilter(None), F.text == kb_back_text)
async def handle_back_to_main_menu_no_state(message: types.Message):
    # ... (логика без изменений) ...
    logger.debug(f"Пользователь {message.from_user.id} нажал '{kb_back_text}' (без состояния)")
    await message.answer(
        "📋 Вы в главном меню. Выберите действие:",
        reply_markup=main_menu_kb
    )


# Фильтр для "Назад в меню" и "Отмена" (включая состояния)
@router.message(F.text.in_({kb_back_text, kb_cancel_text}))
async def handle_back_to_main_menu_with_state(message: types.Message, state: FSMContext):
     # ... (логика без изменений) ...
    current_state = await state.get_state()
    if current_state is not None:
        logger.info(f"Отмена состояния {current_state} для пользователя {message.from_user.id} кнопкой '{message.text}'")
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=main_menu_kb # Возвращаем главное меню
        )
    else:
        logger.debug(f"Пользователь {message.from_user.id} нажал '{message.text}', но состояния не было.")
        await message.answer(
            "📋 Вы в главном меню. Выберите действие:",
            reply_markup=main_menu_kb
        )


# Обработчик для неизвестных сообщений
@router.message(StateFilter(None))
async def handle_unknown_message(message: types.Message):
    # ... (логика без изменений, но проверка теперь по новым текстам) ...
    logger.debug(f"Получено сообщение в StateFilter(None): '{message.text}' от {message.from_user.id}")
    if message.text and message.text in main_menu_button_texts:
        logger.warning(
            f"Обработчик для кнопки главного меню '{message.text}' не сработал! "
            f"Сообщение перехвачено handle_unknown_message."
        )
        # await message.answer("Произошла внутренняя ошибка. Попробуйте нажать кнопку еще раз или перезапустите бота командой /start")
    elif message.text:
        logger.info(f"Получено неизвестное сообщение '{message.text}' от {message.from_user.id}")
        await message.answer(
            "🤔 Не понимаю вас. Пожалуйста, используйте кнопки меню или известные команды.",
            reply_markup=main_menu_kb
        )