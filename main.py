from aiogram import executor

import startup_functions
from middleware import antispam, blacklist, admins

from bot_create import bot, dp, db
from handlers import registration_handlers, menu_handlers, store_handlers

if __name__ == '__main__':
    print("Bot startup.")

    store_handlers.register_store_handlers()
    registration_handlers.register_registration_handlers()
    menu_handlers.register_menu_handlers()
    dp.middleware.setup(admins.AdminMalware(db))
    dp.middleware.setup(blacklist.BlacklistMiddleware(db))
    dp.middleware.setup(antispam.AntispamMiddleware())
    executor.start_polling(dp, on_startup=startup_functions.on_startup, on_shutdown=startup_functions.on_shutdown)
    print("Bot is stopped.")
