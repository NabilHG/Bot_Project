from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

async def init_bot(token):
    bot = Bot(token)
    bot.parse_mode = ParseMode.HTML  # Establecer el modo de análisis de HTML
    dp = Dispatcher()
    return bot, dp