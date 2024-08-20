from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import json
import pandas as pd
import math
import numpy as np

router = Router()



async def load_data(base_path, subfolder_name, type):
    data_list = []
    # Definir los rangos de fechas por year_folder
    date_ranges = {
        "2000": ("2000-01-01", "2004-12-30"),
        "2005": ("2005-01-01", "2009-12-30"),
        "2010": ("2010-01-01", "2014-12-30"),
        "2015": ("2015-01-01", "2019-12-30"),
        "2020": ("2020-01-01", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))  # Hasta ayer
    }

    # Recorrer todas las subcarpetas del segundo nivel
    for year_folder in os.listdir(base_path):
        year_folder_path = os.path.join(base_path, year_folder)
        # Verificar si la carpeta del año es un directorio
        if os.path.isdir(year_folder_path):
            target_folder_path = os.path.join(year_folder_path, subfolder_name)
            # Verificar si la carpeta deseada existe dentro de la carpeta del año
            if os.path.isdir(target_folder_path):
                # Obtener el rango de fechas para el year_folder actual
                start_date, end_date = date_ranges.get(year_folder, (None, None))
                if start_date and end_date:
                    # Cargar todos los archivos JSON dentro de la carpeta deseada
                    for filename in os.listdir(target_folder_path):
                        if filename.endswith(".json"):
                            file_path = os.path.join(target_folder_path, filename)
                            with open(file_path, "r") as file:
                                data = json.load(file)
                                
                                # Filtrar las fechas dentro del rango especificado
                                filtered = {
                                    date: price for date, price in data[type].items()
                                    if start_date <= date <= end_date
                                }

                                # Si hay datos filtrados, agregar al array con el símbolo incluido
                                if filtered:
                                    data_list.append({
                                        "Symbol": data["Symbol"],
                                        type: filtered
                                    })

    return data_list


async def calculate_month_diff(begin_date):

    ancient_date = datetime.strptime(f"{begin_date}", "%Y-%m-%d")

    current_date = datetime.now()

    delta = relativedelta(current_date, ancient_date)

    total_months = delta.years * 12 + delta.months

    return total_months


async def calculate_maximum_drawdown_profit():
    data_close_price_raw = await load_data("data", "close_price", "CLOSE")
    data_rsi_raw = await load_data("data", "rsi", "RSI")
    data_high_raw = await load_data("data", "high", "HIGH")
    data_low_raw = await load_data("data", "low", "LOW")
    data_volume_raw = await load_data("data", "volume", "VOLUME")

    closing_prices = {}
    for response in data_close_price_raw:
        symbol = response["Symbol"]
        if symbol not in closing_prices:
            closing_prices[symbol] = {}

        for date, prices in response["CLOSE"].items():
            closing_prices[symbol][date] = {"close": prices}

    rsi_data = {}

    for data in data_rsi_raw:
        symbol = data["Symbol"]
        if symbol not in data_rsi_raw:
            rsi_data[symbol] = {}

        for date, rsi in data["RSI"].items():
            rsi_data[symbol][date] = rsi

    high_data = {}

    for data in data_high_raw:
        symbol = data["Symbol"]
        if symbol not in data_high_raw:
            high_data[symbol] = {}

        for date, high in data["HIGH"].items():
            high_data[symbol][date] = high

    low_data = {}

    for data in data_low_raw:
        symbol = data["Symbol"]
        if symbol not in data_low_raw:
            low_data[symbol] = {}

        for date, low in data["LOW"].items():
            low_data[symbol][date] = low

    volume_data = {}

    for data in data_volume_raw:
        symbol = data["Symbol"]
        if symbol not in data_rsi_raw:
            volume_data[symbol] = {}

        for date, volume in data["VOLUME"].items():
            volume_data[symbol][date] = volume


    df = await get_dataframe(rsi_data, closing_prices, high_data, low_data, volume_data)
    max_drawdown, profitability, average_hold_duration, avg_notification = await simulation(df)

    return max_drawdown, profitability, average_hold_duration, avg_notification

async def calculate_atr(df, period=14):
    df = df.copy()
    # Asegúrate de estar modificando el DataFrame original usando .loc
    df.loc[:, ('prev_close')] = df[('Valor', 'Close')].shift(1)
    
    df.loc[:, ('Valor', 'tr')] = np.maximum(
        df[('Valor', 'High')] - df[('Valor', 'Low')],
        np.maximum(
            np.abs(df[('Valor', 'High')] - df[('prev_close')]),
            np.abs(df[('Valor', 'Low')] - df[('prev_close')])
        )
    )
    
    # Calcular el ATR usando el promedio móvil del TR
    df.loc[:, ('Valor', 'ATR')] = df[('Valor', 'tr')].rolling(window=period).mean()
    
    return df


async def calculate_vwap(df):
    # Hacer una copia explícita del DataFrame
    df = df.copy()

    df.loc[:, ('Valor', 'cum_vol')] = df[('Valor', 'Volume')].cumsum()
    df.loc[:, ('Valor', 'cum_vol_price')] = (df[('Valor', 'Close')] * df[('Valor', 'Volume')]).cumsum()

    # Calcular el VWAP
    df.loc[:, ('Valor', 'VWAP')] = df[('Valor', 'cum_vol_price')] / df[('Valor', 'cum_vol')]
    
    return df

