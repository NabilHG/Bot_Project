import os
import json
from tortoise import Tortoise
from tortoise.exceptions import IntegrityError
from bot import config
from bot.config import TORTOISE_ORM, MATRIX
from bot.db import models
from datetime import datetime
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()
async def load_data_to_analize(base_path, subfolder_name, type):
    data_dict = {}
    last_year = max(MATRIX.keys())  # Obtener el último año disponible
    target_tickers = set(MATRIX[last_year])  # Obtener los tickers del último año

    # Recorrer todas las subcarpetas del segundo nivel
    for year_folder in os.listdir(base_path):
        year_folder_path = os.path.join(base_path, year_folder)
        
        # Verificar si la carpeta del año es un directorio y corresponde al último año
        if os.path.isdir(year_folder_path) and year_folder == last_year:
            target_folder_path = os.path.join(year_folder_path, subfolder_name)
            
            # Verificar si la carpeta deseada existe dentro de la carpeta del año
            if os.path.isdir(target_folder_path):
                
                # Cargar todos los archivos JSON dentro de la carpeta deseada
                for filename in os.listdir(target_folder_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(target_folder_path, filename)
                        
                        with open(file_path, "r") as file:
                            data = json.load(file)
                            
                            # Obtener el símbolo (ticker) del archivo
                            symbol = data.get("Symbol", "")
                            
                            # Verificar si el ticker está en la lista del último año
                            if symbol in target_tickers and type in data:
                                # Obtener las fechas y sus valores
                                date_values = data[type]
                                
                                # Ordenar las fechas y obtener la última
                                if date_values:
                                    last_date = max(date_values, key=lambda date: datetime.strptime(date, "%Y-%m-%d"))
                                    last_value = date_values[last_date]
                                    
                                    # Añadir el último valor al diccionario
                                    data_dict[symbol] = {last_date: last_value}
    
    return data_dict

async def get_data():
    combined_data = {}
    data_close_price = await load_data_to_analize("data", "close_price", "CLOSE")
    data_close_rsi = await load_data_to_analize("data", "rsi", "RSI")

    for ticker, close_data in data_close_price.items():
        close_date, close_value = list(close_data.items())[0]

        combined_data[ticker] = {'CLOSE': close_value}

        if ticker in data_close_rsi:
            rsi_data = data_close_rsi[ticker]
            rsi_date, rsi_value = list(rsi_data.items())[0] 

            combined_data[ticker]['RSI'] = rsi_value

    return combined_data

# async def send_buy_alert(bot, wallet, ticker, close_value):
#     user_id = 7257826638
#     # user_id = user.id

#     msg = '🚨 <b>Alerta de Compra</b> 🚨\n\n' + f'Ticker: <b>{ticker}</b>\n' + f"Valor de Cierre: <b>{round(close_value,2)}</b>"

#     try:
#         await bot.send_message(user_id, msg, parse_mode='HTML')
#     except Exception as e:
#         print(f"Ocurrió un error al intentar enviar el mensaje: {e}")
#     capital_invested = 1
#     operation = await models.Operation.create(ticker=ticker,status='open', buy_date=datetime.now(), capital_invested=capital_invested, wallet_id=wallet.id)

#     '''TODO
#         Establish relationship wallet-share
#     '''

#     # Guardar los cambios en la base de datos
#     try:
#         await operation.save()
#     except Exception as db_error:
#         print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

#     return

class BuyProcess(StatesGroup):
    ask_to_buy = State()  
    ask_amount = State() 


yes_no_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Sí"), KeyboardButton(text="No")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Función para enviar la alerta de compra y preguntar si desea comprar
async def send_buy_alert(bot, state: FSMContext, user, wallet, share, close_value):
    user_id = user.id
    # Enviar alerta de compra
    msg = (
        '🚨 <b>Alerta de Compra</b> 🚨\n\n' +
        f'Ticker: <b>{share.ticker}</b>\n' +
        f"Valor de Cierre: <b>{round(close_value, 2)}</b>"
    )
    try:
        await bot.send_message(user_id, msg, parse_mode='HTML')
        await bot.send_message(user_id, "¿Deseas realizar la compra?", reply_markup=yes_no_keyboard)
        print("QAA")
        await state.set_state(BuyProcess.ask_to_buy)
        print(f"Estado cambiado a {BuyProcess.ask_to_buy}")
    except Exception as e:
        print(f"Ocurrió un error al intentar enviar el mensaje: {e}")
        await state.clear()
        return

# Manejar la respuesta a la pregunta de si desea comprar
@router.message(BuyProcess.ask_to_buy)
async def ask_to_buy(message: Message, state: FSMContext):
    print("res")
    response = message.text.lower()
    print(f'REsponse: {response}')
    if response in ['sí', 'si']:
        # Preguntar la cantidad a invertir
        await message.answer("¿Qué cantidad deseas invertir?")
        await state.set_state(BuyProcess.ask_amount)
    elif response == 'no':
        await message.answer("Operación cancelada.")
        await state.clear()  # Resetear el estado
    else:
        await message.answer("Respuesta inválida. Por favor, responde con 'Sí' o 'No'.")
        return

# Manejar la respuesta de la cantidad a invertir
@router.message(BuyProcess.ask_amount)
async def ask_amount(message: Message, state: FSMContext, bot, user, wallet, share, close_value):
    try:
        capital_invested = float(message.text)
        if capital_invested <= 0:
            await message.answer("La cantidad debe ser mayor a 0.")
            await state.clear()
            return
    except ValueError:
        await message.answer("Respuesta no válida.")
        await state.clear()
        return

    # Guardar la compra en la base de datos
    try:
        operation = await models.Operation.create(
            ticker=share.ticker,
            status='open',
            buy_date=datetime.now(),
            capital_invested=capital_invested,
            wallet_id=wallet.id
        )

        wallet_share = await models.WalletShare.create(
            wallet=wallet.id,
            share=share.id
        )

        # Guardar los cambios en la base de datos
        await operation.save()
        await wallet_share.save()
        await message.answer("Proceso guardado.")
    except IntegrityError as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

    await state.clear()







async def send_sell_alert(bot, state, user, wallet, share, close_value, operation_open, type):
    user_id = 7257826638
    # user_id = user.id

    text = 'Alerta de Venta por pérdidas'
    if type == 'gain':
        text = 'Alerta de Venta por con beneficios'

    msg = f'🚨 <b>{text}</b> 🚨\n\n' + f'Ticker: <b>{share.ticker}</b>\n' + f"Valor de Cierre: <b>{round(close_value,2)}</b>"

    try:
        await bot.send_message(user_id, msg, parse_mode='HTML')
    except Exception as e:
        print(f"Ocurrió un error al intentar enviar el mensaje: {e}")
    
    operation_open.status= 'close'
    operation_open.sell_date = datetime.now()

    await models.WalletShare.filter(wallet=wallet.id, share=share.id).delete()

    # Guardar los cambios en la base de datos
    try:
        await operation_open.save()  
    except Exception as db_error:
        print(f"Ocurrió un error al guardar en la base de datos: {db_error}")

    return

async def analysis(bot, dp):
    print("Hello analysis")

    tickers = set(MATRIX[max(MATRIX.keys())])  # Obtener los tickers del último año
    data_to_analyze = await get_data()
    # print(data_to_analize)
    # Conecta la base de datos
    await Tortoise.init(TORTOISE_ORM)    
    # Borra y recrea las tablas (opcional, útil para reiniciar los datos)
    await Tortoise.generate_schemas(safe=True)
    try:  
        # retriving all users
        users = await models.User.all()  
    except Exception as e:
        print(f"Error fetching data: {e}")

    for user in users:
        # Crear FSMContext manualmente para el usuario
        bot_info = await bot.get_me()

        storage_key = StorageKey(bot_id=bot_info.id, chat_id=user.id, user_id=user.id)
        state = FSMContext(storage=dp.storage, key=storage_key)

        for ticker in tickers:
            ticker_data = data_to_analyze.get(ticker, {})
            rsi_value = ticker_data.get('RSI')
            close_value = ticker_data.get('CLOSE')
            print(ticker)
            
            wallet = await models.Wallet.filter(user=user).first()
            operation_open = await models.Operation.filter(ticker=ticker, status="open", wallet_id=wallet.id).first()
            a = await wallet.user
            print(f'Wallet from: {a.name}')
            print(f'Wallet id: {wallet.id}')
            share = await models.Share.filter(ticker=ticker).first()
            share_in_portfolio = await models.WalletShare.filter(wallet=wallet.id, share=share.id).exists()

            if operation_open:
                past_close_value = operation_open.capital_invested
                print(f'Operation: {operation_open.ticker}, past close price: {past_close_value}, status: {operation_open.status}')
                print(f'Current close: {close_value}')
                if past_close_value > close_value * 0.9 and share_in_portfolio:  # Verifica si el valor ha caído un 10%
                    print("sell loss")
                    # await send_sell_alert(bot, state, user, wallet, share, close_value, operation_open, "loss")             
            else:
                print("Not found") 

            if rsi_value <= 25 and not share_in_portfolio:
                print("buy")
                print(f'Share in portfolio: {share_in_portfolio}')   
                await send_buy_alert(bot, state, user, wallet, share, close_value)
            elif rsi_value >= 70 and share_in_portfolio:
                print("sell")
                await send_sell_alert(bot, state, user, wallet, share, close_value, operation_open, "gain")

        # Limpiar el estado después del análisis si es necesario
        await state.clear()
    
    return

    

    