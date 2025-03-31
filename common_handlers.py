# bot_new/common_handlers.py
import logging
from aiogram import Router, types, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

# Импортируем тексты кнопок напрямую для проверки
from keyboards import main_menu_kb, weather_kb, currency_kb, cancel_kb

router = Router()
logger = logging.getLogger(__name__)

# Получаем тексты кнопок главного меню
# Это более надежно, чем хардкодить список в обработчике
main_menu_button_texts = []
for row in main_menu_kb.keyboard:
    for button in row:
        main_menu_button_texts.append(button.text)


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

    logger.info(f"Пользователь {message.from_user.id} запустил бота (/start)")
    await message.answer(
        f"👋 Привет, {message.from_user.full_name}! Я ваш многофункциональный помощник.\n"
        "Выберите действие:",
        reply_markup=main_menu_kb
    )


@router.message(StateFilter(None), F.text == "Назад в меню ↩️") # Точное совпадение
async def handle_back_to_main_menu_no_state(message: types.Message):
    """
    Обработчик кнопки "Назад в меню", когда пользователь не в каком-либо состоянии.
    Возвращает пользователя в главное меню.
    """
    logger.debug(f"Пользователь {message.from_user.id} нажал 'Назад в меню' (без состояния)")
    await message.answer(
        "📋 Вы в главном меню. Выберите действие:",
        reply_markup=main_menu_kb
    )

# Обрабатываем и кнопку отмены здесь же
@router.message(F.text.in_({"Назад в меню ↩️", "Отмена ❌"})) # Точное совпадение
async def handle_back_to_main_menu_with_state(message: types.Message, state: FSMContext):
    """
    Обработчик кнопок "Назад в меню" или "Отмена", когда пользователь находится в каком-либо состоянии.
    Сбрасывает состояние и возвращает в главное меню.
    """
    current_state = await state.get_state()
    if current_state is not None:
        logger.info(f"Отмена состояния {current_state} для пользователя {message.from_user.id} кнопкой '{message.text}'")
        await state.clear()
        await message.answer(
            "Действие отменено.",
            reply_markup=main_menu_kb # Возвращаем главное меню
        )
    else:
        # Если состояния нет, просто возвращаем в главное меню (на случай если этот хендлер вызван без состояния)
        logger.debug(f"Пользователь {message.from_user.id} нажал '{message.text}', но состояния не было.")
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
    logger.debug(f"Получено сообщение в StateFilter(None): '{message.text}' от {message.from_user.id}")
    # Проверяем, является ли сообщение текстом кнопки из главного меню
    if message.text and message.text in main_menu_button_texts:
        # Если это текст кнопки, но обработчик для неё не сработал - это ошибка в роутинге или фильтрах
        logger.warning(
            f"Обработчик для кнопки главного меню '{message.text}' не сработал! "
            f"Сообщение перехвачено handle_unknown_message."
        )
        # Можно раскомментировать следующую строку, чтобы сообщить пользователю об ошибке
        # await message.answer("Произошла внутренняя ошибка. Попробуйте нажать кнопку еще раз или перезапустите бота командой /start")
    elif message.text: # Если это просто неизвестный текст
        logger.info(f"Получено неизвестное сообщение '{message.text}' от {message.from_user.id}")
        await message.answer(
            "🤔 Не понимаю вас. Пожалуйста, используйте кнопки меню или известные команды.",
            reply_markup=main_menu_kb
        )
    # Если пришло не текстовое сообщение (фото, стикер и т.п.), можно добавить обработку или просто проигнорировать
    # else:
    #     logger.debug(f"Получено не текстовое сообщение от {message.from_user.id}")