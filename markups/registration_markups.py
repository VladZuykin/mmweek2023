from aiogram.types.reply_keyboard import ReplyKeyboardMarkup, KeyboardButton

NOT_IN_TUC_MARKUP = ReplyKeyboardMarkup([[KeyboardButton("Не состою 🥺")],
                                         [KeyboardButton("Я ошибся в ФИО"), KeyboardButton("Вообще-то я в ПК")]],
                                        resize_keyboard=True, one_time_keyboard=True)
