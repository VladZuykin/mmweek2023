from enum import Enum
import datetime as dt
from middleware.functions import dt_to_dtdict, dtdict_to_str, ACCUSATIVE_TIME_UNITS_FORMS

import pytz
MAX_FULLNAME_LEN = 300
TZ = pytz.timezone("Europe/Moscow")
DATETIME_FORMAT = "%d.%m.%Y %H.%M"
LOG_DATETIME_FORMAT = "%d.%m.%Y %H.%M.%S"
SUPPORT_TIMEDELTA = dt.timedelta(minutes=120)
SUPPORT_TIMEDELTA_ACCUSATIVE_STR =  dtdict_to_str(dt_to_dtdict(SUPPORT_TIMEDELTA), ACCUSATIVE_TIME_UNITS_FORMS)


class TransactionTypes(Enum):
    USER_REGISTER = "user_register"
    SUPPORT_REQUEST = "support_request" # Запрос в тех. поддержку
    PROMO_USAGE = "promo_usage"
    SET_TUC = "set_tuc" # Установка tuc
    CODE_GENERATE = "code_generate"
