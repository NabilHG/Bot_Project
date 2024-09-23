from aiogram import Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.config import TORTOISE_ORM, MATRIX
from bot.db import models
from datetime import datetime
from tortoise import Tortoise
from bot.analysis import latest_close_price

router = Router()

class ProccesSellForm(StatesGroup):
    amount = State()
    confirm = State()


keyboard_Yes_No = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Sí")],
        [KeyboardButton(text="No")],
    ],
    resize_keyboard=True
)
def get_companies_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    row = []

    for company in MATRIX[max(MATRIX.keys())]:  # Obtener las empresas desde MATRIX
        button = InlineKeyboardButton(text=company, callback_data=f"company_sell:{company}")
        row.append(button)

        # Añadir fila cada 5 botones
        if len(row) == 3:
            keyboard.inline_keyboard.append(row)
            row = []

    # Añadir cualquier botón restante
    if row:
        keyboard.inline_keyboard.append(row)

    return keyboard

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

    try:
        await operation_open.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

    operation_value = operation_open.capital_retrived - operation_open.capital_invested
    percentage_obtained = round((operation_value / operation_open.capital_invested) * 100, 2)

    wallet.current_capital += operation_open.capital_retrived
    wallet.gain_capital += operation_open.capital_retrived

    wallet.profit = ((wallet.gain_capital - wallet.initial_capital) / wallet.initial_capital) * 100

    if wallet.peak_capital is None or wallet.gain_capital > wallet.peak_capital:
        wallet.peak_capital = wallet.gain_capital

    drawdown = ((wallet.peak_capital - wallet.gain_capital) / wallet.peak_capital) * 100
    wallet.max_drawdown = max(wallet.max_drawdown or 0, drawdown)

    try:
        await wallet.save()
    except Exception as db_error:
        print(f"Error al actualizar la cartera: {db_error}")

    await message.answer(f"✅ <b>Venta guardada:</b>\n <b>{share.ticker}</b>, con precio de cierre <b>{latest_close_price_value}€</b>.\nResultado de la operación <b>{percentage_obtained}%</b>", reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML')

@router.message(Command(commands=["cancelar"]), ProccesSellForm.amount)
async def cancel_sell_handler(message: Message, state: FSMContext):
    await message.answer("Operación cancelada.")
    await state.clear()  # Limpiar el estado para cancelar la operación

@router.message(Command(commands=["vender"]))
async def ask_to_sell_handler(message: Message, state: FSMContext):
    await message.answer("Selecciona una empresa para vender (para cancelar el registro /cancelar):", reply_markup=get_companies_keyboard())

@router.callback_query(lambda c: c.data.startswith("company_sell:"))
async def process_company_selection(callback_query: types.CallbackQuery, state: FSMContext):
    company = callback_query.data.split(":")[1]
    await callback_query.answer()  # Acknowledge the callback
    id = callback_query.from_user.id

    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    try:
        user = await models.User.filter(id=id).first()  
        wallet = await models.Wallet.filter(user_id=user.id).first()
        share = await models.Share.filter(ticker=company).first()
        operation_open = await models.Operation.filter(ticker=company, status="open", wallet_id=wallet.id).first()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    if share and operation_open:
        await state.update_data(wallet=wallet)
        await state.update_data(share=share)
        await state.update_data(operation=operation_open)

        await callback_query.message.answer("¿Qué cantidad deseas vender?(Solo números)")
        await state.set_state(ProccesSellForm.amount)
    else:
        await callback_query.message.answer("No tienes operaciones abiertas para esta empresa.")

@router.message(ProccesSellForm.amount)
async def ask_amount_to_sell(message: Message, state: FSMContext):
    data = await state.get_data()
    wallet = data.get("wallet")
    try:
        capital = float(message.text)
        if capital > 0:
            await message.answer("¿Estás seguro de realizar la venta?", reply_markup=keyboard_Yes_No)
            await state.update_data(capital=capital)
            await state.set_state(ProccesSellForm.confirm)
        else:
            await message.answer("Por favor, ingresa una cantidad válida de capital.")
            return
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")

@router.message(ProccesSellForm.confirm)
async def confim_to_sell(message: Message, state: FSMContext):
    print("holaa")
    data = await state.get_data()
    capital = data.get("capital")
    response = message.text.lower()
    if response in ["si", "sí"]:
        await proccess_sell(message, capital, state)
        await state.clear()  # Limpiar el estado después de completar la venta
    else:
        await message.answer("Operación cancelada.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()