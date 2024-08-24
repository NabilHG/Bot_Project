import os
import json
import yfinance as yf
import asyncio
from ta.momentum import RSIIndicator

matrix = {
    "2000": ["MSFT", "GE", "CSCO", "WMT", "XOM", "INTC", "C", "PFE", "NOK", "TM", "DTE", "HD", "ORCL", "MRK"],
    "2005": ["XOM", "GE", "MSFT", "C", "BP", "SHEL", "TM", "WMT", "IBM", "JNJ", "COP", "INTC", "AIG", "PFE"],
    "2010": ["XOM", "MSFT", "AAPL", "GE", "WMT", "BRK-B", "PG", "BAC", "JNJ", "WFC", "GOOG", "KO", "CVX", "PFE", "CSCO"],
    "2015": ["AAPL", "GOOG", "XOM", "BRK-B", "MSFT", "WFC", "JNJ", "NVS", "WMT", "GE", "PG", "JPM", "CVX", "ORCL", "VZ"],
    "2020": ["AAPL", "MSFT", "AMZN", "GOOG", "META", "BRK-B", "TSM", "ASML", "TSLA", "BABA", "JPM", "V", "MA", "UNH", "HD"],
    # "2025": ["MSFT", "AAPL", "NVDA", "GOOG", "AMZN", "META", "BRK-B", "LLY", "AVGO", "TSM", "NVO", "JPM"],
}

async def update_data(updated_data):
    updated_data = updated_data
    print("Here we're going to update data every day")
    year = list(matrix.keys())[-1]
    folder_path = "data"
    is_ticker_updated = {ticker: False for ticker in matrix[year]}
    print(is_ticker_updated)
    
    while True:
        for ticker in matrix[year]:
            updated_close_price = False
            updated_rsi = False
            if not is_ticker_updated[ticker]:
                print(ticker)
                data = yf.download(ticker, period="6mo")
                rsi = RSIIndicator(close=data['Close'], window=14)
                data['RSI'] = rsi.rsi()
                last_close_price = data['Close'].iloc[-1]
                last_rsi = data['RSI'].iloc[-1]
                last_date = data.index[-1].strftime('%Y-%m-%d')
                
                file_path_close_price = os.path.join(folder_path, year, "close_price", f"{ticker}.json")
                if os.path.exists(file_path_close_price):
                    with open(file_path_close_price, 'r') as archivo:
                        data_close_price = json.load(archivo)
                    
                    file_last_date = list(data_close_price['CLOSE'].keys())[-1]

                    if last_date != file_last_date:
                        print("Writing")
                        data_close_price['CLOSE'][last_date] = last_close_price
                        with open(file_path_close_price, 'w') as archivo:
                            json.dump(data_close_price, archivo, indent=4)
                    else:
                        updated_close_price = True
                        print(f'Updated: {ticker}')

                file_path_rsi = os.path.join(folder_path, year, "rsi", f"{ticker}.json")
                if os.path.exists(file_path_rsi):
                    with open(file_path_rsi, 'r') as file:
                        data_rsi = json.load(file)
                    
                    file_last_date = list(data_rsi['RSI'].keys())[-1]

                    if last_date != file_last_date:
                        print("Writing")
                        data_rsi['RSI'][last_date] = last_rsi
                        with open(file_path_rsi, 'w') as file:
                            json.dump(data_rsi, file, indent=4)
                    else:
                        updated_rsi = True
                        print(f'Updated rsi: {ticker}')

                if updated_rsi and updated_close_price:
                    is_ticker_updated[ticker] = True
                    print(is_ticker_updated)

            else:
                print(f'Already updated: {ticker}')
            await asyncio.sleep(2)  # Espera 2 segundos antes de pasar a la siguiente iteración
        if all(is_ticker_updated):
            updated_data = True
            break
        else:
            print(f'Not all data updated: {is_ticker_updated}')

    return updated_data
