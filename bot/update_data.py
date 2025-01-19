import os
import json
import yfinance as yf
import asyncio
from ta.momentum import RSIIndicator
from datetime import datetime
from bot.config import MATRIX, FIRST_ADMIN


async def update_data(updated_data, is_ticker_updated, bot):
    print("Here we're going to update data every day")
    year = list(MATRIX.keys())[-1]
    folder_path = "data"
    print(is_ticker_updated)
    
    for ticker in MATRIX[year]:
        if not is_ticker_updated[ticker]:
            print(ticker)
            data = yf.download(ticker, period="6mo")
            rsi = RSIIndicator(close=data['Close'], window=14)
            data['RSI'] = rsi.rsi()
            
            file_path_close_price = os.path.join(folder_path, year, "close_price", f"{ticker}.json")
            file_path_rsi = os.path.join(folder_path, year, "rsi", f"{ticker}.json")
            
            if os.path.exists(file_path_close_price):
                with open(file_path_close_price, 'r') as archivo:
                    data_close_price = json.load(archivo)
            else:
                data_close_price = {'CLOSE': {}}
            
            if os.path.exists(file_path_rsi):
                with open(file_path_rsi, 'r') as archivo:
                    data_rsi = json.load(archivo)
            else:
                data_rsi = {'RSI': {}}
            
            # Determinar la última fecha en los archivos para CLOSE y RSI
            if data_close_price['CLOSE']:
                file_last_date_close = max(datetime.strptime(date, '%Y-%m-%d') for date in data_close_price['CLOSE'].keys())
            else:
                file_last_date_close = datetime.strptime(data.index[0].strftime('%Y-%m-%d'), '%Y-%m-%d')
                
            if data_rsi['RSI']:
                file_last_date_rsi = max(datetime.strptime(date, '%Y-%m-%d') for date in data_rsi['RSI'].keys())
            else:
                file_last_date_rsi = datetime.strptime(data.index[0].strftime('%Y-%m-%d'), '%Y-%m-%d')

            # Usar la fecha más reciente de las dos como referencia
            file_last_date = max(file_last_date_close, file_last_date_rsi)

            # Encontrar todas las fechas nuevas después de la última fecha registrada
            new_data_dates = [date for date in data.index if date > file_last_date]

            if new_data_dates:
                for date in new_data_dates:
                    last_date_str = date.strftime('%Y-%m-%d')
                    last_close_price = data['Close'].loc[date]
                    last_rsi = data['RSI'].loc[date]
                    
                    data_close_price['CLOSE'][last_date_str] = last_close_price
                    data_rsi['RSI'][last_date_str] = last_rsi
                    print(f"Writing data for {ticker} on {last_date_str}")

                with open(file_path_close_price, 'w') as archivo:
                    json.dump(data_close_price, archivo, indent=4)
                
                with open(file_path_rsi, 'w') as archivo:
                    json.dump(data_rsi, archivo, indent=4)
            else:
                is_ticker_updated[ticker] = True
                print(f'Updated: {ticker}')

        else:
            print(f'Already updated: {ticker}')
        
        await asyncio.sleep(2)  # Espera 2 segundos antes de pasar a la siguiente iteración

    if all(is_ticker_updated.values()):
        updated_data[0] = True
        await bot.send_message(FIRST_ADMIN, "Datos actualizados ✅")
    else:
        print(f'Not all data updated: {is_ticker_updated}')

    print(f'Return updated_data: {updated_data[0]}')
    return updated_data
