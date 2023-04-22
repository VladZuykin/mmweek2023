from texts.wallet_names import WALLET_SINGULAR, WALLET_PLURAL, WALLET_GENITIVE

# Тексты кнопок
NOT_IN_TUC_BUTTON_TEXT = "Не состою 🥺"
FULLNAME_FAILURE_BUTTON_TEXT = "Я ошибся в ФИО 😅"
ACTUALLY_IN_TUC_BUTTON_TEXT = "Вообще-то я в ПК 🤨"

SEND_TUC_MANUAL_CHECK_QUERY_TEXT = "Отправить на ручную проверку"
NO_TUC_MANUAL_CHECK_QUERY_TEXT = "Нет, я пошутил"

IT_IS_ME_SIMILAR_BUTTON_TEXT = "Да, это я"
IT_IS_NOT_ME_SIMILAR_BUTTON_TEXT = "Нет, вы ошиблись"

SECOND_CHECK_IN_TUC_BUTTON_TEXT = "Да, я в Профкоме"
SECOND_CHECK_NOT_IN_TUC_BUTTON_TEXT = "Нет 😔"

# Тексты сообщений
GREETING_FIRST_MESSAGE_TEXT = "Привет, ну как там твоя учёба?"
GREETING_SECOND_MESSAGE_TEXT = "Напиши, как тебя зовут," \
                               " чтобы ты мог <b><i>получить заслуженный мерч</i></b> в конце нашей Недели"
GREETING_THIRD_MESSAGE_TEXT = "Кстати, цены в магазине зависят от того, состоишь ли ты в Профкоме, " \
                              "а мерч мы выдаём по студенческому билету, так что не ошибайся при вводе данных!"
GREETING_FOURTH_MESSAGE_TEXT = "Жду твоё ФИО"



JOKE_ANSWER = "Ахаххахаахаххаха"
REPEAT_FULLNAME_ASK_TEXT = "Ничего страшного 😉 Тогда введи ФИО ещё раз, пожалуйста."
WAIT_FOR_TEXT = "Вообще-то я жду от тебя текст, попробуй ещё раз"
FOUND_SIMILAR_TEMPLATE = "Ой, тебя случайно не зовут {}?"
ASK_IF_IN_TUC_TEXT = "А такой человек есть в списке Профкома, это ты?"

NICE_TO_MEET_TEMPLATE = "Приятно познакомиться, {}"
NOT_IN_TUC_TEXT = "Ты не состоишь в Профкоме? 😥"
IN_TUC_TEXT = "Отличная новость! Я нашёл тебя в списках Профкома, так что ты сможешь получить мерч со скидкой!"
CAN_JOIN_TUC_TEXT = "Не переживай, поздно - это когда уже поздно, а пока не поздно - не поздно"
REGISTERED_TEXT1 = f"В таком случае я зарегистрировал тебя на Неделю Матмеха 🎉"
SAD_REGISTERED_TEXT1 = f'В таком случае я грустно зарегистрировал тебя на Неделю Матмеха, ' \
                       f'организованную <a href="https://vk.com/mmprofkom">Профкомом Матмеха</a>'
USUAL_REGISTERED_TEXT1 = "Я зарегистрировал тебя на Неделю Матмеха"
MEANTIME_REGISTERED_TEXT1 = f"Тем временем я зарегистрировал тебя на Неделю Матмеха 😎"
REGISTERED_TEXT2 = f"Теперь ты можешь посещать наши крутые мероприятия и получать за это местную валюту - " \
                   f"{WALLET_PLURAL}. " \
                   f"Их ты сможешь обменять на мерч Матмеха!"
NOT_IN_TUC_MANUAL_CHECK_TEXT1 = "Если ты действительно состоишь в Профкоме, " \
                                "то я могу отправить запрос на ручную проверку "
NOT_IN_TUC_MANUAL_CHECK_TEXT2 = "Пока не подтвердится, что ты профкомовец, мерч будет без скидки"
NOT_IN_TUC_MANUAL_CHECK_TEXT3 = "Придётся подождать, но что поделаешь, жизнь - сложная штука, иногда кажется, " \
                                "что она несправедлива, " \
                                "но мы должны продолжать идти вперед и верить в себя"

TUC_MANUAL_CHECK_SENT_TEXT = "Заявка отправлена. " \
                             "Скоро мы её проверим, не забудем про тебя, лови котика, чтобы было спокойнее"

TUC_MANUAL_CHECK_TEMPLATE = "Пользователь @{}\n\n" \
                            "Представился именем:\n" \
                            "{}\n\n" \
                            "Считает, что он в ПК\n" \
                            "Ссылка на него\n{}"

PREVIOUS_BOT_REGISTERED_TEMPLATE = "Вау, ты участвовал в предыдущей неделе Матмеха, держи за это {} " + \
    WALLET_GENITIVE
