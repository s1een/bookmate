#!venv/bin/python

from aiogram import executor

from create_bot import dp, bot
from handlers import msg_handlers

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
