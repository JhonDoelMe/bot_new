# bot_new/states.py
from aiogram.fsm.state import State, StatesGroup

class CityUpdate(StatesGroup):
    waiting_for_city_name = State()

# Можно добавить другие группы состояний здесь, если понадобится
# class ReminderSetup(StatesGroup):
#     waiting_for_text = State()
#     waiting_for_time = State()