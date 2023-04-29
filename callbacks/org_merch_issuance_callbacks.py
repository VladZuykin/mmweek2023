from aiogram.utils.callback_data import CallbackData

MERCH_ISSUANCE_CB = CallbackData("merch_issuance_user_merch", "purchases_id")
MERCH_ISSUANCE_CONFIRM_CB = "confirm_issuance"
MERCH_ISSUANCE_LESS_CB = "merch_issuance_less"
MERCH_ISSUANCE_MORE_CB = "merch_issuance_more"

MERCH_RETURN_BACK_CB = CallbackData("merch_cancellation_user_merch", "purchases_id")
MERCH_RETURN_BACK_CHOOSE_CB = "merch_cancellation_choose"
MERCH_RETURN_BACK_LESS_CB = "merch_return_back_less"
MERCH_RETURN_BACK_MORE_CB = "merch_return_back_more"
MERCH_RETURN_BACK_CONFIRM_CB = "confirm_return_back"
CANCEL_TEXT_CB = "cancel"

