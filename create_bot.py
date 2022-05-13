import logging
import logging.config

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher.filters.state import StatesGroup, State

from config.bot_config import TOKEN
from data_base.sqlite_db import BotDB

cats = ['img/cat.png', 'img/cat2.png', 'img/cat3.png', 'img/cat4.png', 'img/cat5.png',
        'img/cat6.png', 'img/cat7.png', 'img/cat8.png', 'img/cat9.png', 'img/cat10.png']


# Utils
class Form(StatesGroup):
    choice = State()
    book = State()
    author = State()
    series = State()


if not TOKEN:
    exit("Error: no token provided")

bot = Bot(token=TOKEN)
# Диспетчер для бота
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
BotDB = BotDB('data_base/book_mate.db')
# Включаем логирование, чтобы не пропустить важные сообщения
# filename='logs/bot_log.log'
logging.basicConfig(format=u'%(filename)s [ LINE:%(lineno)+3s ]#%(levelname)+8s [%(asctime)s]  %(message)s',
                    level=logging.INFO)
