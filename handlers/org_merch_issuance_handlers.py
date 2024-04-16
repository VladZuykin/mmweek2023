from typing import Union

from aiogram.dispatcher import FSMContext
from aiogram.types import ParseMode, ReplyKeyboardRemove, Message, CallbackQuery, ChatActions, ReplyKeyboardMarkup, \
    InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from callbacks.org_merch_issuance_callbacks import MERCH_ISSUANCE_CB, MERCH_RETURN_BACK_CONFIRM_CB, CANCEL_TEXT_CB
from fsm.org_merch_issuance_fsm import MerchIssuanceState
from handlers import org_menu_handlers
from markups import org_merch_issuance_markups, menu_markups
from org_bot_create import bot, dp, config, db
from callbacks import org_merch_issuance_callbacks
from middleware import admins
from texts import org_menu_texts, org_merch_issuance_texts
from functions import org_merch_issuance_functions
from texts.org_merch_issuance_texts import MERCH_RETURN_BACK_UNAVAILABLE_TEMPLATE, MERCH_RETURN_BACK_BELOW_ZERO_TEXT, \
    MERCH_CANCELLATION_CONFIRMED_TEMPLATE


@admins.check(2)
async def merch_issuance_code_input(update: Union[Message, CallbackQuery], state: FSMContext):
    if isinstance(update, Message):
        message = update
    else:
        message = update.message
    await message.answer(org_merch_issuance_texts.CODE_INPUT_TEXT,
                         reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("Отмена")))
    await MerchIssuanceState.code_input.set()


