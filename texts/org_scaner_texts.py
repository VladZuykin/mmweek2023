from texts import org_menu_texts

# Тексты сообщений
NO_EVENT_ERROR_TEXT = "За тобой не закреплено мероприятие"

SCAN_CODE_TEMPLATE = "Текущее мероприятие: {}. \n" \
                     "Введи код участника или нажми \"" + org_menu_texts.BACK_TO_MENU_BUTTON_TEXT + \
                     "\", чтобы вернуться в меню"
SCAN_CODE_TEXT = "Введи код участника или нажми \"" + org_menu_texts.BACK_TO_MENU_BUTTON_TEXT + \
                 "\", чтобы вернуться в меню"

NO_PARTICIPANT_TEXT = "Такого участника нет в базе, он не зарегистрирован:("
MONEY_GIVEN_ALREADY_TEMPLATE = "Участнику <u>{}</u> уже начислены баллы"
GIVE_MONEY_TEMPLATE = "Участник: <u>{}</u>. Начислить {}i?"
MONEY_GIVEN_TEMPLATE = "Начислено {}i участнику <u>{}</u>"
NOT_MONEY_GIVEN_TEMPLATE = "Участнику <u>{}</u> код не просканирован"

COERCE_BACK_TO_MENU_TEXT = "Пожалуйста, закончи с вопросом выше о начислении баллов"

# Тексты кнопок
YES_BUTTON_TEXT = "Да"
NO_BUTTON_TEXT = "Нет"
