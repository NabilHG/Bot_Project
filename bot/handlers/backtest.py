from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold
from bot import config
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime
import aiohttp
import asyncio
import os
import json
import subprocess
import time
import pandas as pd
import math 

router = Router()


async def load_data(base_path, subfolder_name):
    data_list = []
    # Recorrer todas las subcarpetas del segundo nivel
    for year_folder in os.listdir(base_path):
        year_folder_path = os.path.join(base_path, year_folder)
        # Verificar si la carpeta del año es un directorio
        if os.path.isdir(year_folder_path):
            target_folder_path = os.path.join(year_folder_path, subfolder_name)
            # Verificar si la carpeta deseada existe dentro de la carpeta del año
            if os.path.isdir(target_folder_path):
                # Cargar todos los archivos JSON dentro de la carpeta deseada
                for filename in os.listdir(target_folder_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(target_folder_path, filename)
                        with open(file_path, "r") as file:
                            data = json.load(file)
                            data_list.append(data)
    
    return data_list


async def fetch_rsi(session, symbol, current_api_key_index, message=None):
    if await is_vpn_active():
        print("OKKKKKKKK")
    api_key = config.get_next_api_key(current_api_key_index)
    print(api_key, "KEY9090")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "RSI",
        "symbol": symbol,
        "interval": "daily",
        "time_period": 14,
        "series_type": "close",
        "apikey": api_key,
    }

    async with session.get(url, params=params) as response:
        if response.status == 200:
            try:
                data = await response.json()
                if not data:
                    await message.answer(
                        **Text(
                            "⚠️ Simbolo: ",
                            Bold(symbol),
                            " no encontrado ❗️❗️\n",
                            Bold("Backtest cancelado"),
                        ).as_kwargs()
                    )
                    return None
                # print(data, "ESTO ES DATA")
                return data
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return None
        else:
            await message.answer(
                **Text(
                    "❌ Error al intentar obtener información de: ",
                    Bold(symbol),
                    f"\n 🚩 {response.status} 🚩",
                ).as_kwargs()
            )
            return None


async def contains_info(responses, substring):
    if isinstance(responses, dict):
        for key, value in responses.items():
            if await contains_info(value, substring):
                return True
    elif isinstance(responses, list):
        for item in responses:
            if await contains_info(item, substring):
                return True
    elif isinstance(responses, str):
        if substring in responses:
            return True
    return False

async def get_public_ip():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.ipify.org') as response:
            return await response.text()


async def get_monthly_alerts_counts(symbols, message, current_api_key_index, current_vpn_server_index):
    monthly_action_counts = {}  

    print(symbols)
    # if not await is_vpn_active():
    #     print("NOOO")
    #     await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))
    # else:
    #     print("SIII")

    # async with aiohttp.ClientSession() as session:
        # tasks = [
        #     fetch_rsi(
        #         session,
        #         symbol,
        #         current_api_key_index,
        #         message,
        #     )
        #     for symbol in symbols
        # ]
        # responses = await asyncio.gather(*tasks)

        # substring = "rate limit is 25 requests per day"
        # if await contains_info(responses, substring):
        #     print("CONTAINS")
        #     if await is_vpn_active():
        #         await desactivate_vpn()
            
        #     # change api key and vpn server
        #     current_api_key_index += 1
        #     current_vpn_server_index += 1

        #     await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))       
            
        #     #call recursively 
        #     counts, nested_responses = await get_monthly_alerts_counts(symbols, message, current_api_key_index, current_vpn_server_index)
        #     # counts, nested_responses = await get_monthly_alerts_counts(symbols, message, current_api_key_index, current_vpn_server_index)
        #     #update
        #     monthly_action_counts.update(counts)
        # else:
        #     print("NOT CONTAINS")
        #     if await is_vpn_active():
        #         await desactivate_vpn()        

          

        #responses has all the data about RSI
    responses = await load_data('data', 'rsi')
    
    has_none = any(filter(lambda x: x is None, responses))  # Si es True, no calcular el backtest
    print(has_none, "has_none")
    if not has_none:
        print("Calculating backtest")

        for symbol, data in zip(symbols, responses):
            if data and "Technical Analysis: RSI" in data:
                rsi_data = data["Technical Analysis: RSI"]
                for date, details in rsi_data.items():
                    month = date.split("-")[1]
                    if month not in monthly_action_counts:
                        monthly_action_counts[month] = {
                            "RSI below 25": 0,
                        }
                    if float(details["RSI"]) <= 25:
                        monthly_action_counts[month]["RSI below 25"] += 1

    # print(monthly_action_counts, "HERE")

    return monthly_action_counts, responses


