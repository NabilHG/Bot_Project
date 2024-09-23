from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.config import TORTOISE_ORM, FIRST_ADMIN, SECOND_ADMIN

router = Router()

@router.message(Command(commands=["ayuda", "info"]))
async def info_handler(message: Message):

    msg = (
        "ℹ️ Esto son los comandos que puedes utilizar:\n"
        "<b>/info</b> para ver que comandos puedes utilizar\n"
        "<b>/perfil</b> se muestra tu perfil actualizado\n"
        "<b>/actualizar</b> para editar ciertas características de tu perfil\n"
        "<b>/generar_link</b> se genera un link para poder invitar a raiz de tu cuenta\n"
        "<b>/comprar TICKER</b> debes de proporcionar el ticker concreto para realizar una compra.\n<code>Ejemplo: <b>/comprar AAPL</b> (se realizará una operación para guardar una compra de apple).</code>\n"
        "<b>/vender TICKER</b> debes de proporcionar el ticker concreto para realizar una venta.\n<code>Ejemplo: <b>/vender AAPL</b> (se realizará una operación para guardar una venta de apple).</code>\n"
        "❗<b>Importante</b>: recuerda que el bot <b>no</b> tiene capacidad de comprar ni de decidir por ti. Los comandos de /comprar y /vender solo son para llevar un registro sobre la rentabilidad del sistema."
    )
    user_id = message.from_user.id
    print(user_id, )
    if user_id in [int(FIRST_ADMIN)]:
        msg += "\n<b>/eliminar</b> para eliminar a un usuario mediante el teléfono"    
    await message.answer(msg, parse_mode='HTML')
        