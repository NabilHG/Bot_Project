import os
import json
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
import yfinance as yf
import asyncio

matrix = {
    "2000": ["MSFT", "GE", "CSCO", "WMT", "XOM", "INTC", "C", "PFE", "NOK", "TM"],
    "2005": ["XOM", "GE", "MSFT", "C", "BP", "SHEL", "TM", "WMT", "IBM", "JNJ"],
    "2010": ["XOM", "MSFT", "AAPL", "GE", "WMT", "BRK-B", "PG", "BAC", "JNJ", "WFC"],
    "2015": ["AAPL", "GOOG", "XOM", "BRK-B", "MSFT", "WFC", "JNJ", "NVS", "WMT", "GE"],
    "2020": ["AAPL", "MSFT", "AMZN", "GOOG", "META", "BRK-B", "TSM", "ASML", "TSLA", "BABA",],
    # "2025": ["MSFT", "AAPL", "NVDA", "GOOG", "AMZN", "META", "BRK.B", "LLY", "AVGO", "TSM",],
}

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
            rsi = RSIIndicator(close=data['Close'], window=14)
            data['RSI'] = rsi.rsi()
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

            