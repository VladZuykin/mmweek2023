from typing import Union

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ParseMode

from org_bot_create import dp, db
from handlers import org_scaner_handlers, org_promo_handlers
from markups import org_menu_markups
from middleware import admins
from texts import org_menu_texts, org_promo_texts
from functions import org_menu_functions


@admins.check(level=1)
async def send_menu_on_update(update: Union[Message, CallbackQuery], state: Union[FSMContext, None]):
    if isinstance(update, CallbackQuery):
        message = update.message
    else:
        message = update
    await message.answer(org_menu_texts.ORG_MENU_TEXT, reply_markup=org_menu_markups.org_menu_markup)


@admins.check(level=3)
async def show_promo_list(message: Message, state: FSMContext):
    promo_list = db.get_promo_list()
    counter = 1
    promo_list_text = ""
    for promo in promo_list:
        name, money, can_use, used, time_ends = promo
        promo_list_text += str(counter) + ". " \
                           + org_promo_texts.PROMO_TO_LIST_TEMPLATE.format(name, money) \
                           + org_menu_functions.get_promo_to_list_text(can_use, time_ends, used) + "\n\n"
        counter += 1
    await message.answer(promo_list_text, parse_mode=ParseMode.HTML)


def register_org_menu_handlers():
    dp.register_message_handler(send_menu_on_update,
                                state="*",
                                commands=['start'])
    dp.register_message_handler(show_promo_list,
                                text=org_menu_texts.MENU_LIST_PROMO_BUTTON_TEXT)
    org_scaner_handlers.register_org_scaner_handlers()
    org_promo_handlers.register_org_promo_handlers()
