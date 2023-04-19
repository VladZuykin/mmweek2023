from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from classes import Config
from database import org_db_funcs


config = Config("config.json")
bot = Bot(token=config.org_bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = org_db_funcs.OrgDataBase(config.db_path)
