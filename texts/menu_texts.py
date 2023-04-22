# Тексты кнопок
import collections

from functions import menu_functions
import datetime as dt

MENU_GET_CODE_BUTTON_TEXT = "Мой код"
MENU_PROFILE_BUTTON_TEXT = "Личный кабинет"
MENU_SCHEDULE_BUTTON_TEXT = "Расписание"
MENU_STORE_BUTTON_TEXT = "Магазин"
MENU_PROMO_BUTTON_TEXT = "Ввести промокод"
MENU_HELP_BUTTON_TEXT = "Справка | Поддержка"

TOO_FREQUENTLY_TEMPLATE = "Ты слишком общительный! Подожди {} и сможешь написать снова. А пока что возвращаю тебя в меню 😉"

HELP_BUTTON_TEXT = "Поддержка"
BACK_BUTTON_TEXT = "Назад"
CANCEL_TEXT = "Отмена"

# Тексты сообщений
RESPOND_TEXT = "Снизу есть кнопки меню, можешь их использовать."
MENU_TEXT = "Добро пожаловать в моё меню! Нажимай на кнопочки снизу 😎"

GENERATE_CODE_TEMPLATE = "Твой код 🔢\n\n<b>{}</b>"
PROFILE_TEMPLATE = "{} 👤\n\nБаланс: {}i\n\nМногочленство в Профкоме: {}"
PROFILE_ERROR = "Произошла ошибка - тебя нет в базе данных"

TUC_TEXTS = {
    0: "не в Профкоме",
    1: "в Профкоме",
    2: "на проверке"
}

NO_SCHEDULE_TEXT = "Расписание пусто"

EVENT_NOT_FOUND_TEXT = "Информация об этом мероприятии недоступна"
MESSAGE_CANT_BE_EDITED_TEXT = "Сообщение не редактируется :("

HELP_INPUT_REQUEST = "Введи свой вопрос"
HELP_MESSAGE_SENT = "Запрос отправлен, возвращаю тебя в меню"
BACK_TO_MENU_TEXT = "Хорошо, возвращаю тебя в меню"
TO_SUPPORT_MESSAGE_TEMPLATE = "Пользователь @{}\n" \
                              "Ссылка на него\n{}\n" \
                              "Он написал:\n{}"

PROMO_INPUT_REQUEST = "Если у тебя есть промокод от организаторов, введи его сюда"
PROMO_SUCCESSFULLY_ACTIVATED_TEXT = "Промокод активирован! Возвращаю тебя в меню 😎"
PROMO_ALREADY_USED = "Ты уже вводил этот промокод, возвращаю тебя в меню"
PROMO_DOESNT_EXISTS = "Промокод недействителен 😕 Попробуй ещё раз!"

STORE_TEMP_TEXT = "Я ещё не открыл двери своего магазинчика 😉"

HELP_TEXT = """Справка по боту

Привет! Я виртуальный помощник по Неделе Матмеха. Со мной ты сможешь копить мнимые единицы и превращать их в вещественный мерч, смотреть расписание и узнавать подробности о мероприятиях Недели.

Чтобы начислить мнимые единицы за участие, покажи свой код организатору во время мероприятия. Код можно посмотреть в разделе "Мой код" в основном меню.

Во время мероприятий организаторы могут выдавать промокоды на дополнительные мнимые единицы. Если ты получил(а) промокод, введи его в разделе "Ввести промокод" в основном меню.

Когда у тебя наберётся достаточно мнимых единиц, ты сможешь забронировать мерч в разделе "Магазин" в основном меню. Количество мерча ограничено, для членов Профкома действуют скидки. Забрать мерч можно будет в конце Недели.

За организацию Недели и разработку меня спасибо: Профкому, Студсовету, СПО Унисон и Сказка.

"""

SCHEDULE_TEXT = """"🎈 Понедельник
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


# def get_schedule_text(events_summary):  # events_summary - список [(id, name, datetime), (...), ..., (...)]
#     if not events_summary:
#         return NO_SCHEDULE_TEXT
#     # Сортировка по дням
#     schedule_dict = {}
#     for event in events_summary:
#         date = event[2].date()
#         if date not in schedule_dict:
#             schedule_dict[date] = [event]
#         else:
#             schedule_dict[date].append(event)
#
#     sorted_schedule_dict = collections.OrderedDict(sorted(schedule_dict.items()))
#     text = ""
#     for key in sorted_schedule_dict:
#         text += f"<b>{menu_functions.get_weekday_str(key).capitalize()}</b>\n"
#         # Сортировка по часам
#         events = sorted_schedule_dict[key]
#         events.sort(key=lambda x: x[2])
#         for event in events:
#             time = dt.datetime.strftime(event[2], "%H:%M")
#             name = event[1]
#             text += f"{time} {name}\n"
#         text += "\n"
#     return SCHEDULE_TEMPLATE.format(text)

def get_event_text(event: dict):
    if not event:
        return EVENT_NOT_FOUND_TEXT
    return event["description"]


# def get_event_text(event: dict):
#     if not event:
#         return EVENT_NOT_FOUND_TEXT
#     week_str = menu_functions.get_weekday_str(event["datetime"])
#     time_str = dt.datetime.strftime(event["datetime"], "%H:%M")
#     name = event["name"]
#     description = event["description"]
#     res = f"""<b>{name}</b>
#
# 📅
# {week_str.capitalize()} в {time_str}
#
# ℹ️
# {description}"""
#     return res
