from aiogram import Bot, Dispatcher

async def init_bot(token):
    bot = Bot(token = token)
    dp = Dispatcher()
    return bot, dp