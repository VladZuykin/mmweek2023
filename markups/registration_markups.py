from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.callback_data import CallbackData

from texts.registration_texts import NOT_IN_TUC_BUTTON_TEXT, FULLNAME_FAILURE_BUTTON_TEXT, ACTUALLY_IN_TUC_BUTTON_TEXT, \
    SEND_TUC_MANUAL_CHECK_QUERY_TEXT, NO_TUC_MANUAL_CHECK_QUERY_TEXT, IT_IS_ME_SIMILAR_BUTTON_TEXT, \
    IT_IS_NOT_ME_SIMILAR_BUTTON_TEXT

NOT_IN_TUC_MARKUP = ReplyKeyboardMarkup([[KeyboardButton(NOT_IN_TUC_BUTTON_TEXT)],
                                         [KeyboardButton(FULLNAME_FAILURE_BUTTON_TEXT),
                                          KeyboardButton(ACTUALLY_IN_TUC_BUTTON_TEXT)]],
                                        resize_keyboard=True, one_time_keyboard=True)

TUC_MANUAL_CHECK_MARKUP = ReplyKeyboardMarkup([[KeyboardButton(SEND_TUC_MANUAL_CHECK_QUERY_TEXT)],
                                               [KeyboardButton(NO_TUC_MANUAL_CHECK_QUERY_TEXT)]],
                                              resize_keyboard=True, one_time_keyboard=True)
tuc_check_cd = CallbackData("tuc_check", "tg_id", "status")

SIMILAR_ASK_MARKUP = ReplyKeyboardMarkup([[KeyboardButton(IT_IS_ME_SIMILAR_BUTTON_TEXT)],
                                          [KeyboardButton(IT_IS_NOT_ME_SIMILAR_BUTTON_TEXT)]],
                                         resize_keyboard=True, one_time_keyboard=True)


def get_tuc_check_inline_keyboard(tg_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Он в ПК", callback_data=tuc_check_cd.new(tg_id=tg_id, status=1)))
    markup.add(InlineKeyboardButton("Он не в ПК", callback_data=tuc_check_cd.new(tg_id=tg_id, status=0)))
    return markup
