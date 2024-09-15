from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command(commands=["no", "NO", "No", "nO"]))
async def ask_to_buy_handler(message: Message):
    response = message.text
    if response in ["no", "NO", "No", "nO"]:
        await message.answer("Cancelando")

