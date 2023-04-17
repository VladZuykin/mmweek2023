from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from texts import menu_texts

menu_markup = ReplyKeyboardMarkup()
menu_markup.add(menu_texts.MENU_GET_CODE_BUTTON_TEXT, menu_texts.MENU_PROFILE_BUTTON_TEXT)
menu_markup.add(menu_texts.MENU_SCHEDULE_BUTTON_TEXT, menu_texts.MENU_STORE_BUTTON_TEXT)
menu_markup.add(menu_texts.MENU_PROMO_BUTTON_TEXT, menu_texts.MENU_HELP_BUTTON_TEXT)
