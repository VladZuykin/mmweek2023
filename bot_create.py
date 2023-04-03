# from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from classes import Config
from database import db_funcs

config = Config("config.json")
bot = Bot(token=config.bot_token)
storage = MemoryStorage()
# storage = RedisStorage2(database=5)
dp = Dispatcher(bot, storage=storage)
db = db_funcs.DataBase(config.db_path)