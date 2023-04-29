from typing import Union

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ParseMode, ReplyKeyboardMarkup

import constants
from org_bot_create import dp, db
from handlers import org_scaner_handlers, org_promo_handlers, org_give_admin_handlers, org_merch_issuance_handlers
from markups import org_menu_markups
from middleware import admins
from texts import org_menu_texts, org_promo_texts
from functions import org_menu_functions
from fsm.org_menu_fsm import TakeOutAccess


async def send_menu_on_update(update: Union[Message, CallbackQuery], state: Union[FSMContext, None]):
    if isinstance(update, CallbackQuery):
        message = update.message
    else:
        message = update
    await message.answer(org_menu_texts.ORG_MENU_TEXT, reply_markup=org_menu_markups.org_menu_markup)
    await state.finish()


@admins.check(level=3)
async def admins_list(message: Message, state: FSMContext):
    await message.answer(org_menu_functions.get_admin_list_text(db),
                         parse_mode=ParseMode.HTML)


@admins.check(level=3)
async def take_out_access_input(message: Message, state: FSMContext):
    await message.answer(org_menu_texts.TAKE_OUT_ACCESS_USERNAME_INPUT_TEXT,
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                             org_menu_texts.BACK_TO_MENU_BUTTON_TEXT))
    await TakeOutAccess.take_access_input.set()


@admins.check(level=3)
async def process_take_out_request(message: Message, state: FSMContext):
    username = message.text
    tg_id = db.get_user_id_by_username(username)
    if tg_id and db.have_admin_rights(tg_id, 1):
        db.execute("DELETE FROM admins WHERE tg_id = ? and level = 1", tg_id, commit=True)
        db.add_transaction(constants.TransactionTypes.ADMIN_TAKE_OUT.value,
                           message.from_user.id,
                           tg_id, None)
        fullname, = db.get_user_info(tg_id, "fullname")
        text = org_menu_texts.TAKE_OUT_ACCESS_DONE_TEMPLATE.format(fullname,
                                                                   username if username and username[
                                                                       0] != "@" else username[1:])
    else:
        db.add_transaction(constants.TransactionTypes.ADMIN_TAKE_OUT.value,
                           message.from_user.id,
                           None, f"failed try to take access from {username}")
        text = org_menu_texts.TAKE_OUT_ACCESS_NOT_FOUND_TEXT
    await message.answer(text + "\n\n" + org_menu_texts.TAKE_OUT_ACCESS_USERNAME_INPUT_TEXT,
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(
                             org_menu_texts.BACK_TO_MENU_BUTTON_TEXT),
                         parse_mode=ParseMode.HTML)
    await TakeOutAccess.take_access_input.set()


@admins.check(level=3)
async def show_promo_list(message: Message, state: FSMContext):
    promo_list = db.get_promo_list()
    counter = 1
    promo_list_text = ""
    texts = []
    for promo in promo_list:
        name, money, can_use, used, time_ends = promo
        promo_list_text += str(counter) + ". " \
                           + org_promo_texts.PROMO_TO_LIST_TEMPLATE.format(name, money) \
                           + org_menu_functions.get_promo_to_list_text(can_use, time_ends, used) + "\n\n"
        counter += 1
        if counter % 20 == 0:
            texts.append(promo_list_text)
            promo_list_text = ""
    if counter % 20 != 0:
        texts.append(promo_list_text)
    for text in texts:
        await message.answer(text, parse_mode=ParseMode.HTML)


def register_org_menu_handlers():
    org_merch_issuance_handlers.register_merch_issuance_handlers()
    dp.register_message_handler(send_menu_on_update,
                                text=org_menu_texts.BACK_TO_MENU_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(send_menu_on_update,
                                state="*",
                                commands=['start'])
    dp.register_message_handler(show_promo_list,
                                text=org_menu_texts.MENU_LIST_PROMO_BUTTON_TEXT)
    dp.register_message_handler(admins_list,
                                state="*",
                                text=org_menu_texts.MENU_ADMINS_LIST_BUTTON_TEXT)
    dp.register_message_handler(take_out_access_input,
                                text=org_menu_texts.MENU_TAKE_AWAY_ACCESS_BUTTON_TEXT)
    dp.register_message_handler(process_take_out_request,
                                state=TakeOutAccess.take_access_input)
    org_scaner_handlers.register_org_scaner_handlers()
    org_promo_handlers.register_org_promo_handlers()
    org_give_admin_handlers.register_org_promo_handlers()
