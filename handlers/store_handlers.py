from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, ParseMode, InputMediaPhoto, InlineKeyboardMarkup

from bot_create import store_cached_imgs
import constants
from callbacks.store_callbacks import STORE_CATEGORY_CB, ITEM_CB, BUY_NO_COLORS_SIZES_CB, \
    BUY_COLORS_SIZES_CB, STORE_MAIN_CB, BUY_CONFIRM_COLORS_SIZES_CB, BUY_CONFIRM_NO_COLORS_SIZES_CB
from markups import store_markups
from bot_create import bot, dp, config
from main import db
from texts import menu_texts, store_texts

MINIATURE_NAME = "main.png"


async def store_categories_show(update: [Message, CallbackQuery], state: FSMContext):
    categories = db.get_stuff_categories()
    money = db.get_user_money(update.from_user.id)
    if db.in_tuc(update.from_user.id):
        text = store_texts.STORE_CATEGORIES_WITH_TUC_TEMPLATE.format(money)
        markup = store_markups.get_store_markup(categories, 1)
    else:
        text = store_texts.STORE_CATEGORIES_NO_TUC_TEMPLATE.format(money)
        markup = store_markups.get_store_markup(categories, 0)
    if isinstance(update, Message):
        message = update
        await store_cached_imgs.send_cached_img(message, MINIATURE_NAME, text, reply_markup=markup,
                                                parse_mode=ParseMode.HTML, message_edit=False)
    elif isinstance(update, CallbackQuery):
        message = update.message
        await store_cached_imgs.send_cached_img(message, MINIATURE_NAME, text, reply_markup=markup,
                                                parse_mode=ParseMode.HTML, message_edit=True)
    else:
        raise ValueError("Неверный update.")


