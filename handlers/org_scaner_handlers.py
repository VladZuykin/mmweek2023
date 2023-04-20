from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from callbacks import org_menu_callbacks
from markups import org_menu_markups
from texts import org_scaner_texts, org_menu_texts
from org_bot_create import dp, db
from middleware import admins
from fsm.org_menu_fsm import ScanerState


@admins.check(level=1)
async def input_code(message: Message, state: FSMContext):
    event_id = db.get_event_id(message.from_user.id)
    event_name = db.get_event_name(event_id)
    if not event_name:
        await message.answer(org_scaner_texts.NO_EVENT_ERROR_TEXT)
        return
    await message.answer(org_scaner_texts.SCAN_CODE_TEMPLATE.format(event_name),
                         reply_markup=org_menu_markups.back_to_menu_markup)
    await ScanerState.scan.set()


@admins.check(level=1)
async def scan_code(message: Message, state: FSMContext):
    """ проверка введенного кода """
    enter_code = message.text
    if enter_code.casefold() == org_menu_texts.BACK_TO_MENU_BUTTON_TEXT.casefold():
        await message.answer(org_menu_texts.BACK_TO_MENU_TEXT,
                             reply_markup=org_menu_markups.org_menu_markup)
        await state.finish()
        return

    participant_id = db.get_id_with_code(enter_code)
    if not participant_id:
        await message.answer(org_scaner_texts.NO_PARTICIPANT_TEXT)
        await message.answer(org_scaner_texts.SCAN_CODE_TEXT)
        return

    event_id = db.get_event_id(message.from_user.id)
    participant_name = db.get_fullname(participant_id)
    part_visits = db.get_events_visited(participant_id)  # part_visits - все мероприятия, посещенные этим участником
    if part_visits and (event_id in part_visits):
        await message.answer(org_scaner_texts.MONEY_GIVEN_ALREADY_TEMPLATE.format(participant_name))
        await message.answer(org_scaner_texts.SCAN_CODE_TEXT)
        return

    money_value = db.get_event_reward(event_id)

    await message.answer(org_scaner_texts.GIVE_MONEY_TEMPLATE.format(participant_name, money_value),
                         reply_markup=org_menu_markups.yes_no_markup)
    await state.update_data({"participant_id": participant_id,
                             "participant_name": participant_name,
                             "event_id": event_id,
                             "money_value": money_value})
    await ScanerState.give_money.set()


@admins.check(level=1)
async def give_money(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tg_id = data["participant_id"]
    name = data["participant_name"]
    event_id = data["event_id"]
    money_value = data["money_value"]
    db.update_event_visits(tg_id, event_id)
    db.add_money(tg_id, money_value)
    await callback_query.message.edit_text(org_scaner_texts.MONEY_GIVEN_TEMPLATE.format(money_value, name),
                                           reply_markup=None)
    await callback_query.message.answer(org_scaner_texts.SCAN_CODE_TEXT,
                                        reply_markup=org_menu_markups.back_to_menu_markup)
    await ScanerState.scan.set()


@admins.check(level=1)
async def give_not_money(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data["participant_name"]
    await callback_query.message.edit_text(org_scaner_texts.NOT_MONEY_GIVEN_TEMPLATE.format(name),
                                           reply_markup=None)
    await callback_query.message.answer(org_scaner_texts.SCAN_CODE_TEXT,
                                        reply_markup=org_menu_markups.back_to_menu_markup)
    await ScanerState.scan.set()


@admins.check(level=1)
async def coerce_back_to_menu(message: Message, state: FSMContext):
    await message.answer(org_scaner_texts.COERCE_BACK_TO_MENU_TEXT, reply_markup=ReplyKeyboardRemove())


def register_org_scaner_handlers():
    dp.register_message_handler(input_code,
                                text=org_menu_texts.MENU_SCANER_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(scan_code,
                                state=ScanerState.scan)
    dp.register_callback_query_handler(give_money,
                                       org_menu_callbacks.GIVE_MONEY_CB.filter(decision='1'),
                                       state=ScanerState.give_money)
    dp.register_callback_query_handler(give_not_money,
                                       org_menu_callbacks.GIVE_MONEY_CB.filter(decision='0'),
                                       state=ScanerState.give_money)
    dp.register_message_handler(coerce_back_to_menu,
                                state=ScanerState.give_money)
