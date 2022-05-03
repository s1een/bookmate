#!venv/bin/python

from aiogram import executor
from create_bot import dp
from handlers import msg_handlers


if __name__ == "__main__":
    msg_handlers.register_handlers_client(dp)
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
