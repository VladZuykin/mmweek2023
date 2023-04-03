import asyncio
import datetime
import collections
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram import types, Dispatcher

from middleware.functions import dt_to_dtdict, dtdict_to_str, ACCUSATIVE_TIME_UNITS_FORMS
from middleware import texts

def set_limits(period: int, period_max_messages: int, ban_time=60, key=None):
    """
    Декоратор для настройки антифлуда для конкретного обработчика

    :param period: Рассматрываемый период получения update-ов
    :param period_max_messages: Максимальное количество сообщений за этот период
    :param ban_time: Время бана при превышении period_max_messages
    :param key: Ключ для бана при злоупотреблении именно этого функционала бота
    :return:
    """

    def decorator(func):
        setattr(func, 'throttling_period', period)
        setattr(func, 'throttling_period_max_messages', period_max_messages)
        setattr(func, 'throttling_ban_time', ban_time)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class AntispamMiddleware(BaseMiddleware):
    """
    Промежуточное ПО для антифлуда
    """

    def __init__(self, period=10, period_max_messages=20, ban_time=60, key_prefix='antispam'):
        """
        Установка параметров по умолчанию для антифлуда

        :param period: Рассматрываемый период получения update-ов
        :param period_max_messages: Максимальное количество сообщений за этот период
        :param ban_time: Время бана при превышении period_max_messages
        :param key_prefix: Префикс, добавляемый в ключ для storage
        """

        self.antispam_period = period
        self.antispam_period_max_messages = period_max_messages
        self.antispam_ban_time = ban_time
        self.prefix = key_prefix

        super(AntispamMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        Этот обработчик вызывается, когда dispatcher получает сообщение
        """
        # Получаем текущий обработчик
        handler = current_handler.get()
        # Получаем диспетчер
        dispatcher = Dispatcher.get_current()
        if handler:
            # Для сообщений, которые попали в какой-то хендлер
            # Если обработчик был настроен в set_limits, получаем параметры, иначе устанавливаем дефолтные
            antispam_period = getattr(handler, 'throttling_period', self.antispam_period)
            antispam_period_max_messages = getattr(handler, 'throttling_period_max_messages',
                                                   self.antispam_period_max_messages)
            antispam_ban_time = getattr(handler, 'throttling_ban_time', self.antispam_ban_time)

            # Ключ нужен для хранения и использования последних апдейтов конкретной группы хендлеров
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            # Для сообщений, которые не пройдут ни в какой хендлер

            # antispam_period = self.antispam_period
            # antispam_period_max_messages = self.antispam_period_max_messages
            # antispam_ban_time = self.antispam_ban_time
            # key = "message"
            return

        # Антиспам не будет обращать внимание на update с ban_time равным 0
        if antispam_ban_time == 0:
            return

        data = await dispatcher.storage.get_data(chat=message.chat.id,
                                                 user=message.from_user.id)
        # Проверка на бан
        if data.get(f"{self.prefix}_banned"):
            if datetime.datetime.now() - data.get(f"{self.prefix}_ban_time") < data.get(f"{self.prefix}_ban_td"):
                # Отменяем выполнение обработчика
                raise CancelHandler()
            else:
                # Обновление информации о бане
                data[f"{self.prefix}_banned"] = False
                data[f"{self.prefix}_ban_time"] = None
                data[f"{self.prefix}_ban_td"] = None
                data[f"{self.prefix}_{key}_last_updates"].clear()

        # Обновление информации о последних обновлениях
        if f"{self.prefix}_{key}_last_updates" not in data.keys():
            data[f"{self.prefix}_{key}_last_updates"] = collections.deque(maxlen=antispam_period_max_messages + 1)
        data[f"{self.prefix}_{key}_last_updates"].append(datetime.datetime.now())

        # Получение информации о последних обновлениях
        throttle_times = data.get(f"{self.prefix}_{key}_last_updates")

        # Проверка, не превышен ли лимит по сообщениям
        if throttle_times and len(throttle_times) > antispam_period_max_messages and \
                datetime.datetime.now() - throttle_times[0] < datetime.timedelta(seconds=antispam_period):
            data[f"{self.prefix}_banned"] = True
            data[f"{self.prefix}_ban_time"] = datetime.datetime.now()
            data[f"{self.prefix}_ban_td"] = datetime.timedelta(seconds=antispam_ban_time)

            # Формирование текста из timedelta
            delta_text = dtdict_to_str(dt_to_dtdict(datetime.timedelta(seconds=antispam_ban_time)),
                                       time_units_forms=ACCUSATIVE_TIME_UNITS_FORMS)
            await message.answer(texts.BAN_TEXT_TEMPLATE.format(delta_text))

            # Выгрузка обновлённой информации в storage
            await dispatcher.storage.update_data(chat=message.chat.id,
                                                 user=message.from_user.id,
                                                 data=data)
            await asyncio.sleep(antispam_ban_time)
            await message.answer(texts.UNBAN_TEXT)
            raise CancelHandler()

        # Выгрузка обновлённой информации в storage
        await dispatcher.storage.update_data(chat=message.chat.id,
                                             user=message.from_user.id,
                                             data=data)