async def calculate_obv(df):
    # Hacer una copia explícita del DataFrame
    df = df.copy()

    df.loc[:, ('Valor', 'obv')] = np.where(
        df[('Valor', 'Close')] > df[('Valor', 'Close')].shift(1),
        df[('Valor', 'Volume')],
        np.where(df[('Valor', 'Close')] < df[('Valor', 'Close')].shift(1), -df[('Valor', 'Volume')], 0)
    )

    # Calcular el OBV
    df.loc[:, ('Valor', 'OBV')] = df[('Valor', 'obv')].cumsum()

    return df


async def get_dataframe(rsi_data, close_data, high_data, low_data, volume_data):
    # Crear un DataFrame para RSI, Close, High, Low y Volume
    data_tuples = []
    for empresa, fechas in rsi_data.items():
        for fecha, valores in fechas.items():
            rsi = float(valores)
            close = float(close_data[empresa][fecha]["close"]) if fecha in close_data[empresa] else None
            high = float(high_data[empresa][fecha]) if fecha in high_data[empresa] else None
            low = float(low_data[empresa][fecha]) if fecha in low_data[empresa] else None
            volume = float(volume_data[empresa][fecha]) if fecha in volume_data[empresa] else None
            data_tuples.append((fecha, empresa, "RSI", rsi))
            data_tuples.append((fecha, empresa, "Close", close))
            data_tuples.append((fecha, empresa, "High", high))
            data_tuples.append((fecha, empresa, "Low", low))
            data_tuples.append((fecha, empresa, "Volume", volume))

    df = pd.DataFrame(data_tuples, columns=["Fecha", "Empresa", "Tipo", "Valor"])
    df.set_index(["Fecha", "Empresa", "Tipo"], inplace=True)
    df.index = df.index.set_levels(pd.to_datetime(df.index.levels[0]), level=0)
    df = df.unstack(level="Tipo")
    df.sort_index(inplace=True)

    # Opcional: Eliminar filas donde todos los valores sean NaN en df
    df_clean = df.dropna(how='all')

    # Calcular ATR, OBV y VWAP por empresa
    indicators = {}
    for empresa in df_clean.index.get_level_values('Empresa').unique():
        empresa_data = df_clean.xs(empresa, level='Empresa', drop_level=False)
        
        # Asegurarse de que hay datos para calcular los indicadores
        if not empresa_data.empty:
            empresa_data = await calculate_atr(empresa_data)
            empresa_data = await calculate_obv(empresa_data)
            empresa_data = await calculate_vwap(empresa_data)

            # Guardar el DataFrame temporal en el diccionario
            indicators[empresa] = empresa_data

    # print(f'Indicators: {indicators}')
  # Convertir los DataFrames a diccionarios y luego a una estructura JSON
    df = indicators.get("V")
    
    # Guardar la cadena de texto en un archivo .txt
    with open("aaaa.txt", "w") as file:
        file.write(df.to_string())
    # Concatenar los datos calculados de todas las empresas
    
    
    df_final = pd.concat(indicators.values())

    return df_final



