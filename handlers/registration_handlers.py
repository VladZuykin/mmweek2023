import asyncio
from random import choice

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ChatActions, ParseMode, ReplyKeyboardRemove

import constants
from functions import registration_functions
from fsm.registration_fsm import GreetingState
from markups import registration_markups
from bot_create import bot, dp, config
from main import db
from texts import registration_texts


async def greetings(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)
    await message.answer(registration_texts.GREETING_FIRST_MESSAGE_TEXT, reply_markup=ReplyKeyboardRemove())
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(2)
    await message.answer(registration_texts.GREETING_SECOND_MESSAGE_TEXT, parse_mode=ParseMode.HTML)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(5)
    await message.answer(registration_texts.GREETING_THIRD_MESSAGE_TEXT)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(5)
    await message.answer(registration_texts.GREETING_FOURTH_MESSAGE_TEXT)
    await GreetingState.fullname.set()

# Получение и проверка имени на Профкомность
async def get_fullname(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)
    db.add_user(message.from_user.id, message.from_user.username, message.text)
    await message.answer(registration_texts.NICE_TO_MEET_TEMPLATE.format(message.text
                                                                         )[:constants.MAX_MESSAGE_LEN],
                         reply_markup=ReplyKeyboardRemove()
                         )
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(2.3)

    # TODO Добавить проверку на участие в Профкоме
    found_tuc = choice((False,))
    if found_tuc:
        db.set_user_tuc(message.from_user.id, 1)
        await message.answer(registration_texts.REGISTERED_TEXT1,
                             )
        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        await asyncio.sleep(4)
        await message.answer(registration_texts.REGISTERED_TEXT2,
                             # reply_markup=registration_markups.
                             )
        await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
        await asyncio.sleep(5)
        await message.answer(registration_texts.IN_TUC_TEXT,
                             )
        await state.finish()
    else:
        await message.answer(registration_texts.NOT_IN_TUC_TEXT,
                             reply_markup=registration_markups.NOT_IN_TUC_MARKUP)
        await GreetingState.not_found.set()

# Повторение ввода имени
async def repeat_fullname_input(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)
    await message.answer(registration_texts.REPEAT_FULLNAME_ASK_TEXT,
                         reply_markup=ReplyKeyboardRemove())
    await GreetingState.fullname.set()

# Регистрация без Профкома
async def register_without_tuc(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)
    await message.answer(registration_texts.REGISTERED_TEXT1,
                         reply_markup=ReplyKeyboardRemove()
                         )
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(2.5)
    await message.answer(registration_texts.REGISTERED_TEXT2,
                         # reply_markup=registration_markups.
                         )
    await state.finish()


# Шуточная регистрация без профкома
async def joke_without_tuc(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)
    await message.answer(registration_texts.JOKE_ANSWER,
                         reply_markup=ReplyKeyboardRemove())
    await asyncio.sleep(2)
    await message.answer(registration_texts.MEANTIME_REGISTERED_TEXT1,
                         )
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(4)
    await message.answer(registration_texts.REGISTERED_TEXT2,
                         # reply_markup=registration_markups.
                         )
    await state.finish()

# Сообщение с вопросом, что с Профкомом
async def offer_tuc_check_query(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)
    await message.answer(registration_texts.NOT_IN_TUC_MANUAL_CHECK_TEXT1)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(3)
    await message.answer(registration_texts.NOT_IN_TUC_MANUAL_CHECK_TEXT2)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(3.5)
    await message.answer(registration_texts.NOT_IN_TUC_MANUAL_CHECK_TEXT3,
                         reply_markup=registration_markups.TUC_MANUAL_CHECK_MARKUP)
    await GreetingState.tuc_check_query.set()


# Отправка в админский чат проверки на Профкомность и регистрация
async def send_tuc_check_query(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_message(chat_id=config.admins_chat_id, text="Привет")  # TODO отправлять админу сообщение в чат
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(1)
    await message.answer(text=registration_texts.TUC_MANUAL_CHECK_SENT_TEXT,
                         reply_markup=ReplyKeyboardRemove())
    await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_PHOTO)
    await asyncio.sleep(3)
    cat_io = await registration_functions.get_random_cat_from_web()
    if cat_io:
        await bot.send_photo(chat_id=message.chat.id, photo=cat_io)
    else:
        cat_io = registration_functions.get_cat_from_files()
        await bot.send_photo(chat_id=message.chat.id, photo=cat_io)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(3)
    await message.answer(registration_texts.MEANTIME_REGISTERED_TEXT1,
                         )
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(4)
    await message.answer(registration_texts.REGISTERED_TEXT2,
                         # reply_markup=registration_markups.
                         )
    await state.finish()


def register_registration_handlers():
    dp.register_message_handler(greetings, lambda s: s != GreetingState.block, commands=['start'])
    dp.register_message_handler(get_fullname,
                                state=GreetingState.fullname)
    dp.register_message_handler(offer_tuc_check_query,
                                text=registration_texts.ACTUALLY_IN_TUC_BUTTON_TEXT,
                                state=GreetingState.not_found)
    dp.register_message_handler(register_without_tuc,
                                text=registration_texts.NOT_IN_TUC_BUTTON_TEXT,
                                state=GreetingState.not_found)
    dp.register_message_handler(repeat_fullname_input,
                                text=registration_texts.FULLNAME_FAILURE_BUTTON_TEXT,
                                state=GreetingState.not_found)
    dp.register_message_handler(send_tuc_check_query,
                                text=registration_texts.SEND_TUC_MANUAL_CHECK_QUERY_TEXT,
                                state=GreetingState.tuc_check_query)
    dp.register_message_handler(joke_without_tuc,
                                text=registration_texts.NO_TUC_MANUAL_CHECK_QUERY_TEXT,
                                state=GreetingState.tuc_check_query)
