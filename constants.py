from enum import Enum

import pytz
MAX_FULLNAME_LEN = 300
TZ = pytz.timezone("Europe/Moscow")
DATETIME_FORMAT = "%d.%m.%Y %H.%M"
class TransactionTypes(Enum):
    USER_REGISTER = "user_register"
    SUPPORT_REQUEST = "support_request" # Запрос в тех. поддержку
    PROMO_USAGE = "promo_usage"
    SET_TUC = "set_tuc" # Установка tuc
    CODE_GENERATE = "code_generate"
