from aiogram import executor

import functions
from middleware import antispam, blacklist, admins
from database import db_funcs

from bot_create import bot, dp, config, db
from handlers import registration_handlers


if __name__ == '__main__':
    print("Bot startup.")
    registration_handlers.register_registration_handlers()
    dp.middleware.setup(admins.AdminMalware(db))
    dp.middleware.setup(blacklist.BlacklistMiddleware(db))
    dp.middleware.setup(antispam.AntispamMiddleware())
    executor.start_polling(dp, on_startup=functions.on_startup, on_shutdown=functions.on_shutdown)
    print("Bot is stopped.")
