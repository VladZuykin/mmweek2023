import json
import os

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
