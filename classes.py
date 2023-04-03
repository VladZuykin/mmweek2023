import json

class Config:
    def __init__(self, config_path: str):
        self.config_path: str = config_path
        self.bot_token: str = ''
        self.db_path = None

        self.load_settings()

    def load_settings(self):
        with open(self.config_path, 'r', encoding='utf-8') as file:
            config = json.loads(file.read())
            self.bot_token = config['tg_bot_token']
            if not self.bot_token:
                raise ValueError("Токен бота не указан. Добавьте его в config.json")
            self.db_path = config["db_path"]
