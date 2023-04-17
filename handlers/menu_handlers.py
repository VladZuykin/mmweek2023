import asyncio
import datetime
from random import choice
from typing import Union
from io import BytesIO

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, ReplyKeyboardRemove, Message, CallbackQuery
from aiogram.utils import deep_linking
from magic_filter import F
import qrcode

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


async def generate_qr_code(message: types.Message, state: FSMContext):
    payload = message.chat.id
    # payload = deep_linking.encode_payload(f'{message.chat.id}')
    link = f'https://t.me/{config.admin_bot_username}?start={payload}'
    image = qrcode.make(link)
    with BytesIO() as buffer:
        image.save(buffer)
        with BytesIO(buffer.getvalue()) as photo:
            await message.answer_photo(photo)


async def generate_code(message: types.Message, state: FSMContext):
    code = db.create_get_enter_code(message.from_user.id)
    await message.answer(menu_texts.GENERATE_CODE_TEMPLATE.format(code),
                         parse_mode=ParseMode.HTML)

async def show_profile(message: types.Message, state: FSMContext):
    info = db.get_user_info(message.from_user.id, "fullname, money, tuc")
    if not info:
        await message.answer(menu_texts.PROFILE_ERROR)
        return
    fullname, money, tuc = info
    await message.answer(menu_texts.PROFILE_TEMPLATE.format(fullname, money, menu_texts.TUC_TEXTS[tuc]))

async def show_help(message: types.Message, state: FSMContext):
    await message.answer(db.get_help_text())


async def show_schedule(message: types.Message, state: FSMContext):
    print("hello")

def register_menu_handlers():
    dp.register_message_handler(send_menu_on_update,
                                F.from_user.func(lambda user: db.user_registered(user.id)),
                                state="*",
                                commands=['start'])
    dp.register_message_handler(generate_code,
                                text=menu_texts.MENU_GET_CODE_BUTTON_TEXT,
                                state="*",)
    dp.register_message_handler(show_profile,
                                text=menu_texts.MENU_PROFILE_BUTTON_TEXT,
                                state="*", )
    dp.register_message_handler(show_help,
                                text=menu_texts.MENU_HELP_BUTTON_TEXT,
                                state="*", )

