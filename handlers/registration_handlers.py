import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ChatActions, ParseMode, ReplyKeyboardRemove

import constants
from fsm.registration_fsm import GreetingState
from markups import registration_markups
from bot_create import bot, dp
from main import db
from texts import registration_texts


async def greetings(message: types.Message, state: FSMContext):
    await GreetingState.block.set()

    await message.answer(registration_texts.GREETING_FIRST_MESSAGE_TEXT, reply_markup=ReplyKeyboardRemove())
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1.7)
    await message.answer(registration_texts.GREETING_SECOND_MESSAGE_TEXT, parse_mode=ParseMode.HTML)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(4.5)
    await message.answer(registration_texts.GREETING_THIRD_MESSAGE_TEXT)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(5)
    await message.answer(registration_texts.GREETING_FOURTH_MESSAGE_TEXT)
    await GreetingState.fullname.set()


async def get_fullname(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    db.add_user(message.from_user.id, message.from_user.username, message.text)
    await message.answer(registration_texts.NICE_TO_MEET_TEMPLATE.format(message.text
                                                                         )[:constants.MAX_MESSAGE_LEN],
                         reply_markup=ReplyKeyboardRemove()
                         )
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)

    if True:  # TODO Добавить проверку на участие в Профкоме
        await message.answer(registration_texts.NOT_IN_TUC_TEXT,
                             reply_markup=registration_markups.NOT_IN_TUC_MARKUP)
    await state.finish()


def register_registration_handlers():
    dp.register_message_handler(greetings, commands=['start'], state=None)
    dp.register_message_handler(get_fullname, lambda msg: not msg.text.startswith("/"),
                                state=GreetingState.fullname)
