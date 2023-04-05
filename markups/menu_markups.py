from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from texts import menu_texts


menu_markup = ReplyKeyboardMarkup()
menu_markup.add(menu_texts.MENU_GET_QR_BUTTON_TEXT)
menu_markup.add(menu_texts.MENU_STORE_BUTTON_TEXT)
menu_markup.add(menu_texts.MENU_POSTER_BUTTON_TEXT, menu_texts.MENU_HELP_BUTTON_TEXT)