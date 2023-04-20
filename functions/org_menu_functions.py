import random
import string
import datetime as dt
import constants

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
