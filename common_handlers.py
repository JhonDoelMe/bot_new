# bot_new/common_handlers.py
from aiogram import Router, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from keyboards import main_menu_kb # Импортируем клавиатуру из keyboards.py
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start.
    Приветствует пользователя и показывает основное меню.
    Сбрасывает состояние, если оно было установлено.
    """
    current_state = await state.get_state()
    if current_state is not None:
        logger.info(f"Сброс состояния {current_state} для пользователя {message.from_user.id} при команде /start")
        await state.clear()

    await message.answer(
        f"👋 Привет, {message.from_user.full_name}! Я ваш многофункциональный помощник.\n"
        "Выберите действие:",
        reply_markup=main_menu_kb
    )


@router.message(StateFilter(None), F.text.lower() == "назад в меню ↩️")
async def handle_back_to_main_menu_no_state(message: types.Message):
    """
    Обработчик кнопки "Назад в меню", когда пользователь не в каком-либо состоянии.
    Возвращает пользователя в главное меню.
    """
    await message.answer(
        "📋 Вы в главном меню. Выберите действие:",
        reply_markup=main_menu_kb
    )

@router.message(F.text.lower().in_({"назад в меню ↩️", "отмена ❌"})) # Обрабатываем и кнопку отмены
async def handle_back_to_main_menu_with_state(message: types.Message, state: FSMContext):
    """
    Обработчик кнопок "Назад в меню" или "Отмена", когда пользователь находится в каком-либо состоянии.
    Сбрасывает состояние и возвращает в главное меню.
    """
    current_state = await state.get_state()
    if current_state is not None:
        logger.info(f"Отмена состояния {current_state} для пользователя {message.from_user.id}")
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=main_menu_kb # Возвращаем главное меню
        )
    else:
        # Если состояния нет, просто возвращаем в главное меню
        await message.answer(
            "📋 Вы в главном меню. Выберите действие:",
            reply_markup=main_menu_kb
        )

# Обработчик для неизвестных команд или текста вне состояний
@router.message(StateFilter(None))
async def handle_unknown_message(message: types.Message):
    """
    Отлавливает любые сообщения текстом, которые не соответствуют
    кнопкам главного меню или командам, когда пользователь не в состоянии.
    """
    # Проверяем, не является ли сообщение текстом кнопки из главного меню
    # Это нужно, т.к. мы не задали StateFilter(None) для обработчиков кнопок меню
    # в соответствующих модулях (weather, currency, city_management)
    # и они могут не сработать первыми.
    # Лучше всего добавить StateFilter(None) к тем обработчикам.
    # Но пока оставим так для совместимости.
    known_buttons = ["погода 🌤️", "курс валют 💰", "мой город 🏙️", "изменить город ✏️", "тревога 🚨"]
    if message.text and message.text.lower() not in known_buttons:
        await message.answer(
            "🤔 Не понимаю вас. Пожалуйста, используйте кнопки меню или известные команды.",
            reply_markup=main_menu_kb
        )