from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


@router.message(Command(commands=["rechazar"]))
async def ask_to_buy_handler(message: Message):
    response = message.text.lower()
    if response == '/rechazar':
        await message.answer("Cancelado.")

