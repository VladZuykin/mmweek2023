from aiogram.dispatcher.filters.state import StatesGroup, State


class GreetingState(StatesGroup):
    block = State()
    fullname = State()
