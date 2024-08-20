import os
import json
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
import yfinance as yf
import asyncio

matrix = {
    "2000": ["MSFT", "GE", "CSCO", "WMT", "XOM", "INTC", "C", "PFE", "NOK", "TM", "DTE", "HD", "ORCL", "MRK"],
    "2005": ["XOM", "GE", "MSFT", "C", "BP", "SHEL", "TM", "WMT", "IBM", "JNJ", "COP", "INTC", "AIG", "PFE"],
    "2010": ["XOM", "MSFT", "AAPL", "GE", "WMT", "BRK-B", "PG", "BAC", "JNJ", "WFC", "GOOG", "KO", "CVX", "PFE", "CSCO"],
    "2015": ["AAPL", "GOOG", "XOM", "BRK-B", "MSFT", "WFC", "JNJ", "NVS", "WMT", "GE", "PG", "JPM", "CVX", "ORCL", "VZ"],
    "2020": ["AAPL", "MSFT", "AMZN", "GOOG", "META", "BRK-B", "TSM", "ASML", "TSLA", "BABA", "JPM", "V", "MA", "UNH", "HD"],
    # "2025": ["MSFT", "AAPL", "NVDA", "GOOG", "AMZN", "META", "BRK-B", "LLY", "AVGO", "TSM", "NVO", "JPM"],
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
    # Inicializar diccionarios para almacenar los datos
    data_rsi = {'Symbol': ticker, 'RSI': {}}
    data_close_price = {'Symbol': ticker, 'CLOSE': {}}
    data_high = {'Symbol': ticker, 'HIGH': {}}
    data_low = {'Symbol': ticker, 'LOW': {}}
    data_volume = {'Symbol': ticker, 'VOLUME': {}}

    # Iterar sobre cada fila en el DataFrame
    for date, values in data[['Close', 'RSI', 'High', 'Low', 'Volume']].iterrows():
        # Formatear la fecha como cadena
        date = date.strftime("%Y-%m-%d")
        # Almacenar los valores en los diccionarios correspondientes
        data_rsi["RSI"][date] = values['RSI']
        data_close_price["CLOSE"][date] = values['Close']
        data_high["HIGH"][date] = values['High']
        data_low["LOW"][date] = values['Low']
        data_volume["VOLUME"][date] = values['Volume']

    # Devolver los diccionarios con los datos almacenados
    all_data = {
        "rsi" : data_rsi,
        "close_price" : data_close_price,
        "high" : data_high,
        "low" : data_low,
        "volume" : data_volume
    }
    return all_data


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
        if not os.path.exists(f"{folder_path}/{year}/high"):
            os.makedirs(f"{folder_path}/{year}/high")
        if not os.path.exists(f"{folder_path}/{year}/low"):
            os.makedirs(f"{folder_path}/{year}/low")
        if not os.path.exists(f"{folder_path}/{year}/volume"):
            os.makedirs(f"{folder_path}/{year}/volume")

        for ticker in matrix[year]:
            start_date, end_date = await get_date(f'{year}')
            start_date = start_date - timedelta(days=200)  # Cambio para extraer datos adicionales si es necesario
            start_date = start_date.strftime("%Y-%m-%d")
            end_date = end_date.strftime("%Y-%m-%d")

            print(ticker)
            data = yf.download(ticker, start=start_date, end=end_date)
            rsi = RSIIndicator(close=data['Close'], window=14)
            data['RSI'] = rsi.rsi()
            data = data.dropna()
            # year = int(year) - 1
            # data = data[~data.index.year.isin([year])]
            # year = year + 1
            # year = str(year)

            # data_rsi, data_close_price, data_high, data_low, data_volume = await trim_data(data, ticker)
            all_data = await trim_data(data, ticker)

            for folder_name in all_data:
                file_path = os.path.join(folder_path, year, folder_name, f"{ticker}.json")
                if not os.path.exists(file_path):
                    with open(file_path, "w") as json_file:
                        json.dump(all_data[folder_name], json_file, indent=4)

            await asyncio.sleep(2)  # Espera 2 segundos antes de pasar a la siguiente iteración




async def update_data():
    print("Here we're going to update data every day")

    year = list(matrix.keys())[-1]
    folder_path = "data"
    data_rsi = {}
    data_close_price = {}
    
    '''TODO'''
    #To calculate daily rsi, you must read the previous 30 days of rsis
    #If the is no data becouse we are in a new year, for example, search in the previous year
    # If the file does not exist in the previous year, we have to download the data and calculate

    for ticker in matrix[year]:
        print(ticker)
        data = yf.download(ticker, period="1d")
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
        