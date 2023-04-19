from aiogram.dispatcher.filters.state import StatesGroup, State


class SupportState(StatesGroup):
    input_wait = State()

class PromoState(StatesGroup):
    input_wait = State()
