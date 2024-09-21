from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.db.models import User, Wallet
from bot.config import TORTOISE_ORM
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist


router = Router()

@router.message(Command(commands=["perfil"]))
async def analysis_handler(message: Message):
    await Tortoise.init(TORTOISE_ORM)

    # Verifica si el usuario ya está registrado
    user_id = message.from_user.id

    try:
        user = await User.get(id=user_id)
        wallet = await Wallet.filter(user_id=user.id).first()
    except Exception as e:
        print(e)
    investor_map = {0.2: "Conservador", 0.4: "Medio", 0.6: "Atrevido"}
    investor_profile = investor_map.get(user.investor_profile)
    msg = (
            "<b>Perfil</b>:\n"
            f"Nombre: <b>{user.name}</b>\n"
            f"Teléfono: <b>{user.phone}</b>\n"
            f"Capital actual: <b>{wallet.current_capital}€</b>\n"
            f"Perfil de inversor: <b>{investor_profile}</b>\n"
            f"Rentabilidad: <b>{round(wallet.profit, 2)}%</b>\n"
            f"Max drawdown: <b>{round(wallet.max_drawdown, 2)}%</b>\n"
            f"Número de operaciones: <b>{wallet.number_of_operations}</b>\n"
        ) 
    await message.answer(msg, parse_mode='HTML')