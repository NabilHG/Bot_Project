from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold 
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from bot.db import models
from tortoise.exceptions import IntegrityError
from tortoise import Tortoise
from tortoise.exceptions import IntegrityError
from bot.config import TORTOISE_ORM, MATRIX
from datetime import datetime


router = Router()

class ProccesBuyForm(StatesGroup):
    amount = State()


async def proccess_buy(id, message, capital, ticker):
    # Conecta la base de datos
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    try:
        user = await models.User.filter(id=id).first()  # Obtener todos los usuarios
        print(user, "user")
    except Exception as e:
        print(f"Error fetching users: {e}")
    try:
        wallet = await models.Wallet.filter(user_id=user.id).first()
    except Exception as e:
        print(e)
    print(wallet, "wallet")
    try:
        share = await models.Share.filter(ticker=ticker).first()
    except Exception as e:
        print(e)
    print(share, "share")
    # Guardar la compra en la base de datos
    print(capital, "EO")
    try:
        operation = await models.Operation.create(
            ticker=share.ticker,
            status='open',
            buy_date=datetime.now(),
            capital_invested=capital,
            wallet_id=wallet.id
        )

        wallet_share = await models.WalletShare.create(
            wallet=wallet,
            share=share
        )

        # Guardar los cambios en la base de datos
        await operation.save()
        await wallet_share.save()
        await message.answer("Proceso guardado.")
    except IntegrityError as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

@router.message(Command(commands=["comprar"]))
async def ask_to_buy_handler(message: Message, state: FSMContext):

    args = message.text.split(maxsplit=1)
    
    if not len(args) > 1:
        await message.reply("Por favor, proporciona un valor después del comando.")

    ticker = args[1].upper()
    print(ticker,MATRIX[max(MATRIX.keys())], args[0])
    if args[0] == "/comprar" and ticker in MATRIX[max(MATRIX.keys())]:
        print("HOLA")
        # Guardar el valor en el FSMContext
        await state.update_data(ticker=ticker)

        await message.answer("¿Qué cantidad deseas invertir?")
        await state.set_state(ProccesBuyForm.amount)


@router.message(ProccesBuyForm.amount)
async def ask_amount(message: Message, state:FSMContext):
    print("OYE5")
    id = message.from_user.id
    user_data = await state.get_data()
    ticker = user_data.get("ticker")  # Obtener el valor

    try:
        capital = float(message.text)
        if capital > 0:
            await proccess_buy(id, message, capital, ticker)
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")
        return  # No avanzamos de estado

