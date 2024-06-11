from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

async def init_bot(token):
    bot = Bot(token = token)
    dp = Dispatcher()
    return bot, dp