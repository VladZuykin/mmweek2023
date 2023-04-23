from aiogram.dispatcher.filters.state import StatesGroup, State

class GiveAccessStates(StatesGroup):
    choose_role = State()
    choose_event = State()
    choose_user = State()
    role_confirmation = State()