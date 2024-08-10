from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import os
import json
import aiohttp
from bot import config
from bot.vpn import VPNManager
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import asyncio

router = Router()
vpn_manager = VPNManager()

matrix = {
    "2000": ["MSFT", "GE", "CSCO", "WMT", "XOM", "INTC", "C", "PFE", "NOK", "TM"],
    "2005": ["XOM", "GE", "MSFT", "C", "BP", "SHEL", "TM", "WMT", "IBM", "JNJ"],
    "2010": ["XOM", "MSFT", "AAPL", "GE", "WMT", "BRK-B", "PG", "BAC", "JNJ", "WFC"],
    "2015": ["AAPL", "GOOG", "XOM", "BRK-B", "MSFT", "WFC", "JNJ", "NVS", "WMT", "GE"],
    "2020": ["AAPL", "MSFT", "AMZN", "GOOG", "META", "BRK-B", "TSM", "ASML", "TSLA", "BABA",],
    # "2025": ["MSFT", "AAPL", "NVDA", "GOOG", "AMZN", "META", "BRK.B", "LLY", "AVGO", "TSM",],
}

# current_api_key_index = 0
# current_vpn_server_index = 0
substring = "rate limit is 25 requests per day"


async def fetch_close_price(session, symbol, current_api_key_index):
    if await vpn_manager.is_vpn_active():
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
                    return None
                # print(data, "ESTO ES DATA")
                return data
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return None
        else:
            return None


async def fetch_rsi(session, symbol, current_api_key_index, message=None):
    if await vpn_manager.is_vpn_active():
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
                    return None
                # print(data, "ESTO ES DATA")
                return data
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return None
        else:
            return None


async def validate_info(
    responses, session, ticker, data, type, current_api, current_vpn
):
    result = {}
    if await vpn_manager.contains_info(responses, substring):
        print("CONTAINS")
        if await vpn_manager.is_vpn_active():
            await vpn_manager.desactivate_vpn()

        # change api key and vpn server
        current_api = +1
        current_vpn = +1

        await vpn_manager.activate_vpn(config.get_next_vpn_server(current_vpn))

        # call recursively
        if type == "rsi":
            result = await get_rsi(session, ticker, data, current_api, current_vpn)
        elif type == "close":
            result = await get_close_price(
                session, ticker, data, current_api, current_vpn
            )
            print(result, "this")

    else:
        print("NOT CONTAINS")
        data.update(responses)


async def get_rsi(
    session, ticker, data, current_api_key_index, current_vpn_server_index
):
    responses = await fetch_rsi(session, ticker, current_api_key_index)
    type = "rsi"
    await validate_info(
        responses,
        session,
        ticker,
        data,
        type,
        current_api_key_index,
        current_vpn_server_index,
    )


async def get_close_price(
    session, ticker, data, current_api_key_index, current_vpn_server_index
):
    responses = await fetch_close_price(session, ticker, current_api_key_index)
    type = "close"
    await validate_info(
        responses,
        session,
        ticker,
        data,
        type,
        current_api_key_index,
        current_vpn_server_index,
    )


async def get_date(year):
    year_map = {
        "2000": ("2000", "2004"),
        "2005": ("2005", "2009"),
        "2010": ("2010", "2014"),
        "2015": ("2015", "2019"),
        "2020": ("2020", "2024"),
        # "2025": ("2025", "2029"),
    }

    if year in year_map:
        year1, year2 = year_map[year]
        start_date = datetime.strptime(f"{year1}-01-01", "%Y-%m-%d")
        end_date = datetime.strptime(f"{year2}-12-31", "%Y-%m-%d")
        return start_date, end_date
    else:
        raise ValueError(
            f"Year {year} is not valid. Valid years are: {', '.join(year_map.keys())}"
        )


