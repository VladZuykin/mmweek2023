from enum import Enum
import datetime as dt
from middleware.functions import dt_to_dtdict, dtdict_to_str, ACCUSATIVE_TIME_UNITS_FORMS

import pytz

MAX_FULLNAME_LEN = 300
TZ = pytz.timezone("Europe/Moscow")
DATETIME_FORMAT = "%d.%m.%Y %H.%M"
LOG_DATETIME_FORMAT = "%d.%m.%Y %H.%M.%S"
SUPPORT_TIMEDELTA = dt.timedelta(minutes=120)
SUPPORT_TIMEDELTA_ACCUSATIVE_STR = dtdict_to_str(dt_to_dtdict(SUPPORT_TIMEDELTA), ACCUSATIVE_TIME_UNITS_FORMS)
PREVIOUS_REGISTERED_BOT_REWARD = 150
LETTERING_PERIOD = 0.5

STORE_PATH = "misc/store/"

PERIOD_TYPES = ['ч', 'д']

LETTERING_ADMIN_ID = 702447805


class TransactionTypes(Enum):
    USER_REGISTER = "user_register"
    SUPPORT_REQUEST = "support_request"  # Запрос в тех. поддержку
    PROMO_USAGE = "promo_usage"
    PROMO_CREATE = "create_promo"
    SET_TUC = "set_tuc"  # Установка tuc
    CODE_GENERATE = "code_generate"
    MONEY_GET = "money_get"
    ADMIN_GAVE = "admin_gave"
    ENTER = "enter"
    PURCHASE_SUCCESS = "purchase_success"
    PURCHASE_FAIL = "purchase_fail"
    ADMIN_TAKE_OUT = "admin_take_out"
    ISSUE_MERCH = "merch_issue"
    MERCH_RETURN_BACK = "merch_return_back"
    ISSUE_MERCH_FAIL = "issue_merch_fail"
    MERCH_RETURN_BACK_FAIL = "merch_return_back_fail"


HELP_TEXT = """<b>Справка по боту</b>

Привет! Я виртуальный помощник по Неделе Матмеха. Со мной ты сможешь копить мнимые единицы и превращать их в вещественный мерч, смотреть расписание и узнавать подробности о мероприятиях Недели.

Чтобы начислить мнимые единицы за участие, покажи свой код организатору во время мероприятия. Код можно посмотреть в разделе "Мой код" в основном меню.

Во время мероприятий организаторы могут выдавать промокоды на дополнительные мнимые единицы. Если ты получил(а) промокод, введи его в разделе "Ввести промокод" в основном меню.

Когда у тебя наберётся достаточно мнимых единиц, ты сможешь забронировать мерч в разделе "Магазин" в основном меню. Количество мерча ограничено, для членов Профкома действуют скидки. Забрать мерч можно будет в конце Недели.

За организацию Недели и разработку меня спасибо: Профкому, Студсовету, СПО Унисон и Сказка.

"""

SCHEDULE_TEXT = """"🎈 <b>Понедельник</b>
13:00 – Открытие Недели. Матмех, главный вход
18:00 – ЧГК 1 тур. Матмех, читальный зал

🎷 Вторник
19:00 – Литературно-музыкальный вечер. Концерт. ПМ-ПУ, конференц-зал

💸 Среда
Ярмарка проектов (Тинькофф, Яндекс, P&G…)
12:00 – Стенды. Матмех, аквариум 16:30 – Лекции. Матмех, ауд. 01

👨‍🦳 Четверг
17:00 – Лекции выпускников.Матмех, ауд. 405

♟️ Пятница
18:00 – Шахматный турнир. Матмех, ауд. 2389
18:00 – ЧГК Финал. Матмех, ауд. 2510
18:00 – Баскетбол. Матмех, спортзал

🎊 Суббота
Campus Fest, ПУНК СПбГУ

🪩 Воскресенье
18:00 – Дискотека. Наб. Обводного канала, 136"""
