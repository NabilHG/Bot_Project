import os
import json
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.db import models
from tortoise.exceptions import IntegrityError
from tortoise import Tortoise
from bot.config import TORTOISE_ORM, MATRIX
from datetime import datetime
from bot.analysis import latest_close_price

router = Router()

class ProccesBuyForm(StatesGroup):
    amount = State()


async def proccess_buy(id, message, capital, ticker):
    # Conecta la base de datos
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    try:
        user = await models.User.filter(id=id).first()  # Obtener todos los usuarios
    except Exception as e:
        print(f"Error fetching users: {e}")
    try:
        wallet = await models.Wallet.filter(user_id=user.id).first()
    except Exception as e:
        print(e)
    try:
        share = await models.Share.filter(ticker=ticker).first()
    except Exception as e:
        print(e)

    purchased_price = round(await latest_close_price(ticker, 'data'), 2)
    print(purchased_price, 'NY')
    # Guardar la compra en la base de datos
    try:
        operation = await models.Operation.create(
            ticker=share.ticker,
            status='open',
            buy_date=datetime.now(),
            capital_invested=capital,
            purchased_price=purchased_price,
            wallet_id=wallet.id
        )

        wallet_share = await models.WalletShare.create(
            wallet=wallet,
            share=share
        )

        # Guardar los cambios en la base de datos
        await operation.save()
        await wallet_share.save()
        await message.answer(f"✅ <b>Compra guardada:</b>\n <b>{ticker}</b>, con precio de cierre <b>{purchased_price}€</b> y capital invertido <b>{capital}€</b>", parse_mode='HTML')
    except IntegrityError as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

@router.message(Command(commands=["comprar"]))
async def ask_to_buy_handler(message: Message, state: FSMContext):

    args = message.text.split(maxsplit=1)
    
    if not len(args) > 1:
        await message.reply("Por favor, proporciona un valor después del comando.")
        return

    ticker = args[1].upper()
    if args[0] == "/comprar" and ticker in MATRIX[max(MATRIX.keys())]:
        # Guardar el valor en el FSMContext
        await state.update_data(ticker=ticker)

        await message.answer("¿Qué cantidad deseas invertir?")
        await state.set_state(ProccesBuyForm.amount)

@router.message(Command(commands=["rechazar"]), ProccesBuyForm.amount)
async def cancel_buy_handler(message: Message, state: FSMContext):
    await message.answer("Operación cancelada.")
    await state.clear()  # Limpiar el estado para cancelar la operación

@router.message(ProccesBuyForm.amount)
async def ask_amount_to_buy(message: Message, state: FSMContext):
    id = message.from_user.id
    user_data = await state.get_data()
    ticker = user_data.get("ticker")  # Obtener el valor

    try:
        capital = float(message.text)
        if capital > 0:
            await proccess_buy(id, message, capital, ticker)
            await state.clear()  # Limpiar el estado después de completar la compra
        else:
            await message.answer("Por favor, ingresa una cantidad válida de capital.")
            return
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")
