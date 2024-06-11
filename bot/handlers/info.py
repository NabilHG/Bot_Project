from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import *

router = Router()

@router.message(Command(commands=["start", "help", "info"]))
async def analysis_handler(message: Message):
    msg = Text(Bold('Info here:') ,"Explain what the bot does and which commands are avaliable")
    await message.answer(**msg.as_kwargs())