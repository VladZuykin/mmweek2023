import asyncio
import datetime
from random import choice

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import ChatActions, ParseMode, ReplyKeyboardRemove
from aiogram.dispatcher.filters import StateFilter
from magic_filter import F

import constants
from functions import registration_functions
from functions.sleep import sleep
from fsm.registration_fsm import GreetingState
from markups import registration_markups
from markups.menu_markups import menu_markup
from bot_create import bot, dp, config
from main import db
from texts import registration_texts


async def greetings(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(registration_texts.GREETING_FIRST_MESSAGE_TEXT,
                         reply_markup=ReplyKeyboardRemove())
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(2)
    await message.answer(registration_texts.GREETING_SECOND_MESSAGE_TEXT, parse_mode=ParseMode.HTML)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(5)
    await message.answer(registration_texts.GREETING_THIRD_MESSAGE_TEXT)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(5)
    await message.answer(registration_texts.GREETING_FOURTH_MESSAGE_TEXT)
    await GreetingState.fullname.set()


# Получение и проверка имени на Профкомность
async def get_fullname(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(registration_texts.NICE_TO_MEET_TEMPLATE.format(
        message.text[:constants.MAX_FULLNAME_LEN]
    ),
        reply_markup=ReplyKeyboardRemove()
    )
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(2)
    # Добавляем в хранилище полное имя
    await state.update_data(fullname=message.text)

    # Проверка, есть ли похожие в Профкоме
    if similar := db.get_similar(message.text):
        await state.update_data(similar=similar)
        if registration_functions.are_different_content_sentences(similar, message.text):
            await message.answer(registration_texts.FOUND_SIMILAR_TEMPLATE.format(
                registration_functions.get_capitalised_sentence(similar)),
                reply_markup=registration_markups.SIMILAR_ASK_MARKUP)
            await GreetingState.found_similar.set()
        else:
            # TODO Сюда сделать вопрос: да или нет всё-таки
            await ask_if_in_tuc(message, state)
    else:
        await message.answer(registration_texts.NOT_IN_TUC_TEXT,
                             reply_markup=registration_markups.NOT_IN_TUC_MARKUP)
        await GreetingState.not_found.set()


# Проверка, есть ли в ПК, если такой чел нашёлся
async def ask_if_in_tuc(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(registration_texts.ASK_IF_IN_TUC_TEXT,
                         reply_markup=registration_markups.in_tuc_markup)
    await GreetingState.if_in_tuc.set()


# Регистрация с отказом в похожем имени
async def similar_fullname_refused(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(registration_texts.NOT_IN_TUC_TEXT,
                         reply_markup=registration_markups.NOT_IN_TUC_MARKUP)
    await GreetingState.not_found.set()


# Регистрация с Профкомом
async def with_tuc_registration(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    data = await state.get_data()
    fullname = registration_functions.get_capitalised_sentence(data["similar"])
    # Сообщение о регистрации, если нашёл в списках профкома
    db.add_user(message.from_user.id, message.from_user.username, fullname, tuc=1)
    await sleep(1)
    await message.answer(registration_texts.USUAL_REGISTERED_TEXT1,
                         reply_markup=ReplyKeyboardRemove())
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(4)
    await message.answer(registration_texts.REGISTERED_TEXT2,
                         reply_markup=menu_markup
                         )
    # await bot.send_chat_action(message.chat.id, ChatActions.TYPING,
    #                            )
    # await sleep(5)
    # await message.answer(registration_texts.IN_TUC_TEXT,
    #                      reply_markup=menu_markup)
    await state.finish()


# Говорит, что ждёт текст, а не команду
async def request_text(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(registration_texts.WAIT_FOR_TEXT,
                         reply_markup=ReplyKeyboardRemove())
    await GreetingState.fullname.set()


# Повторение ввода имени
async def repeat_fullname_input(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(registration_texts.REPEAT_FULLNAME_ASK_TEXT,
                         reply_markup=ReplyKeyboardRemove())
    await GreetingState.fullname.set()


# Добавление в базу данных без профкомства
async def add_db_no_tuc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    fullname = data["fullname"]
    db.add_user(message.from_user.id, message.from_user.username, fullname, tuc=0)


# Добавление со статусом "на проверке"
async def add_db_unknown_tuc(message: types.Message, state: FSMContext):
    data = await state.get_data()
    fullname = data["fullname"]
    db.add_user(message.from_user.id, message.from_user.username, fullname, tuc=2)


# Регистрация без Профкома
async def register_without_tuc(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await add_db_no_tuc(message, state)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(registration_texts.CAN_JOIN_TUC_TEXT,
                         reply_markup=ReplyKeyboardRemove())
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(2)
    await message.answer(registration_texts.SAD_REGISTERED_TEXT1,
                         parse_mode=ParseMode.HTML,
                         disable_web_page_preview=True)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(2.5)
    await message.answer(registration_texts.REGISTERED_TEXT2,
                         reply_markup=menu_markup
                         )
    await state.finish()


# Шуточная регистрация без профкома
async def joke_without_tuc(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await add_db_no_tuc(message, state)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(registration_texts.JOKE_ANSWER,
                         reply_markup=ReplyKeyboardRemove())
    await sleep(2)
    await message.answer(registration_texts.SAD_REGISTERED_TEXT1,
                         parse_mode=ParseMode.HTML,
                         disable_web_page_preview=True)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(4)
    await message.answer(registration_texts.REGISTERED_TEXT2,
                         reply_markup=menu_markup
                         )
    await state.finish()


# Сообщение с вопросом, что с Профкомом, если не нашёл
async def offer_tuc_check_query(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(registration_texts.NOT_IN_TUC_MANUAL_CHECK_TEXT1,
                         reply_markup=ReplyKeyboardRemove())
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(3)
    await message.answer(registration_texts.NOT_IN_TUC_MANUAL_CHECK_TEXT2)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(3.5)
    await message.answer(registration_texts.NOT_IN_TUC_MANUAL_CHECK_TEXT3,
                         reply_markup=registration_markups.TUC_MANUAL_CHECK_MARKUP)
    await GreetingState.tuc_check_query.set()


# Отправка в админский чат проверки на Профкомность и регистрация
async def send_tuc_check_query(message: types.Message, state: FSMContext):
    await GreetingState.block.set()
    await add_db_unknown_tuc(message, state)
    user = message.from_user
    data = await state.get_data()
    fullname = data["fullname"]
    if fullname:
        fullname = fullname[:constants.MAX_FULLNAME_LEN]
    # Отправка в чат к админам
    await bot.send_message(chat_id=config.admins_chat_id,
                           text=registration_texts.TUC_MANUAL_CHECK_TEMPLATE.format(user.username,
                                                                                    fullname,
                                                                                    user.url),
                           reply_markup=registration_markups.get_tuc_check_inline_keyboard(user.id)
                           )
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(1)
    await message.answer(text=registration_texts.TUC_MANUAL_CHECK_SENT_TEXT,
                         reply_markup=ReplyKeyboardRemove())
    await bot.send_chat_action(message.chat.id, ChatActions.UPLOAD_PHOTO)
    await sleep(3)
    cat_io = await registration_functions.get_random_cat_from_web()
    if cat_io:
        await bot.send_photo(chat_id=message.chat.id, photo=cat_io)
    else:
        cat_io = registration_functions.get_cat_from_files()
        await bot.send_photo(chat_id=message.chat.id, photo=cat_io)
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(3)
    await message.answer(registration_texts.MEANTIME_REGISTERED_TEXT1,
                         )
    await bot.send_chat_action(message.chat.id, ChatActions.TYPING)
    await sleep(4)
    await message.answer(registration_texts.REGISTERED_TEXT2,
                         reply_markup=menu_markup
                         )
    await state.finish()


# Обработка админского клика на кнопки в сообщение с подтверждением профкомности
async def check_tuc_admins_chat_onclick(callback: types.CallbackQuery, state: FSMContext, callback_data: dict):
    if callback.message.reply_markup.inline_keyboard:
        if int(callback_data["status"]) == 1:
            db.set_user_tuc(callback_data["tg_id"], 1)
            res = "в ПК"
        else:
            db.set_user_tuc(callback_data["tg_id"], 0)
            res = "не в пк"
        await callback.message.delete_reply_markup()
        text = callback.message.text
        text += f"\n\nВыбрано: {res}\nВыбрал @{callback.from_user.username}\nв " \
                f"{datetime.datetime.now(tz=constants.TZ).strftime('%H:%M:%S %d.%m.%Y')}"
        await callback.message.edit_text(text)
    else:
        await callback.answer("Вы не успели отметить :(")


def register_registration_handlers():
    dp.register_message_handler(greetings,
                                ~F.from_user.func(lambda user: db.user_registered(user.id)),
                                state=None)
    dp.register_message_handler(greetings,
                                ~F.from_user.func(lambda user: db.user_registered(user.id)),
                                lambda s: s != GreetingState.block,
                                commands=['start'])
    dp.register_message_handler(get_fullname,
                                ~F.text.startswith("/"),
                                state=GreetingState.fullname)
    dp.register_message_handler(request_text,
                                F.text.startswith("/"),
                                state=GreetingState.fullname)
    # dp.register_message_handler(with_tuc_registration,
    #                             text=registration_texts.IT_IS_ME_SIMILAR_BUTTON_TEXT,
    #                             state=GreetingState.found_similar)
    dp.register_message_handler(with_tuc_registration,
                                text=registration_texts.SECOND_CHECK_IN_TUC_BUTTON_TEXT,
                                state=GreetingState.if_in_tuc)
    dp.register_message_handler(register_without_tuc,
                                text=registration_texts.SECOND_CHECK_NOT_IN_TUC_BUTTON_TEXT,
                                state=GreetingState.if_in_tuc)
    dp.register_message_handler(ask_if_in_tuc,
                                text=registration_texts.IT_IS_ME_SIMILAR_BUTTON_TEXT,
                                state=GreetingState.found_similar)
    dp.register_message_handler(similar_fullname_refused,
                                text=registration_texts.IT_IS_NOT_ME_SIMILAR_BUTTON_TEXT,
                                state=GreetingState.found_similar)
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
    dp.register_callback_query_handler(check_tuc_admins_chat_onclick,
                                       registration_markups.tuc_check_cd.filter(),
                                       state="*")