async def activate_vpn(config_path):
    print(config_path)
    original_ip = await get_public_ip()
    print(original_ip, "IP1")
    
    try:
        cmd = f'sudo openvpn --config {config_path} --log /var/log/openvpn.log'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while True:
            if await is_vpn_active():
                print(f"VPN activated, exiting while loop: {config_path}")
                break
            else:
                await asyncio.sleep(1)
        
        await asyncio.sleep(5)
        
        vpn_ip = await get_public_ip()
        print(vpn_ip, "IP2")
        
        if original_ip == vpn_ip:
            print("VPN IP and original IP are the same. Something went wrong.")
        else:
            print("VPN activated successfully and IP has changed.")

    except subprocess.CalledProcessError as ex:
        print(f'Error while activating VPN: {ex}')

async def desactivate_vpn():
    try:
        cmd = 'sudo pkill openvpn'
                
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        while True:
            if await is_vpn_active():
                break
            else:
                await asyncio.sleep(1)
        print("VPN desactivated")
    except subprocess.CalledProcessError as ex:
        print(f'Error while desactivating vpn: {ex}')

async def is_vpn_active():
    try:
        result = await asyncio.create_subprocess_shell(
            "ip link",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await result.communicate()
        
        stdout_decoded = stdout.decode()
        stderr_decoded = stderr.decode()

        print(f"stderr: {stderr_decoded}")
        # print(f"stdout: {stdout_decoded}")

        if any("tun" in line and "UP" in line for line in stdout_decoded.splitlines()):
            print("VPN is active")
            return True
        else:
            print("VPN is not active")
            return False
        
    except asyncio.CancelledError:
        raise
    except Exception as ex:
        print(f'Error while checking VPN state: {ex}')
        return False

async def calculate_month_diff(begin_date):

    ancient_date = datetime.strptime(f"{begin_date}", "%Y-%m-%d")

    current_date = datetime.now()

    delta = relativedelta(current_date, ancient_date)

    total_months = delta.years * 12 + delta.months

    return total_months


async def calculate_monthly_avg_alerts(data):
    print(data, "DATA")
    result = {}
    if data:
        total_actions_rsi_below_25 = sum(
            entry["RSI below 25"] for entry in data.values()
        )

        total_months = await calculate_month_diff('2000-01-03')

        average_rsi_below_25 = round(total_actions_rsi_below_25 / total_months, 2)

        result = {
            "avg_below_25": average_rsi_below_25,
        }

        print(f'Media de alertas de compra: {result}')
    return result


async def fetch_close_price(session, symbol, current_api_key_index, message=None):
    if await is_vpn_active():
        print("kooooooo")
    api_key = config.get_next_api_key(current_api_key_index)
    print(api_key, "KEY8080")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": api_key,
    }
    async with session.get(url, params=params) as response:
        if response.status == 200:
            try:
                data = await response.json()
                if not data:
                    await message.answer(
                        **Text(
                            "⚠️ Simbolo: ",
                            Bold(symbol),
                            " no encontrado ❗️❗️\n",
                            Bold("Backtest cancelado"),
                        ).as_kwargs()
                    )
                    return None
                # print(data, "ESTO ES DATA")
                return data
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return None
        else:
            await message.answer(
                **Text(
                    "❌ Error al intentar obtener información de: ",
                    Bold(symbol),
                    f"\n 🚩 {response.status} 🚩",
                ).as_kwargs()
            )
            return None


