# Тексты кнопок
import collections

from database.db_funcs import DataBase
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

def get_profile_text(db: DataBase, tg_id):
    info = db.get_user_info(tg_id, "fullname, money, tuc")
    if not info:
        return PROFILE_ERROR
    fullname, money, tuc = info
    booked_list = db.booked_list(tg_id)
    text = PROFILE_TEMPLATE.format(fullname, money, TUC_TEXTS[tuc])
    if not booked_list:
        return text
    text += "\n\n<b>Твой мерч</b>\n"
    for stuff_id, stuff_sizes_colors_id, name, color, size, count in booked_list:
        text += f"{name}"
        if color:
            text += f" {color}"
        if size:
            text += f" {size}"
        text += f" - {count} шт.\n"
    return text


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
PROMO_SUCCESSFULLY_ACTIVATED_TEMPLATE = "Промокод на {}i активирован! Возвращаю тебя в меню 😎"
PROMO_ALREADY_USED = "Ты уже вводил этот промокод, возвращаю тебя в меню"
PROMO_DOESNT_EXISTS = "Промокод недействителен 😕 Попробуй ещё раз!"

STORE_TEMP_TEXT = "Я ещё не открыл двери своего магазинчика 😉"


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
