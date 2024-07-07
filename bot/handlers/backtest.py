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


router = Router()


async def load_dummy_data():
    data_list = []
    # folder_path = '..\\..\\dummy_data'
    folder_path = r"C:\Users\Nabil\Desktop\bot_project\dummy_data"
    # print(folder_path)
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                data_list.append(data)

    return data_list


async def fetch_rsi(session, symbol, message, current_api_key_index):
    api_key = config.get_next_api_key(current_api_key_index)
    print(api_key, "KEY")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "RSI",
        "symbol": symbol,
        "interval": "daily",
        "time_period": 10,
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
    if not await is_vpn_active():
        print("NOOO")
        await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))
    else:
        print("SIII")

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_rsi(
                session,
                symbol,
                message,
                current_api_key_index,
            )
            for symbol in symbols
        ]
        responses = await asyncio.gather(*tasks)

        substring = "rate limit is 25 requests per day"
         
        if await contains_info(responses, substring):
            print("CONTAINS")
            if await is_vpn_active():
                # change api key and vpn server
                current_api_key_index += 1
                current_vpn_server_index +=1
                await desactivate_vpn()
                await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))
                counts, nested_responses = await get_monthly_alerts_counts(symbols, message, current_api_key_index, current_vpn_server_index)
                monthly_action_counts.update(counts)
                # responses.extend(nested_responses)
            else :
                current_api_key_index += 1
                current_vpn_server_index +=1
                await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))        
                counts, nested_responses = await get_monthly_alerts_counts(symbols, message, current_api_key_index, current_vpn_server_index)
                monthly_action_counts.update(counts)
                # responses.extend(nested_responses)
        else:
            print("NOT CONTAINS")
            if await is_vpn_active():
                await desactivate_vpn()        
        
        #Responses has all the data about RSI
        # print(responses)

        # Procesar las respuestas y acumular los resultados en monthly_action_counts
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
        print(f"stdout: {stdout_decoded}")

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

async def calculate_month_diff():

    ancient_date = datetime.strptime("1999-11-15", "%Y-%m-%d")

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

        total_months = await calculate_month_diff()

        average_rsi_below_25 = round(total_actions_rsi_below_25 / total_months, 2)

        result = {
            "avg_below_25": average_rsi_below_25,
        }
    return result


async def fetch_close_price(session, symbol, message, current_api_key_index):
    api_key = config.get_next_api_key(current_api_key_index)
    print(api_key, "KEY")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "compact",
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

async def test_func(rsi_data, closing_prices, symbols):
    # Convertir los datos de RSI a un DataFrame
    rsi_df = pd.DataFrame.from_dict(rsi_data, orient='index')
    rsi_df.index = pd.to_datetime(rsi_df.index)
    rsi_df['RSI'] = rsi_df['RSI'].astype(float)

    # Convertir los datos de precios de cierre a un DataFrame
    close_df = pd.DataFrame.from_dict(closing_prices, orient='index')
    close_df.index = pd.to_datetime(close_df.index)
    close_df.rename(columns={'close': 'Close'}, inplace=True)
    close_df['Close'] = close_df['Close'].astype(float)

    # Unir los DataFrames en uno solo
    df = pd.merge(rsi_df, close_df, left_index=True, right_index=True)
     
    df.sort_index(inplace=True)
    print(df.head(), "ESTO")  # Verificar que el DataFrame se creó correctamente

    return df


async def test_calculate_drwadown(df):
    holding = False
    entry_price = 0
    portfolio_value = []
    drawdowns = []

    # Simular las transacciones
    for index, row in df.iterrows():
        if not holding and row['RSI'] < 25:
            holding = True
            entry_price = row['Close']
        elif holding and row['RSI'] > 70:
            holding = False
            exit_price = row['Close']
        
        # Calcular el valor del portafolio
        if holding:
            portfolio_value.append(row['Close'])
        else:
            portfolio_value.append(0)

    # Convertir lista de valores del portafolio a una serie de pandas
    portfolio_series = pd.Series(portfolio_value, index=df.index)

    # Calcular el drawdown
    rolling_max = portfolio_series.cummax()
    drawdown = (portfolio_series - rolling_max) / rolling_max
    max_drawdown = drawdown.min()
    
    print(max_drawdown, "????")
    return max_drawdown

async def calculate_maximum_drawdown(symbols, message, data_rsi_raw, current_api_key_index, current_vpn_server_index):
    maximum_drawdown = {}
    print(symbols)
    if not await is_vpn_active():
        print("NOOO")
        await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))
    else:
        print("SIII")

    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_close_price(
                session,
                symbol,
                message,
                current_api_key_index,
            )
            for symbol in symbols
        ]
        responses = await asyncio.gather(*tasks)

        # print(responses)

        substring = "rate limit is 25 requests per day"
         
        #DO RECUSIVITY

        if await contains_info(responses, substring):
            print("CONTAINS")
            if await is_vpn_active():
                # change api key and vpn server
                current_api_key_index += 1
                current_vpn_server_index +=1
                await desactivate_vpn()
                await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))
                result = await calculate_maximum_drawdown(symbols, message, data_rsi_raw, current_api_key_index, current_vpn_server_index)
                if result:
                    maximum_drawdown.update(result)
            else :
                current_api_key_index += 1
                current_vpn_server_index +=1
                await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))        
                result = await calculate_maximum_drawdown(symbols, message, data_rsi_raw, current_api_key_index, current_vpn_server_index)
                if result:
                    maximum_drawdown.update(result)
        else:
            print("NOT CONTAINS")
            if await is_vpn_active():
                await desactivate_vpn()        
        
        #Responses has all the data about RSI
        closing_prices = {}
        for response in responses:
            symbol = response["Meta Data"]["2. Symbol"]
            if symbol not in closing_prices:
                closing_prices[symbol] = {}

            for date, prices in response["Time Series (Daily)"].items():
                closing_prices[symbol][date] = {"close": prices["4. close"]}

        # print(closing_prices, "INTERESA")
        print(data_rsi_raw, "a")
        print(symbols, "A")
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
        print(rsi_data, "INTERESA 2")
        
        # df_data = await test_func(rsi_data, closing_prices, symbols)
        # mdre = await test_calculate_drwadown(df_data)

    return maximum_drawdown


current_api_key_index = 0
current_vpn_server_index = 0

@router.message(Command(commands=["backtest", "BACKTEST", "Backtest", "BackTest"]))
async def backtest_handler(message: Message):
    # getting all the symbols to do the backtest
    # Split the message text to separate the command and the arguments
    args = message.text.split(maxsplit=1)

    # Check if arguments are provided
    if len(args) < 2:
        await message.answer(
            **Text(
                "Por favor, proporciona los ",
                Bold("símbolos"),
                " de las empresas.\nEjemplo: /backtest AAPL, GOOGL, MSFT, IBM, META o /backtest AAPL GOOGL MSFT IBM META",
            ).as_kwargs()
        )
        return
    
    # Process the arguments to handle both comma and space-separated symbols
    raw_symbols = args[1].replace(",", " ").split()
    symbols = [symbol.strip().upper() for symbol in raw_symbols]

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
                f"🧪BackTest\nEmpresas analizadas: {symb_msg}",
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
