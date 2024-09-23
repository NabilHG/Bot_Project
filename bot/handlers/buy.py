import os
import json
from aiogram import Router, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
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
    confirm = State()

# Teclado para confirmar compra
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Sí")],
        [KeyboardButton(text="No")],
    ],
    resize_keyboard=True
)

# Función para generar el teclado con las empresas
async def get_companies_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    row = []  # Inicializa una fila vacía

    for company in MATRIX[max(MATRIX.keys())]:  # Reemplaza esto con tu lógica para obtener empresas
        button = InlineKeyboardButton(text=company, callback_data=f"company_buy:{company}")
        row.append(button)  # Añade el botón a la fila

        # Si la fila tiene 3 botones, añádela al teclado y reinicia la fila
        if len(row) == 3:
            keyboard.inline_keyboard.append(row)
            row = []

    # Si quedan botones en la fila después del bucle, añádelos al teclado
    if row:
        keyboard.inline_keyboard.append(row)

    return keyboard

async def proccess_buy(message, capital, state):
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

        wallet_share = await models.WalletShare.create(wallet=wallet, share=share)
        wallet.current_capital = wallet.current_capital - capital
        wallet.gain_capital = wallet.gain_capital - capital
        wallet.number_of_operations += 1

        # Guardar los cambios en la base de datos
        await operation.save()
        await wallet_share.save()
        await wallet.save()

        await message.answer(
            f"✅ <b>Compra guardada:</b>\n <b>{share.ticker}</b>, con precio de cierre <b>{purchased_price}€</b> y capital invertido <b>{capital}€</b>",
            reply_markup=types.ReplyKeyboardRemove(), parse_mode='HTML'
        )
    except IntegrityError as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

@router.message(Command(commands=["cancelar"]), ProccesBuyForm.amount)
async def cancel_buy_handler(message: Message, state: FSMContext):
    await message.answer("Operación cancelada.")
    await state.clear()  # Limpiar el estado para cancelar la operación

@router.message(Command(commands=["comprar"]))
async def ask_to_buy_handler(message: Message, state: FSMContext):
    # Mostrar el teclado con la lista de empresas disponibles
    keyboard = await get_companies_keyboard()
    await message.answer("Selecciona una empresa para comprar (para cancelar el registro /cancelar):", reply_markup=keyboard)

# Manejar la selección de una empresa desde el teclado inline
@router.callback_query(lambda c: c.data.startswith("company_buy:"))
async def process_company_selection(callback_query: CallbackQuery, state: FSMContext):
    ticker = callback_query.data.split(":")[1]  # Extraer el ticker seleccionado
    print(ticker)
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    id = callback_query.from_user.id
    try:
        user = await models.User.filter(id=id).first()
        wallet = await models.Wallet.filter(user_id=user.id).first()
        share = await models.Share.filter(ticker=ticker).first()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # Guardar el valor en el FSMContext
    await state.update_data(wallet=wallet)
    await state.update_data(share=share)

    await callback_query.message.answer(f"Has seleccionado {ticker}. ¿Qué cantidad deseas invertir de €? (Solo números)")
    await state.set_state(ProccesBuyForm.amount)
    await callback_query.answer()  # Cerrar el callback query

@router.message(ProccesBuyForm.amount)
async def ask_amount_to_buy(message: Message, state: FSMContext):
    data = await state.get_data()
    wallet = data.get("wallet")
    share = data.get("share")
    try:
        capital = float(message.text)
        if capital > 0:
            if wallet.current_capital >= capital:
                await message.answer("¿Estás seguro de realizar la compra?", reply_markup=keyboard)
                await state.update_data(capital=capital)
                await state.set_state(ProccesBuyForm.confirm)
            else:
                msg = (f"Por favor, ingresa una cantidad <b>menor o igual</b> al capital actual de {wallet.current_capital}€\n" +
                       f"Para comprar, vuelve a iniciar el proceso con <b>/comprar {share.ticker}</b> o actualiza el capital actual con <b>/actualizar</b>")
                await message.answer(msg, parse_mode='HTML')
                await state.clear()
                return
        else:
            await message.answer("Por favor, ingresa una cantidad válida de capital.")
            return
    except ValueError:
        await message.answer("Por favor, ingresa una cantidad válida de capital.")

@router.message(ProccesBuyForm.confirm)
async def confim_to_sell(message: Message, state: FSMContext):
    data = await state.get_data()
    capital = data.get("capital")
    response = message.text.lower()
    if response in ["si", "sí"]:
        await proccess_buy(message, capital, state)
        await state.clear()  # Limpiar el estado después de completar la compra
    else:
        await message.answer("Operación cancelada.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()