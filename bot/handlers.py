from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold

def setup_handlers(router: Router):
    @router.message(CommandStart())
    async def command_start_handler(message: Message):
        await message.answer(f"Hello, {hbold(message.from_user.full_name)}! for more info, type /help")

    @router.message()
    async def echo_handler(message: Message):
        if message.text == "/help":
            await message.answer("help here")
            return
