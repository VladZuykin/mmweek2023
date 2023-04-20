from aiogram.types import ReplyKeyboardMarkup
from texts import org_scaner_texts, org_menu_texts, org_promo_texts
from callbacks import org_menu_callbacks
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

org_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
org_menu_markup.add(org_menu_texts.MENU_SCANER_BUTTON_TEXT)
org_menu_markup.add(org_menu_texts.MENU_MERCH_BUTTON_TEXT)
org_menu_markup.add(org_menu_texts.MENU_CREATE_PROMO_BUTTON_TEXT,
                    org_menu_texts.MENU_LIST_PROMO_BUTTON_TEXT)
org_menu_markup.add(org_menu_texts.MENU_GIVE_ACCESS_BUTTON_TEXT)


back_to_menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
back_to_menu_markup.add(org_menu_texts.BACK_TO_MENU_BUTTON_TEXT)


random_promo_markup = ReplyKeyboardMarkup(resize_keyboard=True)
random_promo_markup.add(org_promo_texts.RANDOM_PROMO_BUTTON_TEXT)
random_promo_markup.add(org_menu_texts.BACK_TO_MENU_BUTTON_TEXT)


infinite_uses_promo_markup = ReplyKeyboardMarkup(resize_keyboard=True)
infinite_uses_promo_markup.add(org_promo_texts.INFINITE_USES_BUTTON_TEXT)
infinite_uses_promo_markup.add(org_menu_texts.BACK_TO_MENU_BUTTON_TEXT)


yes_no_markup = InlineKeyboardMarkup()
yes_no_markup.add(InlineKeyboardButton(text=org_scaner_texts.YES_BUTTON_TEXT,
                                       callback_data=org_menu_callbacks.GIVE_MONEY_CB.new(1)),
                  InlineKeyboardButton(text=org_scaner_texts.NO_BUTTON_TEXT,
                                       callback_data=org_menu_callbacks.GIVE_MONEY_CB.new(0)))
