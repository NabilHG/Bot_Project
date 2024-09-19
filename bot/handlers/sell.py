from aiogram import Router, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
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
    confirm = State()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Sí")],
        [KeyboardButton(text="No")],
    ],
    resize_keyboard=True
)

async def proccess_sell(message, capital, state):
    data = await state.get_data()
    wallet = data.get("wallet")
    share = data.get("share")

    latest_close_price_value = round(await latest_close_price(share.ticker, 'data'), 2)

    operation_open = await models.Operation.filter(ticker=share.ticker, status="open", wallet_id=wallet.id).first()

    operation_open.status = 'close'
    operation_open.sell_date = datetime.now()
    operation_open.capital_retrived = capital

    await models.WalletShare.filter(wallet=wallet.id, share=share.id).delete()

    # Guardar los cambios en la base de datos
    try:
        await operation_open.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

    # Calculando el valor de la operación
    operation_value = operation_open.capital_retrived - operation_open.capital_invested
    print(f'Op value: {operation_open}, retrived: {operation_open.capital_retrived}, invested: {operation_open.capital_invested}')
    # Calculando el porcentaje obtenido para esta operación (aunque no lo necesitemos para la cartera)
    percentage_obtained = round((operation_value / operation_open.capital_invested) * 100, 2)
    print(f'Op value: {percentage_obtained}')

    # Actualizar el capital actual de la cartera sumando el valor de la operación
    wallet.current_capital += operation_open.capital_retrived
    wallet.gain_capital += operation_open.capital_retrived

    # Calcular la nueva rentabilidad total (profit) en base al capital actual
    wallet.profit = ((wallet.gain_capital - wallet.initial_capital) / wallet.initial_capital) * 100
    print(f'profit: {wallet.profit}')
    # Actualizar el capital más alto alcanzado (peak_capital)
    if wallet.peak_capital is None or wallet.gain_capital > wallet.peak_capital:
        wallet.peak_capital = wallet.gain_capital

    # Calculando el drawdown en base al peak_capital
    drawdown = ((wallet.peak_capital - wallet.gain_capital) / wallet.peak_capital) * 100
    print("drawdown", drawdown)
    print("max", max(wallet.max_drawdown or 0, drawdown))
    wallet.max_drawdown = max(wallet.max_drawdown or 0, drawdown)  # Guardar el mayor drawdown registrado

    # Guardar los cambios en la cartera
    try:
        await wallet.save()
    except Exception as db_error:
        print(f"Error al actualizar la cartera: {db_error}")

    await message.answer(f"✅ <b>Venta guardada:</b>\n <b>{share.ticker}</b>, con precio de cierre <b>{latest_close_price_value}€</b>.\nResultado de la operación <b>{percentage_obtained}%</b>", reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')

    return

@router.message(Command(commands=["rechazar"]), ProccesSellForm.amount)
async def cancel_sell_handler(message: Message, state: FSMContext):
    await message.answer("Operación cancelada.")
    await state.clear()  # Limpiar el estado para cancelar la operación

@router.message(Command(commands=["vender"]))
async def ask_to_sell_handler(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    
    if not len(args) > 1:
        await message.reply("Por favor, proporciona un valor después del comando.")
        return
    ticker = args[1].upper()
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
        operation_open = await models.Operation.filter(ticker=ticker, status="open", wallet_id=wallet.id).first()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
    

    if args[0] == "/vender":
        # Guardar el valor en el FSMContext
        await state.update_data(wallet=wallet)
        await state.update_data(share=share)
        await state.update_data(operation=operation_open)

        await message.answer("¿Qué cantidad deseas vender?")
        await state.set_state(ProccesSellForm.amount)

@router.message(ProccesSellForm.amount)
async def ask_amount_to_sell(message: Message, state: FSMContext):
    data = await state.get_data()
    wallet = data.get("wallet")
    try:
        capital = float(message.text)
        if capital > 0:
            await message.answer("Estas seguro de realizar la venta?", reply_markup=keyboard)
            await state.update_data(capital=capital)
            await state.set_state(ProccesSellForm.confirm)
        else:
            await message.answer("Por favor, ingresa una cantidad válida de capital.")
            return
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")

@router.message(ProccesSellForm.confirm)
async def confim_to_sell(message: Message, state: FSMContext):
    data = await state.get_data()
    capital = data.get("capital")
    response = message.text.lower()
    print(response)
    if response in ["si", "sí"]:
        await proccess_sell(message, capital, state)
        await state.clear()  # Limpiar el estado después de completar la compra
    else:
        await message.answer("Operación cancelada.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
