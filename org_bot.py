from aiogram import executor

import startup_functions
from middleware import admins, blacklist, antispam

from org_bot_create import dp, db
from handlers import org_menu_handlers


if __name__ == '__main__':
    print("Bot startup.")
    org_menu_handlers.register_org_menu_handlers()
    dp.middleware.setup(admins.AdminMalware(db))
    dp.middleware.setup(blacklist.BlacklistMiddleware(db))
    executor.start_polling(dp, on_startup=startup_functions.on_startup, on_shutdown=startup_functions.on_shutdown)
    print("Bot is stopped.")
