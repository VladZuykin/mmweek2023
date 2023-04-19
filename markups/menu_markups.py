from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from callbacks import menu_callbacks
from texts import menu_texts

CLOSE_INLINE_BUTTON = InlineKeyboardButton("Закрыть", callback_data=menu_callbacks.CLOSE_BUTTON_CALLBACK_DATA)

CANCEL_BUTTON = KeyboardButton(menu_texts.CANCEL_TEXT)

menu_markup = ReplyKeyboardMarkup(resize_keyboard=True)
menu_markup.add(menu_texts.MENU_GET_CODE_BUTTON_TEXT, menu_texts.MENU_PROFILE_BUTTON_TEXT)
menu_markup.add(menu_texts.MENU_SCHEDULE_BUTTON_TEXT, menu_texts.MENU_STORE_BUTTON_TEXT)
menu_markup.add(menu_texts.MENU_PROMO_BUTTON_TEXT, menu_texts.MENU_HELP_BUTTON_TEXT)

help_markup = ReplyKeyboardMarkup().add(menu_texts.HELP_BUTTON_TEXT).add(menu_texts.BACK_BUTTON_TEXT)


def get_schedule_markup(events_summary):  # events_summary - список [(id, name, datetime), (...), ..., (...)]
    if not events_summary:
        return None
    markup = InlineKeyboardMarkup()
    for event in events_summary:
        name = event[1]
        markup.add(InlineKeyboardButton(name, callback_data=menu_callbacks.EVENT_SCHEDULE_CB.new(event[0])))
    return markup


def get_event_markup(event):
    markup = InlineKeyboardMarkup()
    if event:
        text, url = event.get("button_text"), event.get("button_url")
        if url and text:
            markup.add(InlineKeyboardButton(text, url=url))
    markup.add(InlineKeyboardButton("Назад",
                                    callback_data=menu_callbacks.EVENT_SCHEDULE_SHOW))
    return markup
