from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Almacenamiento en memoria para FSM
from bot.handlers import backtest, info, start, buy, sell, update_profile
from bot import analysis
from main import router


async def init_bot(token):
    bot = Bot(token = token)
    storage = MemoryStorage()  # Configura el almacenamiento en memoria para los estados
    dp = Dispatcher(storage=storage)    
    return bot, dp

async def init_routers(dp):
    dp.include_router(router)
    dp.include_router(analysis.router)
    dp.include_router(backtest.router)
    dp.include_router(info.router)
    dp.include_router(start.router)
    dp.include_router(buy.router)
    dp.include_router(sell.router)
    dp.include_router(update_profile.router)