@admins.check(2)
async def merch_issuance_choice(update: Union[Message, CallbackQuery], state: FSMContext, edit=True):
    is_callback = isinstance(update, CallbackQuery)
    if is_callback:
        data = await state.get_data()
        tg_id = data["org_merch_user_tg_id"]
    else:
        user_info = db.get_user_info_by_code(update.text, "tg_id")

        if not user_info:
            await update.answer(org_merch_issuance_texts.CODE_INPUT_FAIL)
            await MerchIssuanceState.code_input.set()
            return
        tg_id = user_info[0]
    text, markup = org_merch_issuance_texts.profile_text_markup_get(db, tg_id)
    if not is_callback:
        await state.update_data(org_merch_user_tg_id=tg_id)
        await update.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    else:
        if edit:
            await update.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
        else:
            await update.message.answer(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await MerchIssuanceState.issuance_merch_choice.set()


@admins.check(2)
async def merch_cancellation_choice(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tg_id = data["org_merch_user_tg_id"]
    text, markup = org_merch_issuance_texts.profile_text_markup_get(db, tg_id, cancellation=True)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await MerchIssuanceState.cancellation_merch_choice.set()


@admins.check(2)
async def merch_cancellation_choice_num(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    purchases_id = callback_data["purchases_id"]
    await state.update_data(purchases_id=purchases_id, merch_to_return_back=0)
    await callback.message.edit_text(org_merch_issuance_texts.merch_return_back_count_text(db,
                                                                                           purchases_id,
                                                                                           0),
                                     reply_markup=org_merch_issuance_markups.get_merch_return_back_markup(db,
                                                                                                          purchases_id,
                                                                                                          0),
                                     parse_mode=ParseMode.HTML)
    await MerchIssuanceState.cancellation_merch_number_choice.set()


@admins.check(2)
async def merch_issuance_choice_num(callback: CallbackQuery, state: FSMContext, callback_data: dict):
    purchases_id = callback_data["purchases_id"]
    await state.update_data(purchases_id=purchases_id, merch_to_issue=0)
    await callback.message.edit_text(org_merch_issuance_texts.merch_issue_count_text(db, purchases_id, 0),
                                     reply_markup=org_merch_issuance_markups.get_merch_issuance_markup(db, purchases_id,
                                                                                                       0),
                                     parse_mode=ParseMode.HTML)
    await MerchIssuanceState.issuance_merch_number_choice.set()


@admins.check(2)
async def merch_cancellation_change(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    purchases_id = data["purchases_id"]
    merch_to_return_back = data["merch_to_return_back"]
    count, issued = db.execute("SELECT count, issued FROM purchases WHERE id = ?", purchases_id, fetch="one")
    changed = False
    if callback.data == org_merch_issuance_callbacks.MERCH_RETURN_BACK_MORE_CB:
        if merch_to_return_back < count:
            changed = True
            merch_to_return_back += 1
    elif callback.data == org_merch_issuance_callbacks.MERCH_RETURN_BACK_LESS_CB:
        if merch_to_return_back > 0:
            changed = True
            merch_to_return_back -= 1
    if changed:
        await state.update_data(purchases_id=purchases_id, merch_to_return_back=merch_to_return_back)
        await callback.message.edit_text(
            org_merch_issuance_texts.merch_return_back_count_text(db, purchases_id, merch_to_return_back),
            reply_markup=org_merch_issuance_markups.get_merch_return_back_markup(db,
                                                                                 purchases_id,
                                                                                 merch_to_return_back),
            parse_mode=ParseMode.HTML)
    else:
        await callback.answer("Куда полегче полегче")


@admins.check(2)
async def merch_issuance_change(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    purchases_id = data["purchases_id"]
    merch_to_issue = data["merch_to_issue"]
    count, issued = db.execute("SELECT count, issued FROM purchases WHERE id = ?", purchases_id, fetch="one")
    changed = False
    if callback.data == org_merch_issuance_callbacks.MERCH_ISSUANCE_MORE_CB:
        if merch_to_issue + issued < count:
            changed = True
            merch_to_issue += 1
    elif callback.data == org_merch_issuance_callbacks.MERCH_ISSUANCE_LESS_CB:
        if merch_to_issue > 0:
            changed = True
            merch_to_issue -= 1
    if changed:
        await state.update_data(purchases_id=purchases_id, merch_to_issue=merch_to_issue)
        await callback.message.edit_text(
            org_merch_issuance_texts.merch_issue_count_text(db, purchases_id, merch_to_issue),
            reply_markup=org_merch_issuance_markups.get_merch_issuance_markup(db,
                                                                              purchases_id,
                                                                              merch_to_issue),
            parse_mode=ParseMode.HTML)
    else:
        await callback.answer("Куда полегче полегче")


@admins.check(2)
async def merch_issuance_number_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    purchases_id = data["purchases_id"]
    merch_to_issue = data["merch_to_issue"]
    user_fullname, count, issued = db.execute("SELECT users.fullname, purchases.count, purchases.issued "
                                              "FROM purchases "
                                              "JOIN users ON purchases.tg_id = users.tg_id "
                                              "WHERE id = ?", purchases_id, fetch="one")
    merch_fullname = org_merch_issuance_functions.get_purchase_merch_fullname(db, purchases_id)
    if issued + merch_to_issue > count:
        await callback.message.edit_text(org_merch_issuance_texts.MERCH_ISSUE_UNAVAILABLE_TEMPLATE.format(
            user_fullname,
            issued + merch_to_issue,
            count,
            merch_fullname
        ),
            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Окей", callback_data=CANCEL_TEXT_CB)),
            parse_mode=ParseMode.HTML)
        await MerchIssuanceState.issuance_bad.set()
        return
    elif merch_to_issue < 0:
        await callback.message.edit_text(org_merch_issuance_texts.MERCH_RETURN_BACK_BELOW_ZERO_TEXT,
                                         reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Окей",
                                                                                                      callback_data=CANCEL_TEXT_CB)))
        await MerchIssuanceState.issuance_bad.set()
        return
    code = db.issue_merch(purchases_id, merch_to_issue, callback.from_user.id)
    # code = 0
    if code == 0:
        await callback.message.edit_text(org_merch_issuance_texts.MERCH_GIVEN_TEMPLATE.format(user_fullname,
                                                                                              merch_to_issue,
                                                                                              merch_fullname),
                                         parse_mode=ParseMode.HTML)
    else:
        await callback.message.edit_text(org_merch_issuance_texts.MERCH_ISSUE_UNAVAILABLE_TEMPLATE.format(
            user_fullname,
            issued + merch_to_issue,
            count,
            merch_fullname
        ))
    await merch_issuance_choice(callback, state, edit=False)


@admins.check(2)
async def merch_return_back_number_confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    purchases_id = data["purchases_id"]
    merch_to_return_back = data["merch_to_return_back"]
    user_fullname, count, issued, tuc_price, not_tuc_price, tuc_status = db.execute(
        "SELECT users.fullname, purchases.count, purchases.issued, "
        "stuff.tuc_price, stuff.not_tuc_price, users.tuc "
        "FROM purchases "
        "JOIN users ON purchases.tg_id = users.tg_id "
        "JOIN stuff ON purchases.stuff_id = stuff.id "
        "WHERE purchases.id = ?", purchases_id, fetch="one")
    merch_fullname = org_merch_issuance_functions.get_purchase_merch_fullname(db, purchases_id)
    if tuc_status:
        price = tuc_price
    else:
        price = not_tuc_price
    if merch_to_return_back > count:
        await callback.message.edit_text(org_merch_issuance_texts.MERCH_RETURN_BACK_UNAVAILABLE_TEMPLATE.format(
            user_fullname,
            count - merch_to_return_back,
            count,
            merch_fullname
        ),
            parse_mode=ParseMode.HTML)
        await MerchIssuanceState.cancellation_bad.set()
        return
    if merch_to_return_back < 0:
        await callback.message.edit_text(org_merch_issuance_texts.MERCH_RETURN_BACK_BELOW_ZERO_TEXT)
        await MerchIssuanceState.cancellation_bad.set()
        return
    if merch_to_return_back <= count - issued:
        text = org_merch_issuance_texts.INSIDE_MERCH_RETURN_BACK_CONFIRMATION_TEMPLATE.format(
            user_fullname,
            merch_to_return_back,
            merch_fullname,
            price,
            price * merch_to_return_back,
            count - issued - merch_to_return_back,
            issued,
            count
        )
    else:
        text = org_merch_issuance_texts.OUTSIDE_MERCH_RETURN_BACK_CONFIRMATION_TEMPLATE.format(
            user_fullname,
            merch_to_return_back,
            merch_fullname,
            price,
            price * merch_to_return_back,
            issued,
            count,
            merch_fullname,
            count - issued,
            merch_to_return_back,
            merch_to_return_back - (count - issued),
            merch_fullname,
            price * merch_to_return_back
        )

    await callback.message.edit_text(text,
                                     reply_markup=InlineKeyboardMarkup().add(
                                         InlineKeyboardButton("Подтвердить выполнение",
                                                              callback_data=MERCH_RETURN_BACK_CONFIRM_CB),
                                         InlineKeyboardButton("Отмена", callback_data=CANCEL_TEXT_CB)),
                                     parse_mode=ParseMode.HTML)
    await MerchIssuanceState.cancellation_merch_number_confirmation.set()


@admins.check(2)
async def merch_return_back_number_process(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    purchases_id = data["purchases_id"]
    merch_to_return_back = data["merch_to_return_back"]
    user_fullname, count, issued, tuc_price, not_tuc_price, tuc_status = db.execute(
        "SELECT users.fullname, purchases.count, purchases.issued, "
        "stuff.tuc_price, stuff.not_tuc_price, users.tuc "
        "FROM purchases "
        "JOIN users ON purchases.tg_id = users.tg_id "
        "JOIN stuff ON purchases.stuff_id = stuff.id "
        "WHERE purchases.id = ?", purchases_id, fetch="one")
    merch_fullname = org_merch_issuance_functions.get_purchase_merch_fullname(db, purchases_id)
    if tuc_status:
        price = tuc_price
    else:
        price = not_tuc_price
    if merch_to_return_back > count:
        await callback.message.edit_text(MERCH_RETURN_BACK_UNAVAILABLE_TEMPLATE.format(
            user_fullname,
            count - merch_to_return_back,
            count,
            merch_fullname,
        ),
            reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton("Окей", callback_data=CANCEL_TEXT_CB)),
            parse_mode=ParseMode.HTML)
        await MerchIssuanceState.cancellation_bad.set()
        return
    if merch_to_return_back < 0:
        await callback.message.edit_text(MERCH_RETURN_BACK_BELOW_ZERO_TEXT,
                                         reply_markup=InlineKeyboardMarkup().add(
                                             InlineKeyboardButton("Окей", callback_data=CANCEL_TEXT_CB)))
        await MerchIssuanceState.cancellation_bad.set()
        return
    text = callback.message.text
    await callback.message.edit_text(text + "\n\n" + MERCH_CANCELLATION_CONFIRMED_TEMPLATE.format(
        user_fullname,
        merch_to_return_back,
        merch_fullname,
        merch_to_return_back * price
    ), parse_mode=ParseMode.HTML)
    db.return_back_merch(purchases_id, merch_to_return_back, callback.from_user.id)
    await merch_issuance_choice(callback, state, edit=False)


@admins.check(2)
async def merch_issuance_choice_return(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    tg_id = data["org_merch_user_tg_id"]
    text, markup = org_merch_issuance_texts.profile_text_markup_get(db, tg_id)
    await callback.message.edit_text(text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await MerchIssuanceState.issuance_merch_choice.set()


def register_merch_issuance_handlers():
    dp.register_message_handler(org_menu_handlers.send_menu_on_update,
                                text="Отмена",
                                state="*")
    dp.register_message_handler(merch_issuance_code_input,
                                text=org_menu_texts.MENU_MERCH_BUTTON_TEXT,
                                state="*")
    dp.register_message_handler(merch_issuance_choice,
                                state=MerchIssuanceState.code_input)
    dp.register_callback_query_handler(merch_issuance_choice_num,
                                       MERCH_ISSUANCE_CB.filter(),
                                       state=MerchIssuanceState.issuance_merch_choice)
    dp.register_callback_query_handler(merch_issuance_change,
                                       text=org_merch_issuance_callbacks.MERCH_ISSUANCE_LESS_CB,
                                       state=MerchIssuanceState.issuance_merch_number_choice)
    dp.register_callback_query_handler(merch_issuance_change,
                                       text=org_merch_issuance_callbacks.MERCH_ISSUANCE_MORE_CB,
                                       state=MerchIssuanceState.issuance_merch_number_choice)
    dp.register_callback_query_handler(merch_issuance_number_confirm,
                                       text=org_merch_issuance_callbacks.MERCH_ISSUANCE_CONFIRM_CB,
                                       state=MerchIssuanceState.issuance_merch_number_choice)
    dp.register_callback_query_handler(merch_issuance_choice_return,
                                       text=org_merch_issuance_callbacks.CANCEL_TEXT_CB,
                                       state=MerchIssuanceState.issuance_merch_number_choice)
    dp.register_callback_query_handler(merch_cancellation_choice,
                                       text=org_merch_issuance_callbacks.MERCH_RETURN_BACK_CHOOSE_CB,
                                       state=MerchIssuanceState.issuance_merch_choice)
    dp.register_callback_query_handler(merch_cancellation_choice_num,
                                       org_merch_issuance_callbacks.MERCH_RETURN_BACK_CB.filter(),
                                       state=MerchIssuanceState.cancellation_merch_choice)
    dp.register_callback_query_handler(merch_issuance_choice,
                                       text=org_merch_issuance_callbacks.CANCEL_TEXT_CB,
                                       state=MerchIssuanceState.cancellation_merch_choice)
    dp.register_callback_query_handler(merch_issuance_choice,
                                       text=org_merch_issuance_callbacks.CANCEL_TEXT_CB,
                                       state=MerchIssuanceState.issuance_bad)
    dp.register_callback_query_handler(merch_cancellation_choice,
                                       text=org_merch_issuance_callbacks.CANCEL_TEXT_CB,
                                       state=MerchIssuanceState.cancellation_merch_number_choice)
    dp.register_callback_query_handler(merch_cancellation_choice,
                                       text=org_merch_issuance_callbacks.CANCEL_TEXT_CB,
                                       state=MerchIssuanceState.cancellation_bad)
    dp.register_callback_query_handler(merch_cancellation_choice,
                                       text=org_merch_issuance_callbacks.CANCEL_TEXT_CB,
                                       state=MerchIssuanceState.cancellation_merch_number_confirmation)
    dp.register_callback_query_handler(merch_cancellation_change,
                                       text=org_merch_issuance_callbacks.MERCH_RETURN_BACK_MORE_CB,
                                       state=MerchIssuanceState.cancellation_merch_number_choice)
    dp.register_callback_query_handler(merch_cancellation_change,
                                       text=org_merch_issuance_callbacks.MERCH_RETURN_BACK_LESS_CB,
                                       state=MerchIssuanceState.cancellation_merch_number_choice)
    dp.register_callback_query_handler(merch_return_back_number_confirm,
                                       text=MERCH_RETURN_BACK_CONFIRM_CB,
                                       state=MerchIssuanceState.cancellation_merch_number_choice)
    dp.register_callback_query_handler(merch_return_back_number_process,
                                       text=MERCH_RETURN_BACK_CONFIRM_CB,
                                       state=MerchIssuanceState.cancellation_merch_number_confirmation)
