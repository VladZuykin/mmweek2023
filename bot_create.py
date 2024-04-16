# from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import classes
import constants
from classes import Config
from create_db import db

config = Config("config.json")
bot = Bot(token=config.bot_token)
storage = MemoryStorage()
# storage = RedisStorage2(database=5)
dp = Dispatcher(bot, storage=storage)
store_cached_imgs = classes.CachedImages(db, constants.STORE_PATH)
