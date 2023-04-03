import json
import os

CONFIG_TEMPLATE = """{
  "tg_bot_token": "",
  "db_path": "database/mmweek2023db.db",
  "admins_chat_id": ""
}
"""

class Config:
    def __init__(self, config_path: str):
        self.config_path: str = config_path
        self.bot_token: str = ''
        self.db_path = None
        self.admins_chat_id = None

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
            self.db_path = config["db_path"]
            self.admins_chat_id = config["admins_chat_id"]

    def create_file(self):
        with open(self.config_path, 'w', encoding='utf-8') as file:
            file.write(CONFIG_TEMPLATE)