async def show_category(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    category_id = callback_data.get("category_id")
    text, markup = store_texts.get_category_list_text_markup(db, category_id, callback.from_user.id)
    img_path = db.get_category_img_path(category_id)
    markup = markup.add(
        InlineKeyboardButton("Назад",
                             callback_data=STORE_MAIN_CB))

    if img_path:
        await store_cached_imgs.send_cached_img(callback.message, img_path, text, reply_markup=markup,
                                                parse_mode=ParseMode.HTML, message_edit=True)
    else:
        await callback.message.edit_caption(caption=text,
                                            reply_markup=markup)


async def show_thing(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    stuff_id = callback_data["stuff_id"]
    if db.is_color_size_stuff(stuff_id):
        text, markup = store_texts.get_thing_color_size_text_markup(db, stuff_id, db.in_tuc(callback.from_user.id),
                                                                    callback.from_user.id)
    else:
        text, markup = store_texts.get_thing_no_color_size_text_markup(db, stuff_id, db.in_tuc(callback.from_user.id),
                                                                       callback.from_user.id)
    category_id = db.get_stuff_info(stuff_id, "stuff_category_id")[0]
    markup.add(
        InlineKeyboardButton("Назад",
                             callback_data=STORE_CATEGORY_CB.new(
                                 category_id=category_id)))
    img_path = db.get_stuff_img_path(stuff_id)
    if img_path:
        await store_cached_imgs.send_cached_img(callback.message, img_path, text, reply_markup=markup,
                                                parse_mode=ParseMode.HTML, message_edit=True)
    else:
        await callback.message.edit_caption(text,
                                            reply_markup=markup,
                                            parse_mode=ParseMode.HTML)


async def confirm_color_size_buy(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    colors_sizes_id = callback_data["colors_sizes_id"]
    stuff_id = db.get_stuff_sizes_colors_texts_info(colors_sizes_id, "stuff_id")[0]
    text, markup = store_texts.get_thing_color_size_confirmation_text_markup(db, colors_sizes_id,
                                                                             db.in_tuc(callback.from_user.id))
    markup.add(
        InlineKeyboardButton("Назад",
                             callback_data=ITEM_CB.new(
                                 stuff_id=stuff_id)))
    await callback.message.edit_caption(text,
                                        reply_markup=markup,
                                        parse_mode=ParseMode.HTML)


async def confirm_no_color_size_buy(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    stuff_id = callback_data["stuff_id"]
    text, markup = store_texts.get_thing_no_color_size_confirmation_text_markup(db, stuff_id,
                                                                                db.in_tuc(callback.from_user.id))
    markup.add(
        InlineKeyboardButton("Назад",
                             callback_data=ITEM_CB.new(
                                 stuff_id=stuff_id)))
    await callback.message.edit_caption(text,
                                        reply_markup=markup,
                                        parse_mode=ParseMode.HTML)


async def color_size_purchase_processing(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    colors_sizes_id = callback_data["colors_sizes_id"]
    stuff_id, = db.get_stuff_sizes_colors_texts_info(colors_sizes_id, "stuff_id")
    category_id, = db.get_stuff_info(stuff_id, "stuff_category_id")
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Назад",
                             callback_data=STORE_CATEGORY_CB.new(category_id=category_id)
                             ))
    error = db.buy_size_color_stuff(callback.from_user.id, colors_sizes_id)
    if not error:
        await callback.message.edit_caption(store_texts.get_size_color_thing_has_bought_text(
            db,
            colors_sizes_id
        ), reply_markup=markup)
    elif error == 1:
        await callback.message.edit_caption(store_texts.THING_NOT_ENOUGH_MONEY_TEXT, reply_markup=markup)
    elif error == 2:
        await callback.message.edit_caption(store_texts.THING_HAS_BEEN_SOLD_TEXT, reply_markup=markup)
    elif error == 3:
        await callback.message.edit_caption(store_texts.TRANSACTION_ERROR, reply_markup=markup)
    else:
        raise ValueError("Неизвестное значение ошибки.")


async def color_no_size_purchase_processing(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    stuff_id = callback_data["stuff_id"]
    category_id, = db.get_stuff_info(stuff_id, "stuff_category_id")
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton("Назад",
                             callback_data=STORE_CATEGORY_CB.new(category_id=category_id)
                             ))
    error = db.buy_no_size_color_stuff(callback.from_user.id, stuff_id)
    if not error:
        await callback.message.edit_caption(store_texts.get_no_size_color_thing_has_bought_text(
            db,
            stuff_id
        ),
            reply_markup=markup)
    elif error == 1:
        await callback.message.edit_caption(store_texts.THING_NOT_ENOUGH_MONEY_TEXT,
                                            reply_markup=markup)
    elif error == 2:
        await callback.message.edit_caption(store_texts.THING_HAS_BEEN_SOLD_TEXT,
                                            reply_markup=markup)
    elif error == 3:
        await callback.message.edit_caption(store_texts.TRANSACTION_ERROR,
                                            reply_markup=markup)
    else:
        raise ValueError("Неизвестное значение ошибки.")


def register_store_handlers():
    dp.register_message_handler(store_categories_show,
                                text=menu_texts.MENU_STORE_BUTTON_TEXT,
                                state=None)
    dp.register_callback_query_handler(show_category,
                                       STORE_CATEGORY_CB.filter(),
                                       state=None)
    dp.register_callback_query_handler(show_thing,
                                       ITEM_CB.filter(),
                                       state=None)
    dp.register_callback_query_handler(confirm_no_color_size_buy,
                                       BUY_NO_COLORS_SIZES_CB.filter(),
                                       state=None)
    dp.register_callback_query_handler(confirm_color_size_buy,
                                       BUY_COLORS_SIZES_CB.filter(),
                                       state=None)
    dp.register_callback_query_handler(store_categories_show,
                                       text=STORE_MAIN_CB,
                                       state=None)
    dp.register_callback_query_handler(color_size_purchase_processing,
                                       BUY_CONFIRM_COLORS_SIZES_CB.filter(),
                                       state=None)
    dp.register_callback_query_handler(color_no_size_purchase_processing,
                                       BUY_CONFIRM_NO_COLORS_SIZES_CB.filter(),
                                       state=None)
