import random, string
import datetime as dt
import constants

from texts import org_promo_texts


def get_generate_promo_code(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for i in range(length))


def get_string_datetime(datetime: dt.datetime):
    return str(datetime.day) + "." + str(datetime.month) + "." + str(datetime.year) \
            + " " + str(datetime.hour) + "." + str(datetime.minute)


def get_promo_added_text(can_use, period_time, period_type):
    if can_use == -1:
        can_use = org_promo_texts.INFINITE_USES_TEXT
    return org_promo_texts.PROMO_ADDED_INFO_TEMPLATE.format(str(period_time) + " " + period_type + ".",
                                                            str(can_use))  # TODO более красивый срок действия


def get_promo_to_list_text(can_use, dt_ends: dt.datetime, num_uses=0):
    if can_use == -1:
        can_use = org_promo_texts.INFINITE_USES_TEXT
    return org_promo_texts.PROMO_TO_LIST_INFO_TEMPLATE.format(str(dt_ends.day) + "."
                                                              + str(dt_ends.month) + "."
                                                              + str(dt_ends.year) + " "
                                                              + str(dt_ends.hour) + ":"
                                                              + str(dt_ends.minute),
                                                              str(num_uses) + "/"
                                                              + str(can_use))


if __name__ == '__main__':
    get_generate_promo_code(6)
