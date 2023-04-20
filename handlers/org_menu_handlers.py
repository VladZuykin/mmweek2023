from typing import Union

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message

from org_bot_create import dp
from handlers import org_scaner_handlers, org_promo_handlers
from markups import org_menu_markups
from middleware import admins
from texts import org_menu_texts


@admins.check(level=1)
async def send_menu_on_update(update: Union[Message, CallbackQuery], state: Union[FSMContext, None]):
    if isinstance(update, CallbackQuery):
        message = update.message
    else:
        message = update
    await message.answer(org_menu_texts.ORG_MENU_TEXT, reply_markup=org_menu_markups.org_menu_markup)


@admins.check(level=3)
async def show_promo_list(message: Message, state: FSMContext):  # TODO
    print("promo_list")


def register_org_menu_handlers():
    dp.register_message_handler(send_menu_on_update,
                                state="*",
                                commands=['start'])
    org_scaner_handlers.register_org_scaner_handlers()
    org_promo_handlers.register_org_promo_handlers()
