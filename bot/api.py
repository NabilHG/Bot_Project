from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage  # Almacenamiento en memoria para FSM

async def init_bot(token):
    bot = Bot(token = token)
    storage = MemoryStorage()  # Configura el almacenamiento en memoria para los estados
    dp = Dispatcher(storage=storage)    
    return bot, dp