from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callbacks.org_merch_issuance_callbacks import MERCH_ISSUANCE_LESS_CB, MERCH_ISSUANCE_MORE_CB, \
    MERCH_ISSUANCE_CONFIRM_CB, CANCEL_TEXT_CB, MERCH_RETURN_BACK_CONFIRM_CB, MERCH_RETURN_BACK_LESS_CB,\
    MERCH_RETURN_BACK_MORE_CB
from database.org_db_funcs import OrgDataBase


def get_merch_issuance_markup(db: OrgDataBase, purchases_id, k):
    count, issued = db.execute("SELECT count, issued FROM purchases WHERE id = ?",
                               purchases_id, fetch="one")
    markup = InlineKeyboardMarkup()
    # if k != 0 and k <= count - issued:
    markup.insert(InlineKeyboardButton("-", callback_data=MERCH_ISSUANCE_LESS_CB))
    markup.insert(InlineKeyboardButton(f"{k}", callback_data="very_nothing"))
    # if k < count - issued:
    markup.insert(InlineKeyboardButton("+", callback_data=MERCH_ISSUANCE_MORE_CB))
    markup.add(InlineKeyboardButton("Подтвердить", callback_data=MERCH_ISSUANCE_CONFIRM_CB),
               InlineKeyboardButton("Отменить", callback_data=CANCEL_TEXT_CB))
    return markup

def get_merch_return_back_markup(db: OrgDataBase, purchases_id, k):
    count, issued = db.execute("SELECT count, issued FROM purchases WHERE id = ?",
                               purchases_id, fetch="one")
    markup = InlineKeyboardMarkup()
    markup.insert(InlineKeyboardButton("-", callback_data=MERCH_RETURN_BACK_LESS_CB))
    markup.insert(InlineKeyboardButton(f"{k}", callback_data="very_nothing"))
    markup.insert(InlineKeyboardButton("+", callback_data=MERCH_RETURN_BACK_MORE_CB))
    markup.add(InlineKeyboardButton("Подтвердить", callback_data=MERCH_RETURN_BACK_CONFIRM_CB),
               InlineKeyboardButton("Отменить", callback_data=CANCEL_TEXT_CB))
    return markup