async def calculate_maximum_drawdown(symbols, message, data_rsi_raw, current_api_key_index, current_vpn_server_index):
    maximum_drawdown = {}
    print(symbols)
    # if not await is_vpn_active():
    #     print("NOOO")
    #     await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))
    # else:
    #     print("SIII")

    # async with aiohttp.ClientSession() as session:
        # tasks = [
        #     fetch_close_price(
        #         session,
        #         symbol,
        #         current_api_key_index,
        #         message,
        #     )
        #     for symbol in symbols
        # ]
        # responses = await asyncio.gather(*tasks)

        # print(responses)

        # substring = "rate limit is 25 requests per day"
         

        # if await contains_info(responses, substring):
        #     print("CONTAINS")
        #     if await is_vpn_active():
        #         await desactivate_vpn()
            
        #     # change api key and vpn server
        #     current_api_key_index += 1
        #     current_vpn_server_index += 1
        #     # call recursively 
        #     await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))        
        #     result = await calculate_maximum_drawdown(symbols, message, data_rsi_raw, current_api_key_index, current_vpn_server_index)
        #     if result:
        #         maximum_drawdown.update(result)
        # else:
        #     print("NOT CONTAINS")
        #     if await is_vpn_active():
        #         await desactivate_vpn()        
                            
        
        #responses has all the data about close_price
    responses = await load_data('data', 'close_price') 

    closing_prices = {}
    for response in responses:
        symbol = response["Meta Data"]["2. Symbol"]
        if symbol not in closing_prices:
            closing_prices[symbol] = {}

        for date, prices in response["Time Series (Daily)"].items():
            closing_prices[symbol][date] = {"close": prices["4. close"]}

    # print(closing_prices, "INTERESA")
    # print(data_rsi_raw, "a")
    # print(symbols, "A")
    rsi_data = {}
    # for data in data_rsi_raw:
    #     for date, rsi in data["Technical Analysis: RSI"].items():
    #         rsi_data[date] = rsi

    for data in data_rsi_raw:
        symbol = data["Meta Data"]["1: Symbol"]
        if symbol not in data_rsi_raw:
            rsi_data[symbol] = {}

        for date, rsi in data["Technical Analysis: RSI"].items():
            rsi_data[symbol][date] = rsi
    # print(rsi_data, "INTERESA 2")
    
    df = await get_dataframe(rsi_data, closing_prices)
    await calculate_drawdown_profit(df, symbols)

    return maximum_drawdown

async def get_dataframe(rsi_data, close_data):
    # with open('output.txt', 'w') as f:
    #     print(rsi_data, file=f)
    # with open('output2.txt', 'w') as f:
    #     print(closing_prices, file=f)
    # close_df = pd.DataFrame({k: {pd.to_datetime(date): float(v['close']) for date, v in val.items()} for k, val in closing_prices.items()}) 
    # # Convertir datos de RSI a DataFrame 
    # rsi_df = pd.DataFrame({k: {pd.to_datetime(date): float(v['RSI']) for date, v in val.items()} for k, val in rsi_data.items()}) 
    # # Renombrar las columnas de los DataFrames para diferenciarlas 
    # close_df = close_df.rename(columns=lambda x: f"{x}_Close") 
    # rsi_df = rsi_df.rename(columns=lambda x: f"{x}_RSI") 
    # # Unir los DataFrames en uno solo 
    # combined_df = pd.concat([close_df, rsi_df], axis=1) 
    # # Ordenar por fecha 
    # combined_df = combined_df.sort_index() 
    # print(combined_df, "DATAFRAME")
    data_tuples = []

    for empresa, fechas in rsi_data.items():
        for fecha, valores in fechas.items():
            rsi = float(valores['RSI'])
            close = float(close_data[empresa][fecha]['close']) if fecha in close_data[empresa] else None
            data_tuples.append((fecha, empresa, 'RSI', rsi))
            data_tuples.append((fecha, empresa, 'Close', close))

    # Crear un DataFrame a partir de las tuplas
    df = pd.DataFrame(data_tuples, columns=['Fecha', 'Empresa', 'Tipo', 'Valor'])

    # Convertir el DataFrame en uno con MultiIndex
    df.set_index(['Fecha', 'Empresa', 'Tipo'], inplace=True)

    df.index = df.index.set_levels(pd.to_datetime(df.index.levels[0]), level=0)    
    df = df.unstack(level='Tipo')
    df.sort_index(inplace=True)
    df_clear = df.dropna()
    # with open('output.txt', 'w') as f:
    #     print(df_clear, file=f)
    return df_clear


