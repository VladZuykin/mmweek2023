from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from callbacks import org_merch_issuance_callbacks

from database.org_db_funcs import OrgDataBase

CODE_INPUT_TEXT = "Пожалуйста, введите код участника"
CODE_INPUT_FAIL = "К сожалению, участника с таким кодом не найдено. Повторите ввод"
PARTICIPANT_TEMPLATE = """
Участник:
<u>{}</u>

Забронированный мерч:
{}"""

MERCH_ISSUE_COUNT_TO_ADD_TEMPLATE = """
Вы хотите выдать
<b>{}</b>
<u>{}</u>
<b><u>{} шт.</u></b>


Осталось выдать {} шт. до полного счастья пользователя.
"""

MERCH_ISSUE_COUNT_TO_RETURN_BACK_TEMPLATE = """
Вы хотите вернуть от
<b>{}</b>
<u>{}</u>
<b><u>{} шт.</u></b>
"""

MERCH_ISSUE_UNAVAILABLE_TEMPLATE = """
К сожалению, выдать мерч не удалось. Возможно, количество позиций изменилось.
Участнику <b>{}</b> было бы всего выдано <u>{}/{} шт.</u> позиций <u>{}</u>
Попробуйте обновить меню"""

MERCH_RETURN_BACK_UNAVAILABLE_TEMPLATE = """
К сожалению, вернуть мерч не удалось. Возможно, количество позиций изменилось.
У участника <b>{}</b> после операции было бы <u>{}/{} шт.</u> позиций <u>{}</u>
Попробуйте обновить меню"""

MERCH_RETURN_BACK_BELOW_ZERO_TEXT = "Не знаю, как, но выбрано отрицательное количество."

MERCH_GIVEN_TEMPLATE = "Выдача сохранена: участнику <b>{}</b> выдано <u>{} шт.</u> позиций <u>{}</u>"

INSIDE_MERCH_RETURN_BACK_CONFIRMATION_TEMPLATE = """
Подтверди, что участнику <b>{}</b> отменится <u>{} единиц</u> товара <u>{}</u> стоимостью по <u>{}i</u> каждый и будет возвращено <u>{}i</u>.
Тебе останется выдать ему в будущем <u>{} позиций</u> этого мерча, так как у него <u>{}/{}</u> на руках.\nОн тебе сейчас не должен отдавать мерч."""

OUTSIDE_MERCH_RETURN_BACK_CONFIRMATION_TEMPLATE = """
Подтверди, что участнику <b>{}</b> отменится <u>{}</u> единиц товара <u>{}</u> стоимостью по <u>{}i</u> каждый и будет возвращено <u>{}i</u>.
Ему уже было выдано <u>{}/{}</u> единиц <u>{}</u>, тебе оставалось выдать ему <u>{}</u> единиц, а ты пытаешься отменить <u>{}</u> единиц, """ \
                                                  "поэтому у него нужно забрать <u>{}</u> единиц <u>{}</u> и " \
                                                  "ему вернётся <u>{}i</u> за всё отменённое."

MERCH_BUY_CANCELLATION_TEXT = "Выбери, какую позицию отменить"
MERCH_BUY_CANCELLATION_COUNT_TEXT = "Выбери, сколько нужно отменить"
MERCH_CANCELLATION_UNAVAILABLE_TEXT = "Не удалось сделать отмену мерча. " \
                                      "Возможно количество забронированных позиций изменилось, " \
                                      "пока ты выбирал количество. Попробуй выдать ещё раз"

MERCH_CANCELLATION_CONFIRM_TEMPLATE = """
Подтверди, что участнику {} отменится {} единиц {} и будет возвращено {} мнимых единиц.
У него останется забронировано {} позиций этого мерча"""

MERCH_PARTIALLY_CANCELLED_YET_TEMPLATE = "Участнику уже было выдано {} единиц, забронировано сейчас {}, " \
                                         "а ты пытаешься отменить {}, поэтому перед отменой участник должен " \
                                         "вернуть {} единиц"

MERCH_CANCELLATION_CONFIRMED_TEMPLATE = "Участнику {} отменено <u>{}</u> единиц мерча <u>{}</u> и возвращено <u>{}i</u>."


