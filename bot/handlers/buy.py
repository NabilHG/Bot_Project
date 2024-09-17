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


async def proccess_buy(id, message, capital, state):

    data = await state.get_data()
    wallet = data.get("wallet")  
    share = data.get("share")  

    purchased_price = round(await latest_close_price(share.ticker, 'data'), 2)

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
        await message.answer(f"✅ <b>Compra guardada:</b>\n <b>{share.ticker}</b>, con precio de cierre <b>{purchased_price}€</b> y capital invertido <b>{capital}€</b>", parse_mode='HTML')
    except IntegrityError as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

@router.message(Command(commands=["rechazar"]), ProccesBuyForm.amount)
async def cancel_buy_handler(message: Message, state: FSMContext):
    await message.answer("Operación cancelada.")
    await state.clear()  # Limpiar el estado para cancelar la operación

@router.message(Command(commands=["comprar"]))
async def ask_to_buy_handler(message: Message, state: FSMContext):

    args = message.text.split(maxsplit=1)
    
    if not len(args) > 1:
        await message.reply("Por favor, proporciona un ticker después del comando.")
        return
    if not ticker in MATRIX[max(MATRIX.keys())]:
        await message.reply("Por favor, proporciona un ticker correcto.")
        return
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    id = message.from_user.id
    try:
        user = await models.User.filter(id=id).first()  
        wallet = await models.Wallet.filter(user_id=user.id).first()
        share = await models.Share.filter(ticker=ticker).first()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    ticker = args[1].upper()
    if args[0] == "/comprar":
        # Guardar el valor en el FSMContext
        await state.update_data(wallet=wallet)
        await state.update_data(share=share)

        await message.answer("¿Qué cantidad deseas invertir?")
        await state.set_state(ProccesBuyForm.amount)

@router.message(ProccesBuyForm.amount)
async def ask_amount_to_buy(message: Message, state: FSMContext):
    data = await state.get_data()
    wallet = data.get("wallet")  

    try:
        capital = float(message.text)
        if capital > 0:
            if wallet.current_capital >= capital:
                await proccess_buy(message, capital, state)
                await state.clear()  # Limpiar el estado después de completar la compra
            else:
                await message.answer("Por favor, ingresa una cantidad <b>menor o igual</b> al capital actual.\nPara comprar, primero actualiza el capital inicial en <b>/actualizar</b>", parse_mode='HTML')
                return
        else:
            await message.answer("Por favor, ingresa una cantidad válida de capital.")
            return
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")