async def simulation(df):
    # Inicializar el DataFrame para almacenar la fecha y el valor del portafolio
    df_portfolio_tracking = pd.DataFrame(columns=["Fecha", "Portfolio Value"])
    # Inicializar otras variables necesarias para la simulación
    initial_cash = 1000
    cash = initial_cash
    portfolio = {ticker: 0 for ticker in df.index.get_level_values("Empresa").unique()}
    buy_prices = {ticker: None for ticker in portfolio.keys()}
    buy_dates = {
        ticker: None for ticker in portfolio.keys()
    }  # Registro de fecha de compra
    hold_durations = []  # Lista para almacenar las duraciones de las posiciones
    buy_notification = 0
    total_percent = 0
    cp_out = 0

    # Simular las operaciones
    for date, group in df.groupby(level="Fecha"):
        close_prices = {
            ticker: group.loc[(date, ticker), ("Valor", "Close")]
            for ticker in portfolio.keys()
            if (date, ticker) in group.index
        }
        rsis = {
            ticker: group.loc[(date, ticker), ("Valor", "RSI")]
            for ticker in portfolio.keys()
            if (date, ticker) in group.index
        }
        atrs = {
            ticker: group.loc[(date, ticker), ("Valor", "ATR")]
            for ticker in portfolio.keys()
            if (date, ticker) in group.index
        }
        obvs = {
            ticker: group.loc[(date, ticker), ("Valor", "OBV")]
            for ticker in portfolio.keys()
            if (date, ticker) in group.index
        }
        vwaps = {
            ticker: group.loc[(date, ticker), ("Valor", "VWAP")]
            for ticker in portfolio.keys()
            if (date, ticker) in group.index
        }
        
        # Señales de compra y venta
        for ticker in portfolio.keys():
            if ticker in close_prices and ticker in rsis and ticker in atrs and ticker in obvs and ticker in vwaps:
                if not math.isnan(rsis[ticker]) and not math.isnan(close_prices[ticker]):
                    
                    # Estrategia de compra basada en RSI + ATR
                    if rsis[ticker] <= 25 and close_prices[ticker] < vwaps[ticker] and cash > 0:
                        if portfolio[ticker] == 0: 
                            amount_to_invest = initial_cash * 0.3
                            if amount_to_invest >= cash:
                                shares_to_buy = cash / close_prices[ticker]
                                cash = 0
                            else:
                                shares_to_buy = amount_to_invest / close_prices[ticker]  
                                cash -= amount_to_invest
                            portfolio[ticker] += shares_to_buy
                            buy_notification += 1
                            buy_prices[ticker] = close_prices[ticker]
                            buy_dates[ticker] = date

                    # Estrategia de venta basada en RSI + OBV
                    elif rsis[ticker] >= 70 and portfolio[ticker] > 0 and obvs[ticker] < 0:
                        cp_out = close_prices[ticker]
                        c = cp_out - buy_prices[ticker]
                        percent = (c / buy_prices[ticker]) * 100
                        total_percent += percent
                        cash += portfolio[ticker] * close_prices[ticker]
                        portfolio[ticker] = 0
                        hold_durations.append((date - buy_dates[ticker]).days)
                        buy_prices[ticker] = None
                        buy_dates[ticker] = None

                    # Estrategia de venta por Stop-Loss basado en ATR
                    elif (
                        buy_prices[ticker] is not None
                        and close_prices[ticker] < buy_prices[ticker] - (atrs[ticker] * 2)
                    ):
                        cp_out = close_prices[ticker]
                        c = cp_out - buy_prices[ticker]
                        percent = (c / buy_prices[ticker]) * 100
                        total_percent += percent
                        cash += portfolio[ticker] * close_prices[ticker]
                        portfolio[ticker] = 0
                        hold_durations.append((date - buy_dates[ticker]).days)
                        buy_prices[ticker] = None
                        buy_dates[ticker] = None

        # Valor actual de la cartera en cada paso
        current_value = cash + sum(
            portfolio[ticker] * close_prices[ticker]
            for ticker in portfolio.keys()
            if ticker in close_prices
        )
        # Crear un DataFrame temporal con la fecha y el valor del portafolio
        temp_df = pd.DataFrame(
            {"Fecha": [date], "Portfolio Value": [current_value]}
        ).dropna(how="all", axis=1)
        # Concatenar el DataFrame temporal al DataFrame de seguimiento
        df_portfolio_tracking = pd.concat(
            [df_portfolio_tracking, temp_df], ignore_index=True
        )

    if hold_durations:
        average_hold_duration = sum(hold_durations) / len(hold_durations)

    # Finalmente, visualizar o guardar los resultados
    print(df_portfolio_tracking)

    # Calcular max drawdown y rentabilidad
    df_portfolio_tracking["Peak"] = df_portfolio_tracking["Portfolio Value"].cummax()
    df_portfolio_tracking["Drawdown"] = (
        df_portfolio_tracking["Portfolio Value"] - df_portfolio_tracking["Peak"]
    )
    df_portfolio_tracking["Drawdown Percent"] = (
        df_portfolio_tracking["Drawdown"] / df_portfolio_tracking["Peak"]
    )
    # Maximum drawdown
    max_drawdown = df_portfolio_tracking["Drawdown Percent"].min()
    # Rentabilidad del portafolio
    final_portfolio_value = df_portfolio_tracking["Portfolio Value"].iloc[-1]
    profitability = (final_portfolio_value - initial_cash) / initial_cash * 100
    print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")
    print(f"Profitability: {profitability:.2f}%")
    total_months = await calculate_month_diff("2000-01-01")
    avg_notification = buy_notification / total_months
    print(f"Cantidad de alertas: {buy_notification}, meses totales: {total_months}, media: {avg_notification}")        
    print(f"Media de dias que se tiene una accion: {average_hold_duration}")
    print(f'Porcetaje total de las operaciones: {total_percent}')
    max_drawdown = round(max_drawdown * 100, 2)
    profitability = round(profitability, 2)
    avg_notification = round(avg_notification, 2)
    average_hold_duration = round(average_hold_duration, 2)
    
    return str(max_drawdown), str(profitability), str(average_hold_duration), str(avg_notification)




@router.message(Command(commands=["backtest", "BACKTEST", "Backtest", "BackTest"]))
async def backtest_handler(message: Message):

    max_drawdown, profitability, average_hold_duration, avg_notification = await calculate_maximum_drawdown_profit()
    
    msg = '🧪 BackTest 🧪\n\n' + f'🧮 Media de alertas mensuales: <b>{avg_notification}</b>\n' + f"🔹 Media de días que se mantiene una acción en cartera: <b>{average_hold_duration}</b>\n" + f'☠️ Maximum draw down: <b>{max_drawdown}%</b>\n' + f'💰 Rentabilidad: <b>{profitability}%</b>'
    
    await message.answer(str(msg), parse_mode='HTML')
           
    return