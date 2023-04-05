import asyncio
import datetime
from random import choice
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, ReplyKeyboardRemove, Message, CallbackQuery
from magic_filter import F

import constants
from markups import menu_markups
from bot_create import bot, dp, config
from main import db
from texts import menu_texts

async def send_menu_on_update(update: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(update, CallbackQuery):
        message = update.message
    else:
        message = update

    await message.answer(menu_texts.MENU_TEXT,
                         reply_markup=menu_markups.menu_markup)

def register_menu_handlers():
    dp.register_message_handler(send_menu_on_update,
                                F.from_user.func(lambda user: db.user_registered(user.id)),
                                state="*",
                                commands=['start'])
