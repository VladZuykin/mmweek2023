from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from callbacks.store_callbacks import STORE_CATEGORY_CB, JOIN_TUC_CB

TUC_JOIN_BUTTON_TEXT = "Вступление в Профком"


def get_store_markup(categories, tuc):  # categories: [(1, "Верхняя одежда"),...]
    markup = InlineKeyboardMarkup()
    for category_id, name in categories:
        markup.add(InlineKeyboardButton(name,
                                        callback_data=STORE_CATEGORY_CB.new(category_id=category_id)))
    if not tuc:
        markup.add(InlineKeyboardButton(TUC_JOIN_BUTTON_TEXT, url="https://m.vk.com/@mmprofkom-vstuplenie-v-profkom"))
    return markup
