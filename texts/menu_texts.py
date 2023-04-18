# Тексты кнопок
import collections

from functions import menu_functions
import datetime as dt

MENU_GET_CODE_BUTTON_TEXT = "Мой код"
MENU_PROFILE_BUTTON_TEXT = "ЛК"
MENU_SCHEDULE_BUTTON_TEXT = "Расписание"
MENU_STORE_BUTTON_TEXT = "Магазин"
MENU_PROMO_BUTTON_TEXT = "Ввести промокод"
MENU_HELP_BUTTON_TEXT = "Помощь по боту и неделе"

# Тексты сообщений
MENU_TEXT = "Добро пожаловать в моё меню, нажимайте на кнопочки снизу. 😎"

GENERATE_CODE_TEMPLATE = "Ваш код 🔢\n\n<b>{}</b>"
PROFILE_TEMPLATE = "{} 👤\n\nБаланс: {}i\n\nМногочленство в профкоме: {}"
PROFILE_ERROR = "Извините, произошла ошибка. Вас нет в базе данных."

TUC_TEXTS = {
    0: "не в профкоме",
    1: "в профкоме",
    2: "на проверке"
}

SCHEDULE_TEMPLATE = """<b>Расписание</b>\n\n{}"""
NO_SCHEDULE_TEXT = "К сожалению, расписание пусто."

EVENT_NOT_FOUND_TEXT = "К сожалению, информация об это мероприятии недоступна."
MESSAGE_CANT_BE_EDITED_TEXT = "Сообщение не редактируется :("


def get_schedule_text(events_summary):  # events_summary - список [(id, name, datetime), (...), ..., (...)]
    if not events_summary:
        return NO_SCHEDULE_TEXT
    # Сортировка по дням
    schedule_dict = {}
    for event in events_summary:
        date = event[2].date()
        if date not in schedule_dict:
            schedule_dict[date] = [event]
        else:
            schedule_dict[date].append(event)

    sorted_schedule_dict = collections.OrderedDict(sorted(schedule_dict.items()))
    text = ""
    for key in sorted_schedule_dict:
        text += f"<b>{menu_functions.get_weekday_str(key).capitalize()}</b>\n"
        # Сортировка по часам
        events = sorted_schedule_dict[key]
        events.sort(key=lambda x: x[2])
        for event in events:
            time = dt.datetime.strftime(event[2], "%H:%M")
            name = event[1]
            text += f"{time} {name}\n"
        text += "\n"
    return SCHEDULE_TEMPLATE.format(text)


def get_event_text(event: dict):
    if not event:
        return EVENT_NOT_FOUND_TEXT
    week_str = menu_functions.get_weekday_str(event["datetime"])
    time_str = dt.datetime.strftime(event["datetime"], "%H:%M")
    name = event["name"]
    description = event["description"]
    res = f"""<b>{name}</b>
    
📅
{week_str.capitalize()} в {time_str}

ℹ️
{description}"""
    return res
