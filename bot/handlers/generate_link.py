import base64
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.db.models import User
from bot.config import TORTOISE_ORM, FIRST_ADMIN
from tortoise import Tortoise

router = Router()

async def encode_id(id):
    user_bytes = str(id).encode('utf-8')
    return base64.urlsafe_b64encode(user_bytes).decode('utf-8')

async def encode_multiple_id(id):
    print(FIRST_ADMIN, id)
    combined_params = f'{FIRST_ADMIN}-{str(id)}'
    # combined_params = f'{str(id)}-{1234567890}'

    return base64.urlsafe_b64encode(combined_params.encode('utf-8')).decode('utf-8')

@router.message(Command(commands=["generar_link"]))
async def generate_link(message: Message):
    await Tortoise.init(TORTOISE_ORM)

    # Verifica si el usuario ya está registrado
    user_id = message.from_user.id
    try:
        user = await User.get(id=user_id)
    except Exception as e:
        print(e)

    if user.is_lictor:
        encoded_id = await encode_multiple_id(user.id)
    else:
        encoded_id = await encode_id(user.id)

    link = f"https://t.me/Avisador_STM_bot?start={encoded_id}"

    await message.answer(f'Con este enlaze pueden invitar a quien quieras: {link}')