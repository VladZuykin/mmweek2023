import json
import os
from io import BytesIO

from aiogram.types import ParseMode, Message, InputMedia, InlineKeyboardMarkup, InputFile, InputMediaPhoto

from database.db_funcs import DataBase

CONFIG_TEMPLATE = """{
  "tg_bot_token": "",
  "tg_admin_bot_username": "",
  "db_path": "database/mmweek2023db.db",
  "admins_chat_id": "",
  "support_chat_id": "",
  "org_bot_token": ""
}
"""


class Config:
    def __init__(self, config_path: str):
        self.config_path: str = config_path
        self.bot_token: str = ''
        self.db_path = None
        self.admins_chat_id = None
        self.admin_bot_username: str = ''
        self.support_chat_id = None
        self.org_bot_token = ""

        if os.path.exists(config_path):
            self.load_settings()
        else:
            self.create_file()
            raise FileNotFoundError("Создан файл config.json, заполните его")

    def load_settings(self):
        with open(self.config_path, 'r', encoding='utf-8') as file:
            config = json.loads(file.read())
            self.bot_token = config['tg_bot_token']
            if not self.bot_token:
                raise ValueError("Токен бота не указан. Добавьте его в config.json")
            self.admin_bot_username = config['tg_admin_bot_username']
            self.db_path = config["db_path"]
            self.admins_chat_id = config["admins_chat_id"]
            self.support_chat_id = config["support_chat_id"]
            self.org_bot_token = config["org_bot_token"]

    def create_file(self):
        with open(self.config_path, 'w', encoding='utf-8') as file:
            file.write(CONFIG_TEMPLATE)


class CachedImages:
    def __init__(self, db: DataBase, start_path):
        self.db = db
        self.START_PATH = start_path
        db.execute("DELETE FROM img_cache")

    async def send_cached_img(self, message: Message, path: str, caption: str,
                              reply_markup: InlineKeyboardMarkup,
                              parse_mode,
                              message_edit=True):
        res_path = self.START_PATH + path
        img_id = self.db.execute("SELECT img_id FROM img_cache WHERE path = ?", res_path, fetch="one")
        if not img_id:
            res = res_path
        else:
            res, = img_id
        if message_edit:
            if not img_id:
                message = await message.edit_media(
                    InputMediaPhoto(InputFile(res), caption=caption, parse_mode=parse_mode),
                    reply_markup=reply_markup)
            else:
                message = await message.edit_media(InputMediaPhoto(res, caption=caption, parse_mode=parse_mode),
                                                   reply_markup=reply_markup)
        else:
            if not img_id:
                message = await message.answer_photo(InputFile(res), caption=caption, reply_markup=reply_markup,
                                                     parse_mode=parse_mode)
            else:
                message = await message.answer_photo(res, caption=caption, reply_markup=reply_markup,
                                                     parse_mode=parse_mode)
        if not img_id:
            self.db.execute("INSERT INTO img_cache (path, img_id) VALUES (?, ?) "
                            "ON CONFLICT (path) DO NOTHING", res_path, message.photo[-1].file_id, commit=True)
