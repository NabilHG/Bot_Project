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


async def load_dummy_data(folder_path):
    data_list = []
    # print(folder_path)
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                data_list.append(data)

    return data_list


async def fetch_rsi(session, symbol, current_api_key_index, message=None):
    api_key = config.get_next_api_key(current_api_key_index)
    print(api_key, "KEY")
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
    if not await is_vpn_active():
        print("NOOO")
        await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))
    else:
        print("SIII")

    async with aiohttp.ClientSession() as session:
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

        responses = await load_dummy_data('/home/bot/Desktop/Bot_Project/bot/dummy_data_rsi')
        substring = "rate limit is 25 requests per day"
        if await contains_info(responses, substring):
            print("CONTAINS")
            if await is_vpn_active():
                await desactivate_vpn()
            
            # change api key and vpn server
            current_api_key_index += 1
            current_vpn_server_index += 1

            await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))       
            
            #call recursively 
            counts, nested_responses = await get_monthly_alerts_counts(symbols, message, current_api_key_index, current_vpn_server_index)
            # counts, nested_responses = await get_monthly_alerts_counts(symbols, message, current_api_key_index, current_vpn_server_index)
            #update
            monthly_action_counts.update(counts)
        else:
            print("NOT CONTAINS")
            if await is_vpn_active():
                await desactivate_vpn()        

          

        #Responses has all the data about RSI
        # print(responses)

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

        print(f'Media de alertas de compra: {result}')
    return result


async def fetch_close_price(session, symbol, current_api_key_index, message=None):
    print("ASD")
    api_key = config.get_next_api_key(current_api_key_index)
    print(api_key, "KEY")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "outputsize": "full",
        "apikey": api_key,
    }
    print("1")
    async with session.get(url, params=params) as response:
        print("2")
        if response.status == 200:
            print("3")
            try:
                print("4")
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
                print(data, "ESTO ES DATA")
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
    if not await is_vpn_active():
        print("NOOO")
        await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))
    else:
        print("SIII")

    async with aiohttp.ClientSession() as session:
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

        substring = "rate limit is 25 requests per day"
         
        responses = await load_dummy_data('/home/bot/Desktop/Bot_Project/bot/dummy_data_price') 

        if await contains_info(responses, substring):
            print("CONTAINS")
            if await is_vpn_active():
                await desactivate_vpn()
            
            # change api key and vpn server
            current_api_key_index += 1
            current_vpn_server_index += 1
            # call recursively 
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
        
        # df_data = await test_func(rsi_data, closing_prices, symbols)
        # mdre = await test_calculate_drwadown(df_data)
        df = await get_dataframe(rsi_data, closing_prices)

        await calculate_drawdown_profit(df, symbols)

    return maximum_drawdown

async def get_dataframe(rsi_data, closing_prices):
    close_df = pd.DataFrame({k: {pd.to_datetime(date): float(v['close']) for date, v in val.items()} for k, val in closing_prices.items()}) 
    # Convertir datos de RSI a DataFrame 
    rsi_df = pd.DataFrame({k: {pd.to_datetime(date): float(v['RSI']) for date, v in val.items()} for k, val in rsi_data.items()}) 
    # Renombrar las columnas de los DataFrames para diferenciarlas 
    close_df = close_df.rename(columns=lambda x: f"{x}_Close") 
    rsi_df = rsi_df.rename(columns=lambda x: f"{x}_RSI") 
    # Unir los DataFrames en uno solo 
    combined_df = pd.concat([close_df, rsi_df], axis=1) 
    # Ordenar por fecha 
    combined_df = combined_df.sort_index() 
    print(combined_df, "DATAFRAME")

    return combined_df


async def calculate_drawdown_profit(df, symbols):
    initial_cash = 1000  # Capital inicial
    cash = initial_cash
    portfolio = {ticker: 0 for ticker in symbols}
    buy_prices = {ticker: None for ticker in symbols}
    portfolio_value = []
    shares_buyed = []
    var_A = 0
    
    # Simular las operaciones
    for date, row in df.iterrows():
        close_prices = {ticker: row[f'{ticker}_Close'] for ticker in portfolio.keys()}
        rsis = {ticker: row[f'{ticker}_RSI'] for ticker in portfolio.keys()}
    
        #ONCE A SHARE IS BUYED, WE CAN NOT BUY IT AGAIN UNTIL WE SELL IT?

        
        # Señales de compra y venta
        for ticker in portfolio.keys():
            if rsis[ticker] < 25 and cash > 0:
                shares_to_buy = (cash / len(portfolio.keys())) // close_prices[ticker] #RETHINK THIS
                print(f"Cash: {cash}, cantidad de tickers: {len(portfolio.keys())}, precio de cierre: {close_prices[ticker]}")
                print(f"Cuantas acciones se van a comprar: {shares_to_buy}")
                if shares_to_buy > 0 and ticker not in shares_buyed:
                    var_A +=1
                    cash -= shares_to_buy * close_prices[ticker]
                    portfolio[ticker] += shares_to_buy
                    buy_prices[ticker] = close_prices[ticker]
                    shares_buyed.append(ticker)
                    print(f"Compra {ticker}:{rsis[ticker]} el dia {date}")
                else:
                    print(f"No se pudo comprar {ticker} por cash insuficiente o ya esta comprado")
            elif rsis[ticker] > 70 and portfolio[ticker] > 0 and ticker in shares_buyed:
                cash += portfolio[ticker] * close_prices[ticker]
                portfolio[ticker] = 0
                buy_prices[ticker] = None
                shares_buyed.remove(ticker)
                print(f"Venta {ticker}:{rsis[ticker]} el dia {date}")
            elif buy_prices[ticker] is not None and close_prices[ticker] < buy_prices[ticker] * 0.9 and ticker in shares_buyed:
                cash += portfolio[ticker] * close_prices[ticker]
                portfolio[ticker] = 0
                buy_prices[ticker] = None
                shares_buyed.remove(ticker)
                print(f"Venta {ticker} por perdida de 10%:{rsis[ticker]} el dia {date}")

        # Valor actual de la cartera en cada paso
        current_value = cash + sum(portfolio[ticker] * close_prices[ticker] for ticker in portfolio.keys())
        portfolio_value.append(current_value)

    # Crear un DataFrame con la curva de capital
    df['Portfolio Value'] = portfolio_value
    print(df['Portfolio Value'], "portfolio value")
    max_drawdown_PANDAS = max(1 - df['Portfolio Value']/df['Portfolio Value'].rolling(window=len(df['Portfolio Value']), min_periods=0).max())
    print(max_drawdown_PANDAS, "max_drawdown PANDAS")
    # Calcular el maximum drawdown
    df['Peak'] = df['Portfolio Value'].cummax()
    df['Drawdown'] = df['Portfolio Value'] - df['Peak']
    df['Drawdown Percent'] = df['Drawdown'] / df['Peak']

    # Maximum drawdown
    max_drawdown = df['Drawdown Percent'].min()
    # Rentabilidad del portafolio
    final_portfolio_value = df['Portfolio Value'].iloc[-1]
    profitability = (final_portfolio_value - initial_cash) / initial_cash * 100
    
    print(f'Maximum Drawdown: {max_drawdown * 100:.2f}%')
    print(f'Profitability: {profitability:.2f}%')
    print(f'Media de alertas de compra: {var_A/60}')


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
                " de las empresas.\nEjemplo: /backtest AAPL, GOOG, MSFT, IBM, META o /backtest AAPL GOOG MSFT IBM META",
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