#ONCE A SHARE IS BUYED, WE CAN NOT BUY IT AGAIN UNTIL WE SELL IT?

async def calculate_drawdown_profit(df, symbols):
    # Inicializar el DataFrame para almacenar la fecha y el valor del portafolio
    df_portfolio_tracking = pd.DataFrame(columns=['Fecha', 'Portfolio Value'])

    # Inicializar otras variables necesarias para la simulación
    initial_cash = 1000
    cash = initial_cash
    portfolio = {ticker: 0 for ticker in df.index.get_level_values('Empresa').unique()}
    buy_prices = {ticker: None for ticker in portfolio.keys()}
    shares_buyed = []
    buy_notification = 0
    # Simular las operaciones
    for date, group in df.groupby(level='Fecha'):
        close_prices = {ticker: group.loc[(date, ticker), ('Valor', 'Close')] for ticker in portfolio.keys() if (date, ticker) in group.index}
        rsis = {ticker: group.loc[(date, ticker), ('Valor', 'RSI')] for ticker in portfolio.keys() if (date, ticker) in group.index}
        
        # Señales de compra y venta
        for ticker in portfolio.keys():
            if ticker in close_prices and ticker in rsis:
                if not math.isnan(rsis[ticker]) and not math.isnan(close_prices[ticker]):
                    if rsis[ticker] < 25 and cash > 0:
                        buy_notification += 1
                        shares_to_buy = (cash / len(portfolio.keys())) // close_prices[ticker]
                        if shares_to_buy > 0 and ticker not in shares_buyed:
                            cash -= shares_to_buy * close_prices[ticker]
                            portfolio[ticker] += shares_to_buy
                            buy_prices[ticker] = close_prices[ticker]
                            shares_buyed.append(ticker)
                    elif rsis[ticker] > 70 and portfolio[ticker] > 0 and ticker in shares_buyed:
                        cash += portfolio[ticker] * close_prices[ticker]
                        portfolio[ticker] = 0
                        buy_prices[ticker] = None
                        shares_buyed.remove(ticker)
                    elif buy_prices[ticker] is not None and close_prices[ticker] < buy_prices[ticker] * 0.9 and ticker in shares_buyed:
                        cash += portfolio[ticker] * close_prices[ticker]
                        portfolio[ticker] = 0
                        buy_prices[ticker] = None
                        shares_buyed.remove(ticker)

        # Valor actual de la cartera en cada paso
        current_value = cash + sum(portfolio[ticker] * close_prices[ticker] for ticker in portfolio.keys() if ticker in close_prices)
        
        # Crear un DataFrame temporal con la fecha y el valor del portafolio
        temp_df = pd.DataFrame({'Fecha': [date], 'Portfolio Value': [current_value]}).dropna(how='all', axis=1)
        # temp_df_cleaned = temp_df.dropna(how='all', axis=1)
        # Concatenar el DataFrame temporal al DataFrame de seguimiento
        df_portfolio_tracking = pd.concat([df_portfolio_tracking, temp_df], ignore_index=True)

    # Finalmente, puedes visualizar el DataFrame o utilizarlo para cálculos adicionales
    print(df_portfolio_tracking, "kek")
    # with open('output.txt', 'w') as f:
    #     print(df_portfolio_tracking, file=f)

    # Calcular max drawdown y rentabilidad
    df_portfolio_tracking['Peak'] = df_portfolio_tracking['Portfolio Value'].cummax()
    df_portfolio_tracking['Drawdown'] = df_portfolio_tracking['Portfolio Value'] - df_portfolio_tracking['Peak']
    df_portfolio_tracking['Drawdown Percent'] = df_portfolio_tracking['Drawdown'] / df_portfolio_tracking['Peak']

    # Maximum drawdown
    max_drawdown = df_portfolio_tracking['Drawdown Percent'].min()

    # Rentabilidad del portafolio
    final_portfolio_value = df_portfolio_tracking['Portfolio Value'].iloc[-1]
    profitability = (final_portfolio_value - initial_cash) / initial_cash * 100

    print(f'Maximum Drawdown: {max_drawdown * 100:.2f}%')
    print(f'Profitability: {profitability:.2f}%')
    total_months = await calculate_month_diff('2000-01-03')
    print(f'Cantidad de alertas: {buy_notification}, meses totales: {total_months}, media: {buy_notification/total_months}')
    # print(f'Media de alertas de compra: {var_A/60}')


