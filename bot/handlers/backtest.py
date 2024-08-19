from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os
import json
import pandas as pd
import math

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

    if type.startswith('MA'):
        date_ranges = {
        "2000": ("1999-09-01", "2004-12-30"),
        "2005": ("2004-09-01", "2009-12-30"),
        "2010": ("2009-09-01", "2014-12-30"),
        "2015": ("2014-09-01", "2019-12-30"),
        "2020": ("2019-09-01", (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"))  # Hasta ayer
        }
    print(f'{type}: {date_ranges}')
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
    data_ma50_raw = await load_data("data", "ma50", "MA50")
    data_ma20_raw = await load_data("data", "ma20", "MA20")

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

    ma50_data = {}

    for data in data_ma50_raw:
        symbol = data["Symbol"]
        if symbol not in data_ma50_raw:
            ma50_data[symbol] = {}

        for date, ma50 in data["MA50"].items():
            ma50_data[symbol][date] = ma50

    ma20_data = {}

    for data in data_ma20_raw:
        symbol = data["Symbol"]
        if symbol not in data_ma20_raw:
            ma20_data[symbol] = {}

        for date, ma20 in data["MA20"].items():
            ma20_data[symbol][date] = ma20

    df_rsi_close, df_ma50, df_ma20 = await get_dataframe(rsi_data, closing_prices, ma50_data, ma20_data)
    max_drawdown, profitability, average_hold_duration, avg_notification = await simulation(df_rsi_close, df_ma50, df_ma20)

    return max_drawdown, profitability, average_hold_duration, avg_notification

async def get_dataframe(rsi_data, close_data, ma50_data, ma20_data):

    # Crear un DataFrame para RSI y Close
    data_tuples = []
    for empresa, fechas in rsi_data.items():
        for fecha, valores in fechas.items():
            rsi = float(valores)
            close = (
                float(close_data[empresa][fecha]["close"])
                if fecha in close_data[empresa]
                else None
            )
            data_tuples.append((fecha, empresa, "RSI", rsi))
            data_tuples.append((fecha, empresa, "Close", close))

    df_rsi_close = pd.DataFrame(data_tuples, columns=["Fecha", "Empresa", "Tipo", "Valor"])
    df_rsi_close.set_index(["Fecha", "Empresa", "Tipo"], inplace=True)
    df_rsi_close.index = df_rsi_close.index.set_levels(pd.to_datetime(df_rsi_close.index.levels[0]), level=0)
    df_rsi_close = df_rsi_close.unstack(level="Tipo")
    df_rsi_close.sort_index(inplace=True)

    # Crear un DataFrame separado para MA50
    ma50_tuples = []
    for empresa, fechas in ma50_data.items():
        for fecha, valor in fechas.items():
            ma50_tuples.append((fecha, empresa, valor))

    df_ma50 = pd.DataFrame(ma50_tuples, columns=["Fecha", "Empresa", "MA50"])
    df_ma50.set_index(["Fecha", "Empresa"], inplace=True)
    df_ma50.index = df_ma50.index.set_levels(pd.to_datetime(df_ma50.index.levels[0]), level=0)
    df_ma50.sort_index(inplace=True)

    # Crear un DataFrame separado para MA20
    ma20_tuples = []
    for empresa, fechas in ma20_data.items():
        for fecha, valor in fechas.items():
            ma20_tuples.append((fecha, empresa, valor))

    df_ma20 = pd.DataFrame(ma20_tuples, columns=["Fecha", "Empresa", "MA20"])
    df_ma20.set_index(["Fecha", "Empresa"], inplace=True)
    df_ma20.index = df_ma20.index.set_levels(pd.to_datetime(df_ma20.index.levels[0]), level=0)
    df_ma20.sort_index(inplace=True)


    # Opcional: Eliminar filas donde todos los valores sean NaN en df_rsi_close
    df_rsi_close_clean = df_rsi_close.dropna(how='all')

    return df_rsi_close_clean, df_ma50, df_ma20

async def is_sma_trending(ma_short_series, ma_long_series, current_date):
    past_date_short = current_date - pd.Timedelta(days=20)  # SMA corta
    past_date_long = current_date - pd.Timedelta(days=50)   # SMA larga
    
    while past_date_short not in ma_short_series.index:
        past_date_short -= pd.Timedelta(days=1)
    
    while past_date_long not in ma_long_series.index:
        past_date_long -= pd.Timedelta(days=1)
    
    ma_short_current = ma_short_series.loc[current_date]
    ma_short_past = ma_short_series.loc[past_date_short]
    ma_long_current = ma_long_series.loc[current_date]
    ma_long_past = ma_long_series.loc[past_date_long]
    
    # Condición de tendencia alcista: SMA corta debe estar comenzando a subir y SMA corta debe estar a punto de cruzar SMA larga o ya cruzando
    return ma_short_current < ma_short_past and ma_short_current < ma_long_current

async def simulation(df, df_ma50, df_ma20):
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
        
        # Señales de compra y venta
        for ticker in portfolio.keys():
            if ticker in close_prices and ticker in rsis:
                if not math.isnan(rsis[ticker]) and not math.isnan(close_prices[ticker]):
                    if rsis[ticker] <= 25 and cash > 0:
                        # Verificar si la MA50 está en tendencia alcista
                        ma50_series = df_ma50.xs(ticker, level="Empresa")["MA50"]
                        ma20_series = df_ma20.xs(ticker, level="Empresa")["MA20"]
                        # if await is_sma_trending(ma20_series, ma50_series, date):
                        # Comprar si no hay acciones de este ticker en cartera
                        if portfolio[ticker] == 0: 
                            print(f'Cash antes de comprar: {cash}')
                            # Calcular el monto a invertir y las acciones fraccionarias a comprar
                            amount_to_invest = initial_cash * 0.3
                            if amount_to_invest >= cash:
                                print(f'Cash: {cash} mas pequeño que cantidad a invertir: {amount_to_invest}')
                                shares_to_buy = cash / close_prices[ticker]
                                cash = 0
                            else:
                                print(f'Cash: {cash} mas grande que cantidad a invertir: {amount_to_invest}')
                                shares_to_buy = amount_to_invest / close_prices[ticker]  
                                cash -= amount_to_invest
                            print(f'Ticker: {ticker}, precio de cierre: {close_prices[ticker]}, rsi: {rsis[ticker]}, fecha: {date}')
                            print(f'Cantidad a invertir: {amount_to_invest}')
                            print(f'Cantidad de acciones a comprar: {shares_to_buy}')
                            # Realizar la compra fraccionaria
                            portfolio[ticker] += shares_to_buy  # Comprar las acciones fraccionarias
                            buy_notification += 1
                            buy_prices[ticker] = close_prices[ticker]
                            buy_dates[ticker] = date  # Registrar la fecha de la primera compra
                            print(f'Cash despues de comprar: {cash}')
                    elif rsis[ticker] >= 75 and portfolio[ticker] > 0:
                        print(f'Venta con beneficios de ticker: {ticker}, precio: {close_prices[ticker]}, fecha: {date}')
                        cp_out = close_prices[ticker]
                        c = cp_out - buy_prices[ticker]
                        percent = (c / buy_prices[ticker]) * 100
                        print(f'Porcentaje de la operacion: {percent}')
                        total_percent += percent
                        print(f'Total percent: {total_percent}')

                        cash += portfolio[ticker] * close_prices[ticker] # Vender todas las acciones
                        portfolio[ticker] = 0
                        # Calcular duración de retención y añadir a la lista
                        hold_durations.append((date - buy_dates[ticker]).days)
                        buy_prices[ticker] = None
                        buy_dates[ticker] = (
                            None  # Limpiar la fecha de compra registrada
                        ) 
                    elif (
                        buy_prices[ticker] is not None
                        and close_prices[ticker] < buy_prices[ticker] * 0.9
                    ):
                        print(f'Venta con perdidas de ticker: {ticker}, precio: {close_prices[ticker]}, fecha: {date}')
                        cp_out = close_prices[ticker]
                        c = cp_out - buy_prices[ticker]
                        percent = (c / buy_prices[ticker]) * 100
                        print(f'Porcentaje de la operacion: {percent}')
                        a = total_percent + percent
                        print(f'Esto es A: {a}')
                        total_percent = a
                        print(f'Total percent: {total_percent}')
                      
                        cash += portfolio[ticker] * close_prices[ticker] # Vender todas las acciones
                        portfolio[ticker] = 0
                        # Calcular duración de retención y añadir a la lista
                        hold_durations.append((date - buy_dates[ticker]).days)
                        buy_prices[ticker] = None
                        buy_dates[ticker] = (
                            None  # Limpiar la fecha de compra registrada
                        )

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
    # Finalmente, puedes visualizar el DataFrame o utilizarlo para cálculos adicionales
    print(df_portfolio_tracking)
    # with open('output.txt', 'w') as f:
    #     print(df_portfolio_tracking, file=f)
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