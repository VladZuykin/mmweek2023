from aiogram.dispatcher.filters.state import StatesGroup, State


class ScanerState(StatesGroup):
    scan = State()
    give_money = State()


class PromoState(StatesGroup):
    choose_promo = State()
    num_points = State()
    num_uses = State()
    period = State()
