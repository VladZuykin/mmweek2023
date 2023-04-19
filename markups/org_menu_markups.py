from aiogram.types import ReplyKeyboardMarkup
from texts import org_scaner_texts, org_menu_texts
from callbacks import org_menu_callbacks
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

org_menu_markup = ReplyKeyboardMarkup()
org_menu_markup.add(org_menu_texts.MENU_SCANER_BUTTON_TEXT)
org_menu_markup.add(org_menu_texts.MENU_MERCH_BUTTON_TEXT)
org_menu_markup.add(org_menu_texts.MENU_CREATE_PROMO_BUTTON_TEXT,
                    org_menu_texts.MENU_LIST_PROMO_BUTTON_TEXT)
org_menu_markup.add(org_menu_texts.MENU_GIVE_ACCESS_BUTTON_TEXT)


def get_yes_no_markup():
    yes_no = InlineKeyboardMarkup()
    yes_no.add(InlineKeyboardButton(text=org_scaner_texts.YES_BUTTON_TEXT,
                                    callback_data=org_menu_callbacks.GIVE_MONEY_CB.new(1)),
               InlineKeyboardButton(text=org_scaner_texts.NO_BUTTON_TEXT,
                                    callback_data=org_menu_callbacks.GIVE_MONEY_CB.new(0)))
    return yes_no
