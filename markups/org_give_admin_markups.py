from aiogram.types import ReplyKeyboardMarkup
from texts import org_give_admin_texts
from callbacks import org_give_admin_callbacks
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


give_role_cancel_button = InlineKeyboardButton(org_give_admin_texts.CANCEL_BUTTON_TEXT,
                                               callback_data=org_give_admin_callbacks.CANCEL_BUTTON_CB)