async def trim_data(data, ticker):
    data_rsi = {'Symbol': ticker, 'RSI': {}}
    data_close_price = {'Symbol': ticker, 'CLOSE': {}}

    for date, values in data[['Close', 'RSI']].iterrows():
        # print(f'Fecha: {date}')
        date = date.strftime("%Y-%m-%d")
        data_rsi["RSI"][date] = values['RSI']
        data_close_price["CLOSE"][date] = values['Close']

    return data_rsi, data_close_price

async def get_data():
    folder_path = "data"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    for year in matrix:
        if not os.path.exists(f"{folder_path}/{year}"):
            os.makedirs(f"{folder_path}/{year}")
        if not os.path.exists(f"{folder_path}/{year}/rsi"):
            os.makedirs(f"{folder_path}/{year}/rsi")
        if not os.path.exists(f"{folder_path}/{year}/close_price"):
            os.makedirs(f"{folder_path}/{year}/close_price")
        print(matrix[year])
        data_rsi = {}
        data_close_price = {}

        for ticker in matrix[year]:
            print(ticker)
            start_date, end_date = await get_date(f'{year}')
            start_date = start_date - timedelta(days=30)
            # Convertimos la nueva fecha a una cadena si es necesario
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")

            data = yf.download(ticker, start=start_date, end=end_date)
            # Calcular el RSI diario y agregarlo al DataFrame
            data['RSI'] = await calculate_rsi(data)

            # Eliminar filas con valores NaN que pueden aparecer al inicio
            data = data.dropna()
            # Convertir la cadena a un número entero
            year = int(year) - 1
            # Borramos los datos de los anteriores años
            data = data[~data.index.year.isin([year])]
            year = year + 1
            year = str(year)
            data_rsi, data_close_price = await trim_data(data, ticker)

            if not os.path.exists(f"{folder_path}/{year}/close_price/{ticker}.json"):
                file_path = os.path.join(folder_path, year, "close_price", f"{ticker}.json")
                with open(file_path, "w") as json_file:
                    json.dump(data_close_price, json_file, indent=4)

            if not os.path.exists(f"{folder_path}/{year}/rsi/{ticker}.json"):
                file_path = os.path.join(folder_path, year, "rsi", f"{ticker}.json")
                with open(file_path, "w") as json_file:
                    json.dump(data_rsi, json_file, indent=4)

            await asyncio.sleep(2)  # Espera 2 segundos antes de pasar a la siguiente iteración

async def test():
    year = "2015"
    ticker = 'AAPL'
    start_date, end_date = await get_date(f'{year}')
    start_date = start_date - timedelta(days=30)
    # Convertimos la nueva fecha a una cadena si es necesario
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")

    data = yf.download(ticker, start=start_date, end=end_date)
    # Calcular el RSI diario y agregarlo al DataFrame
    data['RSI'] = await calculate_rsi(data)

    # Eliminar filas con valores NaN que pueden aparecer al inicio
    data = data.dropna()
    # Convertir la cadena a un número entero
    year = int(year) - 1
    # Borramos los datos de los anteriores años
    data = data[~data.index.year.isin([year])]
    with open('output.txt', 'w') as f:
        print(data[['Close', 'RSI']].to_string(), file=f)

    await trim_data(data, ticker)

# Función para calcular el RSI
async def calculate_rsi(data):
    # Calcular la diferencia en el precio de cierre día a día
    delta = data['Close'].diff()
    
    # Calcular las ganancias y pérdidas
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    
    # Calcular las ganancias y pérdidas medias
    avg_gain = ganancia.rolling(window=14, min_periods=14).mean()
    avg_loss = perdida.rolling(window=14, min_periods=14).mean()
    
    # Calcular el RS (Relative Strength)
    rs = avg_gain / avg_loss
    
    # Calcular el RSI
    rsi = 100 - (100 / (1 + rs))
    
    return rsi



@router.message(Command(commands=["update"]))
async def backtest_handler(message: Message):
    print("uploadCompanies")