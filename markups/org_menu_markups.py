from aiogram.types import ReplyKeyboardMarkup
from texts import org_scaner_texts
from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

org_menu_markup = ReplyKeyboardMarkup()
org_menu_markup.add(org_scaner_texts.MENU_SCANER_BUTTON_TEXT)
org_menu_markup.add(org_scaner_texts.MENU_MERCH_BUTTON_TEXT)
org_menu_markup.add(org_scaner_texts.MENU_CREATE_PROMO_BUTTON_TEXT,
                    org_scaner_texts.MENU_LIST_PROMO_BUTTON_TEXT)
org_menu_markup.add(org_scaner_texts.MENU_GIVE_ACCESS_BUTTON_TEXT)

GIVE_MONEY_CB = CallbackData("give_money_confirmation", "decision")


def get_yes_no_markup():
    yes_no = InlineKeyboardMarkup()
    yes_no.add(InlineKeyboardButton(text="Да", callback_data=GIVE_MONEY_CB.new(1)),
               InlineKeyboardButton(text="Нет", callback_data=GIVE_MONEY_CB.new(0)))
    return yes_no
