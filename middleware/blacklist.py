from aiogram import types
from aiogram.dispatcher.handler import current_handler, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from database import db_funcs

class BlacklistMiddleware(BaseMiddleware):
    def __init__(self, db: db_funcs.DataBase):
        """
            Промежуточное ПО для отсеивания забаненных
        """
        self.db = db
        self.blacklist = []
        super(BlacklistMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        handler = current_handler.get()
        if handler and self.db.in_blacklist(message.from_user.id):
            raise CancelHandler()

