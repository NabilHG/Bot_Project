from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from bot.config import TORTOISE_ORM, MATRIX
from bot.db import models
from datetime import datetime
from tortoise import Tortoise
from bot.analysis import latest_close_price

router = Router()
class ProccesSellForm(StatesGroup):
    amount = State()

async def proccess_sell(id, message, capital, ticker):
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

    latest_close_price_value = round(await latest_close_price(ticker, 'data'), 2)

    operation_open = await models.Operation.filter(ticker=ticker, status="open", wallet_id=wallet.id).first()


    operation_open.status= 'close'
    operation_open.sell_date = datetime.now()
    operation_open.capital_retrived = capital


    await models.WalletShare.filter(wallet=wallet.id, share=share.id).delete()

    # Guardar los cambios en la base de datos
    try:
        await operation_open.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

    '''TODO'''
    #Calculate gain/loss percent and how this operations impacted to the wallet (recalculate profit and max drawdown)

    operation_value = operation_open.capital_retrived - operation_open.capital_invested

    # Calculando el porcentaje obtenido
    percentage_obtained = (operation_value / operation_open.capital_retrived) * 100
    await message.answer(f"✅ <b>Venta guardada:</b>\n <b>{ticker}</b>, con precio de cierre <b>{latest_close_price_value}€</b>.\nResuletado de la operación <b>{percentage_obtained}%</b>", parse_mode='HTML')

    return

@router.message(Command(commands=["vender"]))
async def ask_to_sell_handler(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    
    if not len(args) > 1:
        await message.reply("Por favor, proporciona un valor después del comando.")
        return

    ticker = args[1].upper()
    if args[0] == "/vender" and ticker in MATRIX[max(MATRIX.keys())]:
        # Guardar el valor en el FSMContext
        await state.update_data(ticker=ticker)

        await message.answer("¿Qué cantidad deseas vender?")
        await state.set_state(ProccesSellForm.amount)

@router.message(Command(commands=["rechazar"]), ProccesSellForm.amount)
async def cancel_sell_handler(message: Message, state: FSMContext):
    await message.answer("Operación cancelada.")
    await state.clear()  # Limpiar el estado para cancelar la operación

@router.message(ProccesSellForm.amount)
async def ask_amount_to_sell(message: Message, state: FSMContext):
    id = message.from_user.id
    user_data = await state.get_data()
    ticker = user_data.get("ticker")  # Obtener el valor

    try:
        capital = float(message.text)
        if capital > 0:
            await proccess_sell(id, message, capital, ticker)
            await state.clear()  # Limpiar el estado después de completar la compra
        else:
            await message.answer("Por favor, ingresa una cantidad válida de capital.")
            return
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")

