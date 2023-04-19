from aiogram.dispatcher.filters.state import StatesGroup, State


class GreetingState(StatesGroup):
    block = State()
    fullname = State()
    found_similar = State()
    if_in_tuc = State()
    not_found = State()
    register = State()
    tuc_check_query = State()

