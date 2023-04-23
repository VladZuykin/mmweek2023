from aiogram import types
from aiogram.dispatcher.handler import current_handler, CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from database.db_funcs import DataBase


def check(level):
    """
    Декоратор для того, чтобы пользователя проверили на админку
    :return:
    """

    def decorator(func):
        setattr(func, 'admin_check', True)
        setattr(func, 'admin_check_level', level)
        return func

    return decorator


class AdminMalware(BaseMiddleware):
    """
    Промежуточное ПО для антифлуда
    """

    def __init__(self, db: DataBase, all_are_admins=False):
        """
        Промежуточное ПО для отсеивания админов
        :param all_are_admins: Если True, то все воспринимаются как администраторы
        """

        self.all_are_admins = all_are_admins
        self.db = db
        super(AdminMalware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        Этот обработчик вызывается, когда dispatcher получает сообщение
        """
        have_right = await self.user_have_right(message.from_user.id)
        if not have_right:
            await message.answer("Извините, но у вас не хватает прав.")
            raise CancelHandler()

    async def on_process_callback_query(self, callback: types.CallbackQuery, data: dict):
        """
        Этот обработчик вызывается, когда dispatcher получает Callback Query
        """
        have_right = await self.user_have_right(callback.from_user.id)
        if not have_right:
            await callback.answer("Извините, но у вас не хватает прав.")
            raise CancelHandler()

    async def user_have_right(self, tg_id):
        # Получаем текущий обработчик
        handler = current_handler.get()
        if not handler or self.all_are_admins:
            return True

        admin_check = getattr(handler, 'admin_check', False)
        admin_level_check = getattr(handler, 'admin_check_level', None)
        if not admin_check or not admin_level_check:
            return True

        if self.db.have_admin_rights(tg_id, admin_level_check):
            return True
        return False