def profile_text_markup_get(db: OrgDataBase, tg_id, cancellation=False):
    fullname, = db.get_user_info(tg_id, "fullname")
    data = db.get_purchases_by_id(tg_id, "id, stuff_id, stuff_sizes_colors_id, issued, count")
    list_text = ""
    markup = InlineKeyboardMarkup()
    for i, params in enumerate(data):
        purchase_id, stuff_id, stuff_sizes_colors_id, issued, count = params
        name, = db.get_stuff_info(stuff_id, "name")
        size_color = db.get_stuff_sizes_colors(stuff_sizes_colors_id, "size, color")
        list_text += f"{i + 1}. "
        merch_fullname = name
        if size_color:
            size, color = size_color
            if size:
                merch_fullname += f" {size} "
            if color:
                merch_fullname += f" {color} "
        indent = " " * (len(str(i)) + 3)
        list_text += f"{merch_fullname}\n{indent}Выдано {issued}/{count}\n"
        if not cancellation and issued != count:
            markup.add(InlineKeyboardButton(merch_fullname,
                                            callback_data=org_merch_issuance_callbacks.MERCH_ISSUANCE_CB.new(
                                                purchases_id=purchase_id
                                            )))
        elif cancellation:
            markup.add(InlineKeyboardButton(merch_fullname,
                                            callback_data=org_merch_issuance_callbacks.MERCH_RETURN_BACK_CB.new(
                                                purchases_id=purchase_id
                                            )))
    if not cancellation:
        markup.add(InlineKeyboardButton("Сделать возврат мерча",
                                        callback_data=org_merch_issuance_callbacks.MERCH_RETURN_BACK_CHOOSE_CB))
    else:
        markup.add(InlineKeyboardButton("Назад",
                                        callback_data=org_merch_issuance_callbacks.CANCEL_TEXT_CB))
    if not cancellation:
        res_text = "<b><u>Выдача мерча</u></b>\n"
    else:
        res_text = "<b><u>Возврат мерча</u></b>\n"
    res_text += PARTICIPANT_TEMPLATE.format(fullname, list_text)
    return res_text, markup


def merch_issue_count_text(db: OrgDataBase, purchases_id, k):
    tg_id, fullname, stuff_name, sizes_colors_id, count, issued = db.execute(
        "SELECT users.tg_id, "
        "users.fullname, "
        "stuff.name, "
        "purchases.stuff_sizes_colors_id, "
        "purchases.count, "
        "purchases.issued "
        "FROM purchases "
        "JOIN users ON purchases.tg_id = users.tg_id "
        "JOIN stuff ON purchases.stuff_id = stuff.id "
        "WHERE purchases.id = ?", purchases_id, fetch="one")

    size_color = db.get_stuff_sizes_colors_texts_info(sizes_colors_id, "size, color")

    merch_fullname = stuff_name
    if size_color:
        size, color = size_color
        if size:
            merch_fullname += f" {size} "
        if color:
            merch_fullname += f" {color} "

    return MERCH_ISSUE_COUNT_TO_ADD_TEMPLATE.format(fullname, merch_fullname, k, count - issued - k)


def merch_return_back_count_text(db: OrgDataBase, purchases_id, k):
    tg_id, fullname, stuff_name, sizes_colors_id, count, issued = db.execute(
        "SELECT users.tg_id, "
        "users.fullname, "
        "stuff.name, "
        "purchases.stuff_sizes_colors_id, "
        "purchases.count, "
        "purchases.issued "
        "FROM purchases "
        "JOIN users ON purchases.tg_id = users.tg_id "
        "JOIN stuff ON purchases.stuff_id = stuff.id "
        "WHERE purchases.id = ?", purchases_id, fetch="one")

    size_color = db.get_stuff_sizes_colors_texts_info(sizes_colors_id, "size, color")

    merch_fullname = stuff_name
    if size_color:
        size, color = size_color
        if size:
            merch_fullname += f" {size} "
        if color:
            merch_fullname += f" {color} "

    return MERCH_ISSUE_COUNT_TO_RETURN_BACK_TEMPLATE.format(fullname, merch_fullname, k)
