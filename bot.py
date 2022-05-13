#!venv/bin/python

from aiogram import executor
from aiogram.utils.executor import start_webhook

from create_bot import dp, bot
from handlers import msg_handlers
from config.bot_config import WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT


async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)


async def on_shutdown(dispatcher):
    await bot.delete_webhook()


if __name__ == "__main__":
    msg_handlers.register_handlers_client(dp)
    # start_webhook(
    #     dispatcher=dp,
    #     webhook_path=WEBHOOK_PATH,
    #     skip_updates=True,
    #     on_startup=on_startup,
    #     on_shutdown=on_shutdown,
    #     host=WEBAPP_HOST,
    #     port=WEBAPP_PORT,
    # )
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)
