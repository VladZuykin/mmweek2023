from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton
from texts.registration_texts import NOT_IN_TUC_BUTTON_TEXT, FULLNAME_FAILURE_BUTTON_TEXT, ACTUALLY_IN_TUC_BUTTON_TEXT,\
    SEND_TUC_MANUAL_CHECK_QUERY_TEXT, NO_TUC_MANUAL_CHECK_QUERY_TEXT

NOT_IN_TUC_MARKUP = ReplyKeyboardMarkup([[KeyboardButton(NOT_IN_TUC_BUTTON_TEXT)],
                                         [KeyboardButton(FULLNAME_FAILURE_BUTTON_TEXT),
                                          KeyboardButton(ACTUALLY_IN_TUC_BUTTON_TEXT)]],
                                        resize_keyboard=True, one_time_keyboard=True)

TUC_MANUAL_CHECK_MARKUP = ReplyKeyboardMarkup([[KeyboardButton(SEND_TUC_MANUAL_CHECK_QUERY_TEXT)],
                                               [KeyboardButton(NO_TUC_MANUAL_CHECK_QUERY_TEXT)]],
                                              resize_keyboard=True, one_time_keyboard=True)
