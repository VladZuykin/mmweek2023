from texts import org_menu_texts

# Тексты кнопок
RANDOM_PROMO_BUTTON_TEXT = "Случайно"
INFINITE_USES_BUTTON_TEXT = "Не ограничено"


# Тексты сообщений
HOW_CREATE_PROMO_TEXT = "Введи промокод или нажми \"" \
                        + RANDOM_PROMO_BUTTON_TEXT + "\", чтобы сгенерировать автоматически. \n\n" \
                        "Нажми \"" + org_menu_texts.BACK_TO_MENU_BUTTON_TEXT + \
                        "\", чтобы вернуться в меню"
PROMO_ALREADY_EXISTS_TEXT = "Такой промокод уже существует. \n" \
                            "Пожалуйста, введи другой или нажми \"" + RANDOM_PROMO_BUTTON_TEXT + "\""
NUM_POINTS_PROMO_TEXT = "На какую сумму промокод?"
NUM_POINTS_ERROR_PROMO_TEXT = "Пожалуйста, введи целое положительное число"
NUM_USES_PROMO_TEXT = "Введи количество использований или нажми \"" + INFINITE_USES_BUTTON_TEXT + "\""
NUM_USES_ERROR_PROMO_TEXT = "Пожалуйста, введи целое положительное число или нажми \"" \
                            + INFINITE_USES_BUTTON_TEXT + "\""
PERIOD_PROMO_TEXT = "Введи срок действия промокода в часах (например: 3ч) или в днях (например: 1д)"
PERIOD_ERROR_PROMO_TEXT = "Пожалуйста, введи срок действия в формате \"(целое число >0)ч\" или \"(целое число >0)д\""

PROMO_ADDED_TEMPLATE = "Создан промокод \'<code>{}</code>\' на сумму {}i\n\n"
PROMO_ADDED_INFO_TEMPLATE = "Срок действия: <b>{}</b>\n" \
                            "Число применений: <b>{}</b>"
PROMO_TO_LIST_TEMPLATE = "Промокод \'<code>{}</code>\' на сумму {}i.\n"
PROMO_TO_LIST_INFO_TEMPLATE = "Срок действия: до <b>{}</b>\n" \
                              "Число применений: <b>{}</b>"
INFINITE_USES_TEXT = "не ограничено"
