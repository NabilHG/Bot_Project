from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
import os
import json
import aiohttp
from bot import config
from .backtest import is_vpn_active
from .backtest import activate_vpn
from .backtest import desactivate_vpn
from datetime import datetime

router = Router()

matrix = {
    "2000": ["MSFT", "GE", "CSCO", "WMT", "XOM", "INTC", "C", "PFE", "NOK", "TM"],
    "2005": ["XOM", "GE", "MSFT", "C", "BP", "SHEL", "TM" , "WMT", "IBM", "JNJ"],
    "2010": ["XOM", "MSFT", "AAPL", "GE", "WMT", "BRK.B", "PG", "BAC", "JNJ", "WFC"],
    "2015": ["AAPL", "GOOG", "XOM", "BRK.B", "MSFT", "WFC", "JNJ", "NVS", "WMT", "GE"],
    "2020": ["AAPL", "MSFT", "AMZN", "GOOG", "META", "BRK.B", "TSM", "ASML", "TSLA", "BABA"],
    "2025": ["MSFT", "AAPL", "NVDA", "GOOG", "AMZN", "META", "BRK.B", "LLY", "AVGO", "TSM"],
} 

current_api_key_index = 0
current_vpn_server_index = 0
substring = "rate limit is 25 requests per day"

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
async def fetch_close_price(session, symbol, current_api_key_index):
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
                    return None
                # print(data, "ESTO ES DATA")
                return data
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return None
        else:
            return None

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
                    return None
                # print(data, "ESTO ES DATA")
                return data
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return None
        else:
            return None


async def validate_info(responses, session, ticker, data, type, current_api, current_vpn):
    result = {}
    if await contains_info(responses, substring):
        print("CONTAINS")
        if await is_vpn_active():
            await desactivate_vpn()
          
        # change api key and vpn server
        current_api =+ 1
        current_vpn =+ 1
        
        await activate_vpn(config.get_next_vpn_server(current_vpn))
        
        #call recursively 
        if type == 'rsi':
            result = await get_rsi(session, ticker, data, current_api, current_vpn)
        elif type == 'close':
            result = await get_close_price(session, ticker, data, current_api, current_vpn)
            print(result, "this")
        
    else:
        print("NOT CONTAINS")
        data.update(responses)    

            

async def get_rsi(session, ticker, data, current_api_key_index, current_vpn_server_index):
    responses = await fetch_rsi(session, ticker, current_api_key_index)
    type = 'rsi'
    await validate_info(responses, session, ticker, data, type, current_api_key_index, current_vpn_server_index)

async def get_close_price(session, ticker, data, current_api_key_index, current_vpn_server_index):
    responses = await fetch_close_price(session, ticker, current_api_key_index)
    type = 'close'
    await validate_info(responses, session, ticker, data, type, current_api_key_index, current_vpn_server_index)

async def get_date(year):
    year_map = {
        '2000': ('2000', '2005'),
        '2005': ('2005', '2010'),
        '2010': ('2010', '2015'),
        '2015': ('2015', '2020'),
        '2020': ('2020', '2025'),
        '2025': ('2025', '2030')
    }
    
    if year in year_map:
        year1, year2 = year_map[year]
        start_date = datetime.strptime(f'{year1}-01-03', '%Y-%m-%d')
        end_date = datetime.strptime(f'{year2}-12-30', '%Y-%m-%d')
        return start_date, end_date
    else:
        raise ValueError(f"Year {year} is not valid. Valid years are: {', '.join(year_map.keys())}")


async def trim_data(data, year, type):
    # Convertir las fechas a objetos datetime para comparación
    start_date, end_date = await get_date(year)

    # Filtrar los datos de "Time Series (Daily)" entre las fechas dadas
    filtered_time_series = {date: values for date, values in data[f'{type}'].items()
                            if start_date <= datetime.strptime(date, '%Y-%m-%d') <= end_date}

    # Crear el diccionario con "Meta Data" y los datos filtrados
    filtered_data = {
        'Meta Data': data['Meta Data'],
        f'{type}': filtered_time_series
    }

    return filtered_data

async def get_data():
    folder_path = 'data'
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    for year in matrix:
        if not os.path.exists(f'{folder_path}/{year}'):
            os.makedirs(f'{folder_path}/{year}')
        if not os.path.exists(f'{folder_path}/{year}/rsi'):
            os.makedirs(f'{folder_path}/{year}/rsi')
        if not os.path.exists(f'{folder_path}/{year}/close_price'):
            os.makedirs(f'{folder_path}/{year}/close_price')
        print(matrix[year])
        data_rsi = {}
        data_close_price = {}

        for ticker in matrix[year]:
            print(ticker)
            data_to_save_close_price = {}
            data_to_save_rsi = {}
            if not await is_vpn_active():
                await activate_vpn(config.get_next_vpn_server(current_vpn_server_index))

            if not os.path.exists(f'{folder_path}/{year}/close_price/{ticker}.json'):
                async with aiohttp.ClientSession() as session:
                    await get_close_price(session, ticker, data_close_price, current_api_key_index, current_vpn_server_index)
                data_to_save_close_price = await trim_data(data_close_price, year, 'Time Series (Daily)')
                
                file_path = os.path.join(folder_path, year, 'close_price', f'{ticker}.json')
                with open(file_path, 'w') as json_file:
                    json.dump(data_to_save_close_price, json_file, indent=4)

            if not os.path.exists(f'{folder_path}/{year}/rsi/{ticker}.json'):
                async with aiohttp.ClientSession() as session:
                    await get_rsi(session, ticker, data_rsi, current_api_key_index, current_vpn_server_index)
                    # print(data_rsi, "here")
                data_to_save_rsi = await trim_data(data_rsi, year, 'Technical Analysis: RSI')
            
                file_path = os.path.join(folder_path, year, 'rsi', f'{ticker}.json')
                with open(file_path, 'w') as json_file:
                    json.dump(data_to_save_rsi, json_file, indent=4)
            


@router.message(Command(commands=["update"]))
async def backtest_handler(message: Message):
    print("uploadCompanies")