import random
import string
import datetime as dt
import constants
from database.db_funcs import DataBase

from texts import org_promo_texts
from middleware import functions


def get_generate_promo_code(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(length))


def get_string_datetime(datetime: dt.datetime):
    return str(datetime.day) + "." + str(datetime.month) + "." + str(datetime.year) \
           + " " + str(datetime.hour) + "." + str(datetime.minute)


def get_promo_added_text(can_use, period_time, period_type):
    if can_use == -1:
        can_use = org_promo_texts.INFINITE_USES_TEXT
    if period_type == constants.PERIOD_TYPES[0]:
        period = functions.dtdict_to_str(functions.dt_to_dtdict(dt.timedelta(hours=period_time)))
    else:
        period = functions.dtdict_to_str(functions.dt_to_dtdict(dt.timedelta(days=period_time)))
    return org_promo_texts.PROMO_ADDED_INFO_TEMPLATE.format(period,
                                                            str(can_use))


def get_promo_to_list_text(can_use, dt_ends: dt.datetime, num_uses=0):
    month = ("0" + str(dt_ends.month))[-2:]
    minute = ("0" + str(dt_ends.minute))[-2:]
    if can_use == -1:
        uses = org_promo_texts.INFINITE_USES_TEXT
    else:
        uses = str(num_uses) + "/" + str(can_use)
    return org_promo_texts.PROMO_TO_LIST_INFO_TEMPLATE.format(str(dt_ends.day) + "."
                                                              + month + "."
                                                              + str(dt_ends.year) + " "
                                                              + str(dt_ends.hour) + ":"
                                                              + minute,
                                                              uses)


def get_admin_list_text(db: DataBase):
    level1_list = db.get_admin_list(1)
    text = "<b>Сила-персила</b>\n"
    for num, data in enumerate(level1_list):
        tg_id, username, full_name, event_id = data
        event = db.get_event(event_id)
        text += f"{num + 1}. <code>@{username}</code> {full_name} - {event['name']}\n"
    if not level1_list:
        text += "Пусто.\n"
    text += "\n<b>Гали</b>\n"
    level2_list = db.get_admin_list(2)
    for num, data in enumerate(level2_list):
        tg_id, username, full_name, event_id = data
        text += f"{num + 1}. @{username} {full_name}\n"
    if not level2_list:
        text += "Пусто.\n"
    text += "\n<b>Самые крутые</b>\n"
    level3_list = db.get_admin_list(3)
    for num, data in enumerate(level3_list):
        tg_id, username, full_name, event_id = data
        text += f"{num + 1}. @{username} {full_name}\n"
    return text
