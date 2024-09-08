from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold 

router = Router()

@router.message(Command(commands=["start", "help", "info"]))
async def analysis_handler(message: Message):
    # user_id = message.from_user.id  # Obtén el ID del usuario
    # print(user_id)
    a = message.from_user.first_name    
    b = message.from_user.last_name    
    print(a, b)
    msg = Text(Bold('Info here:') ,"Explain what the bot does and which commands are avaliable")
    await message.answer(**msg.as_kwargs())