current_api_key_index = 0
current_vpn_server_index = 0

@router.message(Command(commands=["backtest", "BACKTEST", "Backtest", "BackTest"]))
async def backtest_handler(message: Message):
    # getting all the symbols to do the backtest
    # Split the message text to separate the command and the arguments
    args = message.text.split(maxsplit=1)

    # Check if arguments are provided
    # if len(args) < 2:
    #     await message.answer(
    #         **Text(
    #             "Por favor, proporciona los ",
    #             Bold("símbolos"),
    #             " de las empresas.\nEjemplo: /backtest AAPL, GOOG, MSFT, IBM, META o /backtest AAPL GOOG MSFT IBM META",
    #         ).as_kwargs()
    #     )
    #     return
    
    # Process the arguments to handle both comma and space-separated symbols
    # raw_symbols = args[1].replace(",", " ").split()
    # symbols = [symbol.strip().upper() for symbol in raw_symbols]
    symbols = ['INTC', 'GOOG', 'AMZN', 'ASML', 'PFE', 'TSLA', 'XOM', 'PG', 'SHEL', 
                'TM', 'JNJ', 'META', 'GE', 'TSM', 'C', 'BRK.B', 'CSCO', 'WFC', 
                'AAPL', 'NOK', 'MSFT', 'BP', 'BABA', 'IBM', 'NVS', 'BAC', 'WMT']
    if not symbols:
        await message.answer(
            **Text("No se han proporcionado símbolos válidos.").as_kwargs()
        )
        return
    
    data, data_rsi_raw = await get_monthly_alerts_counts(symbols, message, current_api_key_index, current_vpn_server_index)
    result_avg_alerts = await calculate_monthly_avg_alerts(data)
    print(current_vpn_server_index, "<---")
    a = await calculate_maximum_drawdown(symbols, message, data_rsi_raw, current_api_key_index, current_vpn_server_index)
    print(a, "AAAAAAA") 
    # print(result_avg_alerts)
    result_avg_alerts = '' #Temporal
    if result_avg_alerts:
        symb_msg = ", ".join(symbols)
        await message.answer(
            **Text(
                f"🧪BackTest\nEmpresas analizadas: {symb_msg}🧪",
                "\n🧮 Media de alertas mensuales: \n" "🔹 Compra: ",
                Bold(result_avg_alerts["avg_below_25"]),
            ).as_kwargs()
        )
    return


"""
    iterate through all symbols, for each one, execute backtest
    backtest: 
      ✅-avarage number of actions monthly, when rsi is lower than 25 (rsi < 25), or rsi is higher than 70 (rsi > 70), that's an action
      -maximum drawdown
      -profit yearly 
"""
