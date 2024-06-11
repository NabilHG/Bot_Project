from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold 

router = Router()

@router.message(Command(commands=["backtest"]))
async def analysis_handler(message: Message):
    msg = Text(Bold('Analysis Report:') ,"Here is your backtest.")  
    await message.answer(**msg.as_kwargs())
