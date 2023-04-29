from aiogram.dispatcher.filters.state import StatesGroup, State


class MerchIssuanceState(StatesGroup):
    code_input = State()
    cancellation_merch_choice = State()
    cancellation_merch_number_choice = State()
    cancellation_merch_number_confirmation = State()
    issuance_merch_choice = State()
    issuance_merch_number_choice = State()
    issuance_merch_number_confirmation = State()
    cancellation_bad = State()
    issuance_bad = State()

