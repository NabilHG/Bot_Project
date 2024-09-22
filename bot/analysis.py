import os
import json
import asyncio
from tortoise import Tortoise
from bot.config import TORTOISE_ORM, MATRIX
from bot.db import models
from datetime import datetime
from aiogram import Router

router = Router()

async def latest_close_price(ticker, base_dir):
    # Buscar el ticker en el último año disponible en la matriz
    for year in sorted(MATRIX.keys(), reverse=True):
        if ticker in MATRIX[year]:
            # Construir la ruta del archivo
            file_path = os.path.join(base_dir, year, 'close_price', f'{ticker}.json')
            
            # Verificar si el archivo existe
            if os.path.exists(file_path):
                # Cargar el archivo JSON
                with open(file_path, 'r') as file:
                    data = json.load(file)
                
                # Obtener los valores de 'CLOSE'
                close_data = data.get('CLOSE', {})
                if close_data:
                    # Devolver el último valor (el de la fecha más reciente)
                    last_date = max(close_data.keys())
                    return close_data[last_date]
                else:
                    print(f"No hay datos de 'CLOSE' para {ticker} en {year}")
    
    print(f"Ticker {ticker} no encontrado en ningún año")



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

async def analyze_user_tickers(user, tickers, data_to_analyze, bot):
    try:
        wallet = await models.Wallet.filter(user=user).first()
        if not wallet:
            print(f'No wallet found for user {user.id}')
            return
       
        print(f'Processing wallet for user {user.id} ({user.name}), wallet id: {wallet.id}')
        user_shares = {ws.share_id for ws in await models.WalletShare.filter(wallet=wallet.id)}
       
        for ticker in tickers:
            ticker_data = data_to_analyze.get(ticker, {})
            rsi_value = ticker_data.get('RSI')
            close_value = ticker_data.get('CLOSE')
            if not (rsi_value and close_value):
                print(f"Data missing for ticker {ticker}")
                continue

            print(f"Analyzing ticker: {ticker} for user: {user.id}")
           
            share = await models.Share.filter(ticker=ticker).first()
            if not share:
                print(f"No share data found for ticker {ticker}")
                continue
           
            operation_open = await models.Operation.filter(ticker=ticker, status="open", wallet_id=wallet.id).first()
            share_in_portfolio = share.id in user_shares

            # Verificar si hay operaciones abiertas y procesar
            if rsi_value <= 25 and not share_in_portfolio:
                capital_to_invest = wallet.current_capital
                if round(wallet.initial_capital * user.investor_profile, 2) < wallet.current_capital:
                    capital_to_invest = round(wallet.initial_capital * user.investor_profile, 2)
                   
                msg = (
                    '🚨 <b>Alerta de compra</b> 🚨\n\n' +
                    f'Ticker: <b>{share.ticker}</b>\n' +
                    f"Valor de Cierre: <b>{round(close_value, 2)}€</b>\n" +
                    f'Según tu perfil de inversor y el capital actual disponible, el bot sugiere una cantidad estimada para invertir: <b>{capital_to_invest}€</b>\n' + 
                    f'Esta sugerencia es <b>automática</b> y <b>no</b> constituye una recomendación de inversión.'
                )
                try:
                    await bot.send_message(user.id, msg, parse_mode='HTML')
                    await asyncio.sleep(0.2)  # Pausa mínima entre mensajes
                    await bot.send_message(user.id, f"¿Deseas realizar la compra? (/comprar <b>{ticker}</b> o /rechazar)", parse_mode='HTML')
                    await asyncio.sleep(0.2)  # Pausa mínima entre mensajes
                except Exception as e:
                    print(f"Error sending buy alert: {e}")
                   
            elif rsi_value >= 70 and share_in_portfolio:
                msg = (
                    '🚨 <b>Alerta de venta por beneficios</b> 🚨\n\n' +
                    f'Ticker: <b>{share.ticker}</b>\n' +
                    f"Valor de Cierre: <b>{round(close_value, 2)}€</b>"
                )
                try:
                    await bot.send_message(user.id, msg, parse_mode='HTML')
                    await asyncio.sleep(0.2)  # Pausa mínima entre mensajes
                    await bot.send_message(user.id, f"¿Deseas realizar la venta? (/vender <b>{ticker}</b> o /rechazar)", parse_mode='HTML')
                    await asyncio.sleep(0.2)  # Pausa mínima entre mensajes
                except Exception as e:
                    print(f"Error sending sell alert: {e}")

            if operation_open:
                past_close_value = operation_open.purchased_price
                if past_close_value  * 0.9 > close_value and share_in_portfolio:
                    msg = (
                    '🚨 <b>Alerta de venta por pérdidas</b> 🚨\n\n' +
                    f'Ticker: <b>{share.ticker}</b>\n' +
                    f"Valor de Cierre: <b>{round(close_value, 2)}€</b>"
                    )
                    try:
                        await bot.send_message(user.id, msg, parse_mode='HTML')
                        await asyncio.sleep(0.2)  # Pausa mínima entre mensajes
                        await bot.send_message(user.id, f"¿Deseas realizar la venta? (/vender <b>{ticker}</b> o /rechazar)", parse_mode='HTML')
                        await asyncio.sleep(0.2)  # Pausa mínima entre mensajes

                    except Exception as e:
                        print(f"Error sending sell alert: {e}")                    
           
    except Exception as e:
        print(f"Error processing user {user.id}: {e}")

async def analysis(bot):
    tickers = set(MATRIX[max(MATRIX.keys())])  # Obtener los tickers del último año
    data_to_analyze = await get_data()

    # Conecta la base de datos
    await Tortoise.init(TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)

    try:
        users = await models.User.all()  # Obtener todos los usuarios
    except Exception as e:
        print(f"Error fetching users: {e}")
        return

    # Procesar cada usuario en paralelo
    tasks = [analyze_user_tickers(user, tickers, data_to_analyze, bot) for user in users]
    await asyncio.gather(*tasks)