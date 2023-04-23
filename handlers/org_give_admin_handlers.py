import datetime as dt
from enum import Enum
from typing import Union

import constants

from aiogram.types import Message, ParseMode, CallbackQuery
from aiogram.dispatcher import FSMContext

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from callbacks import org_give_admin_callbacks, menu_callbacks
from markups import org_menu_markups, menu_markups, org_give_admin_markups
from texts import org_menu_texts, org_give_admin_texts
from org_bot_create import dp, db
from middleware import admins
from fsm.give_acess_fsm import GiveAccessStates


@admins.check(3)
async def access_type_choose(update: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(update, Message):
        message = update
    else:
        message = update.message
    await message.answer(org_give_admin_texts.ACCESS_KINDS_TEXT,
                         reply_markup=ReplyKeyboardMarkup(
                             resize_keyboard=True
                         ).add(org_give_admin_texts.FIRST_LEVEL_ADMIN_BUTTON_TEXT).add(
                             org_give_admin_texts.SECOND_LEVEL_ADMIN_BUTTON_TEXT).add(
                             org_give_admin_texts.THIRD_LEVEL_ADMIN_BUTTON_TEXT).add(
                             org_give_admin_texts.MENU_BUTTON_TEXT),
                         parse_mode=ParseMode.HTML)
    await GiveAccessStates.choose_role.set()

@admins.check(3)
async def level_2_3_chose(message: Message, state: FSMContext):
    await state.storage.update_data(chat=message.chat.id, user=message.from_user.id, data={"event": None,
                                                                                           "admin_level": message.text})
    await admin_tg_input(message, state)

@admins.check(3)
async def admin_tg_input(update: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(update, Message):
        data = await state.storage.get_data(chat=update.chat.id, user=update.from_user.id)
        message = update
    else:
        data = await state.storage.get_data(chat=update.message.chat.id, user=update.from_user.id)
        message = update.message
    event = data.get("event")
    role = data.get("admin_level")
    if event is not None:
        event_name = db.get_event(event)["name"]
        text = org_give_admin_texts.USERNAME_WITH_EVENT_INPUT_TEMPLATE.format(role, event_name)
    else:
        text = org_give_admin_texts.USERNAME_NO_EVENT_INPUT_TEMPLATE.format(role)
    await message.answer(text,
                         reply_markup=ReplyKeyboardMarkup(
                             resize_keyboard=True
                         ).add(
                             org_give_admin_texts.CANCEL_BUTTON_TEXT),
                         parse_mode=ParseMode.HTML)
    await GiveAccessStates.choose_user.set()

@admins.check(3)
async def role_confirmation(message: Message, state: FSMContext):
    data = await state.storage.get_data(chat=message.chat.id, user=message.from_user.id)
    role = data["admin_level"]
    event = data.get("event")
    username = message.text
    if username.startswith("@"):
        username = username[1:]
    if tg_id := db.get_user_id_by_username(message.text):
        fullname = db.get_fullname(tg_id)
        await state.storage.update_data(chat=message.chat.id, user=message.from_user.id, data={"tg_id": tg_id,
                                                                                               "username": username})
        if event is not None:
            event_name = db.get_event(event)["name"]
            text = org_give_admin_texts.ROLE_CONFIRMATION_WITH_EVENT_TEMPLATE.format(f"{fullname} (@{username})",
                                                                                     role,
                                                                                     event_name)
        else:
            text = org_give_admin_texts.ROLE_CONFIRMATION_NO_EVENT_TEMPLATE.format(f"{fullname} (@{username})",
                                                                                   role)
        await message.answer(text,
                             reply_markup=ReplyKeyboardMarkup(
                                 resize_keyboard=True
                             ).add(org_give_admin_texts.CONFIRM_BUTTON).add(org_give_admin_texts.CANCEL_BUTTON_TEXT),
                             parse_mode=ParseMode.HTML)
        await GiveAccessStates.role_confirmation.set()
    else:
        await message.answer(org_give_admin_texts.ROLE_NOT_FOUND_TEXT)
        await admin_tg_input(message, state)

@admins.check(3)
async def role_confirmed(message: Message, state: FSMContext):
    data = await state.storage.get_data(chat=message.chat.id, user=message.from_user.id)
    role = data["admin_level"]
    event = data.get("event")
    tg_id = data.get("tg_id")
    username = data.get("username")
    fullname = db.get_fullname(tg_id)
    if event is None:
        text = org_give_admin_texts.ACCESS_GIVEN_NO_EVENT_TEMPLATE.format(f"{fullname} (@{username})",
                                                                          role)
        if role == org_give_admin_texts.SECOND_LEVEL_ADMIN_BUTTON_TEXT:
            db.set_level_2_3_admin(tg_id, 2, message.from_user.id)
        elif role == org_give_admin_texts.THIRD_LEVEL_ADMIN_BUTTON_TEXT:
            db.set_level_2_3_admin(tg_id, 3, message.from_user.id)
        else:
            raise ValueError("Неверная роль.")
    else:
        event_name = db.get_event(event)["name"]
        text = org_give_admin_texts.ACCESS_GIVE_WITH_EVENT_TEMPLATE.format(f"{fullname} (@{username})",
                                                                           role,
                                                                           event_name)
        db.set_level_1_admin(tg_id, event, message.from_user.id)

    await message.answer(text,
                         parse_mode=ParseMode.HTML)
    await admin_tg_input(message, state)

@admins.check(3)
async def level1_event_choose(message: Message, state: FSMContext):
    await state.storage.update_data(chat=message.chat.id, user=message.from_user.id, data={"event": None,
                                                                                           "admin_level": message.text})
    events_summary = db.get_events_summary(show_all=True)
    markup = menu_markups.get_schedule_markup(events_summary)
    await message.answer("Отличный выбор.", reply_markup=ReplyKeyboardMarkup(resize_keyboard=True
                                                                             ).add(
        org_give_admin_texts.CANCEL_BUTTON_TEXT))
    await message.answer(org_give_admin_texts.CHOOSE_EVENT_TEXT,
                         reply_markup=markup,
                         parse_mode=ParseMode.HTML)
    await GiveAccessStates.choose_event.set()

@admins.check(3)
async def edit_role_user_input(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    await callback.message.delete()
    event = callback_data.get("event_id")
    await state.storage.update_data(chat=callback.message.chat.id, user=callback.from_user.id,
                                    data={"event": event})
    await admin_tg_input(callback, state)


async def menu_return(message: Message, state: FSMContext):
    await message.answer(org_give_admin_texts.MENU_RETURN_TEXT,
                         reply_markup=org_menu_markups.org_menu_markup,
                         parse_mode=ParseMode.HTML)
    await state.finish()

def register_org_promo_handlers():
    dp.register_message_handler(access_type_choose,
                                text=org_menu_texts.MENU_GIVE_ACCESS_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(access_type_choose,
                                text=org_give_admin_texts.CANCEL_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(access_type_choose,
                                text=org_give_admin_texts.CANCEL_BUTTON_TEXT,
                                state=GiveAccessStates.choose_event)
    dp.register_message_handler(access_type_choose,
                                text=org_give_admin_texts.ROLE_CHOOSE_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(level1_event_choose,
                                text=org_give_admin_texts.FIRST_LEVEL_ADMIN_BUTTON_TEXT,
                                state=GiveAccessStates.choose_role)
    dp.register_callback_query_handler(edit_role_user_input,
                                       menu_callbacks.EVENT_SCHEDULE_CB.filter(),
                                       state=GiveAccessStates.choose_event)
    dp.register_message_handler(level_2_3_chose,
                                text=org_give_admin_texts.SECOND_LEVEL_ADMIN_BUTTON_TEXT,
                                state=GiveAccessStates.choose_role)
    dp.register_message_handler(level_2_3_chose,
                                text=org_give_admin_texts.THIRD_LEVEL_ADMIN_BUTTON_TEXT,
                                state=GiveAccessStates.choose_role)
    dp.register_message_handler(role_confirmed,
                                text=org_give_admin_texts.CONFIRM_BUTTON,
                                state=GiveAccessStates.role_confirmation)
    dp.register_message_handler(menu_return,
                                text=org_give_admin_texts.MENU_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(role_confirmation,
                                state=GiveAccessStates.choose_user)
