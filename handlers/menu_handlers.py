import asyncio
import collections
import datetime
from random import choice
from typing import Union
from io import BytesIO

import aiogram
import qrcode
from aiogram import types
from aiogram.utils.exceptions import MessageCantBeEdited
from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, ReplyKeyboardRemove, Message, CallbackQuery, ChatActions, ReplyKeyboardMarkup
from magic_filter import F
import datetime as dt

import constants
import middleware.functions
from fsm import menu_fsm
from fsm.registration_fsm import GreetingState
from functions import menu_functions
from markups import menu_markups
from bot_create import bot, dp, config
from main import db
from markups.menu_markups import menu_markup
from middleware import antispam
from texts import menu_texts, registration_texts
from callbacks import menu_callbacks


async def any_message_menu_respond(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await asyncio.sleep(0.5)
    await state.finish()
    await message.answer(menu_texts.RESPOND_TEXT,
                         reply_markup=menu_markup)


async def send_menu_on_update(update: Union[Message, CallbackQuery], state: FSMContext):
    await state.finish()
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


def get_events_for(tg_id):
    if db.get_admin_level(tg_id) > 0:
        events = db.get_events_summary(True)
    else:
        events = db.get_events_summary(False)
    return events


async def edit_show_schedule(callback: CallbackQuery, state: FSMContext):
    events = get_events_for(callback.from_user.id)
    await callback.message.edit_text(menu_texts.get_schedule_text(events),
                                     parse_mode=ParseMode.HTML,
                                     reply_markup=menu_markups.get_schedule_markup(events))


async def show_schedule(message: types.Message, state: FSMContext):
    events = get_events_for(message.from_user.id)
    await message.answer(menu_texts.get_schedule_text(events),
                         parse_mode=ParseMode.HTML,
                         reply_markup=menu_markups.get_schedule_markup(events))


async def show_event(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    event_id = int(callback_data.get('event_id'))
    event = db.get_event(event_id)
    text = menu_texts.get_event_text(event)
    markup = menu_markups.get_event_markup(event)
    await callback.message.edit_text(text,
                                     reply_markup=markup,
                                     parse_mode=ParseMode.HTML
                                     )


# async def show_help(message: types.Message, state: FSMContext):
#     await message.answer(db.get_help_text(),
#                          reply_markup=menu_markups.help_markup,
#                          parse_mode=ParseMode.HTML)


async def support_input(message: types.Message, state: FSMContext):
    await message.answer(menu_texts.HELP_INPUT_REQUEST,
                         reply_markup=ReplyKeyboardMarkup(
                             resize_keyboard=True, one_time_keyboard=True
                         ).add(menu_markups.CANCEL_BUTTON)
                         )
    await menu_fsm.SupportState.input_wait.set()


async def cancel(message: types.Message, state: FSMContext):
    await message.answer(menu_texts.BACK_TO_MENU_TEXT,
                         reply_markup=menu_markups.menu_markup)
    await state.finish()


async def support_sent(message: types.Message, state: FSMContext):
    user = message.from_user
    support_request_sent = db.get_last_support_request_time(user.id)
    now = dt.datetime.now(tz=constants.TZ)
    if support_request_sent and  now < support_request_sent + constants.SUPPORT_TIMEDELTA:
        ans_text = menu_texts.TOO_FREQUENTLY_TEMPLATE.format(constants.SUPPORT_TIMEDELTA_ACCUSATIVE_STR)
        await message.answer(ans_text,
                             reply_markup=menu_markups.menu_markup)
    else:
        await bot.send_message(chat_id=config.support_chat_id,
                               text=menu_texts.TO_SUPPORT_MESSAGE_TEMPLATE.format(user.username, user.url, message.text))
        await message.answer(menu_texts.HELP_MESSAGE_SENT,
                             reply_markup=menu_markups.menu_markup)
        db.add_transaction(constants.TransactionTypes.SUPPORT_REQUEST.value,
                           message.from_user.id, None, message.text)
    await state.finish()


async def promo_respond(message: types.Message, state: FSMContext):
    await message.answer(menu_texts.PROMO_INPUT_REQUEST,
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True,
                                                          one_time_keyboard=True).add(menu_markups.CANCEL_BUTTON))
    await menu_fsm.PromoState.input_wait.set()


async def promo_input(message: types.Message, state: FSMContext):
    promo = message.text
    error_code = db.use_promo(message.from_user.id, promo)
    if error_code == 0:
        await message.answer(menu_texts.PROMO_SUCCESSFULLY_ACTIVATED_TEXT,
                             reply_markup=menu_markups.menu_markup)
        await state.finish()
    elif error_code == 2:
        await message.answer(menu_texts.PROMO_ALREADY_USED,
                             reply_markup=menu_markups.menu_markup)
        await state.finish()
    else:
        await message.answer(menu_texts.PROMO_DOESNT_EXISTS,
                             reply_markup=ReplyKeyboardMarkup(resize_keyboard=True,
                                                              one_time_keyboard=True).add(menu_markups.CANCEL_BUTTON)
                             )


async def show_shop_temp_message(message: types.Message, state: FSMContext):
    await message.answer(menu_texts.STORE_TEMP_TEXT)


def register_menu_handlers():
    dp.register_message_handler(send_menu_on_update,
                                F.from_user.func(lambda user: db.user_registered(user.id)),
                                state="*",
                                commands=['start'])
    dp.register_message_handler(generate_code,
                                text=menu_texts.MENU_GET_CODE_BUTTON_TEXT,
                                state="*", )
    dp.register_message_handler(show_profile,
                                text=menu_texts.MENU_PROFILE_BUTTON_TEXT,
                                state="*", )
    # dp.register_message_handler(show_help,

    #                             text=menu_texts.MENU_HELP_BUTTON_TEXT,
    #                             state="*", )
    dp.register_message_handler(show_schedule,
                                text=menu_texts.MENU_SCHEDULE_BUTTON_TEXT,
                                state="*")
    dp.register_callback_query_handler(show_event,
                                       menu_callbacks.EVENT_SCHEDULE_CB.filter())
    dp.register_callback_query_handler(edit_show_schedule,
                                       text=menu_callbacks.EVENT_SCHEDULE_SHOW,
                                       state="*")
    dp.register_message_handler(support_input,
                                text=menu_texts.HELP_BUTTON_TEXT,
                                state=None)
    dp.register_message_handler(cancel,
                                text=menu_texts.CANCEL_TEXT,
                                state=menu_fsm.SupportState.input_wait)
    dp.register_message_handler(cancel,
                                text=menu_texts.BACK_BUTTON_TEXT,
                                state=None)
    dp.register_message_handler(support_sent,
                                state=menu_fsm.SupportState.input_wait
                                )
    dp.register_message_handler(cancel,
                                text=menu_texts.CANCEL_TEXT,
                                state=menu_fsm.PromoState.input_wait,
                                )
    dp.register_message_handler(promo_respond,
                                state=None,
                                text=menu_texts.MENU_PROMO_BUTTON_TEXT)
    dp.register_message_handler(promo_input,
                                state=menu_fsm.PromoState.input_wait
                                )
    dp.register_message_handler(show_shop_temp_message,
                                state=None,
                                text=menu_texts.MENU_STORE_BUTTON_TEXT)
    # Обязательно оставить в конце, чтобы отвечал на остальные сообщения
    dp.register_message_handler(any_message_menu_respond,
                                F.from_user.func(lambda user: db.user_registered(user.id)),
                                state=None)
