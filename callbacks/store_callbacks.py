from aiogram.utils.callback_data import CallbackData

STORE_MAIN_CB = "store_main_page"
STORE_CATEGORY_CB = CallbackData("show_store_category", "category_id")
JOIN_TUC_CB = "store_join_tuc"

ITEM_CB = CallbackData("show_item_id", "stuff_id")
BUY_NO_COLORS_SIZES_CB = CallbackData("buy_no_colors_sizes", "stuff_id")
BUY_COLORS_SIZES_CB = CallbackData("buy_colors_sizes", "colors_sizes_id")
BUY_CONFIRM_COLORS_SIZES_CB = CallbackData("buy_confirm_colors_sizes", "colors_sizes_id")
BUY_CONFIRM_NO_COLORS_SIZES_CB = CallbackData("buy_confirm_no_colors_sizes", "stuff_id")
