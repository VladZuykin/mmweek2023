from aiogram.dispatcher.filters.state import StatesGroup, State


class ScanerState(StatesGroup):
    scan = State()
    give_money = State()
