from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import datetime
import os
import json
import pandas as pd
import math

router = Router()


async def load_data(base_path, subfolder_name):
    data_list = []
    # Recorrer todas las subcarpetas del segundo nivel
    for year_folder in os.listdir(base_path):
        year_folder_path = os.path.join(base_path, year_folder)
        # Verificar si la carpeta del año es un directorio
        if os.path.isdir(year_folder_path):
            target_folder_path = os.path.join(year_folder_path, subfolder_name)
            # Verificar si la carpeta deseada existe dentro de la carpeta del año
            if os.path.isdir(target_folder_path):
                # Cargar todos los archivos JSON dentro de la carpeta deseada
                for filename in os.listdir(target_folder_path):
                    if filename.endswith(".json"):
                        file_path = os.path.join(target_folder_path, filename)
                        with open(file_path, "r") as file:
                            data = json.load(file)
                            data_list.append(data)

    return data_list


async def calculate_month_diff(begin_date):

    ancient_date = datetime.strptime(f"{begin_date}", "%Y-%m-%d")

    current_date = datetime.now()

    delta = relativedelta(current_date, ancient_date)

    total_months = delta.years * 12 + delta.months

    return total_months


async def calculate_maximum_drawdown():
    maximum_drawdown = {}
    data_close_price_raw = await load_data("data", "close_price")
    data_rsi_raw = await load_data("data", "rsi")

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

    df = await get_dataframe(rsi_data, closing_prices)
    await simulation(df)

    return maximum_drawdown


async def get_dataframe(rsi_data, close_data):

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

    # Crear un DataFrame a partir de las tuplas
    df = pd.DataFrame(data_tuples, columns=["Fecha", "Empresa", "Tipo", "Valor"])

    # Convertir el DataFrame en uno con MultiIndex
    df.set_index(["Fecha", "Empresa", "Tipo"], inplace=True)

    df.index = df.index.set_levels(pd.to_datetime(df.index.levels[0]), level=0)
    df = df.unstack(level="Tipo")
    df.sort_index(inplace=True)
    df_clear = df.dropna()
    # with open('output.txt', 'w') as f:
    #     print(df_clear, file=f)
    return df_clear


# ONCE A SHARE IS BUYED, WE CAN NOT BUY IT AGAIN UNTIL WE SELL IT?


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
    buy_notification_2020 = 0
    hold_durations_2020 = []  # Lista para almacenar las duraciones de las posiciones

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
                if not math.isnan(rsis[ticker]) and not math.isnan(
                    close_prices[ticker]
                ):
                    if rsis[ticker] <= 25 and cash > 0:
                        # Comprar si no hay acciones de este ticker en cartera
                        if portfolio[ticker] == 0: 
                            
                            if date.year == 2020 or date.year == 2021 or date.year == 2022 or date.year == 2023 or date.year == 2024:
                                buy_notification_2020 += 1


                            if cash >= close_prices[ticker]:
                                cash -= close_prices[ticker]
                            else:
                                print(f'Fecha: {date}, ticker: {ticker}, close_price: {close_prices[ticker]}, rsi: {rsis[ticker]}, cash: {cash}')
                                cash = 0
                            
                            buy_notification += 1
                            portfolio[ticker] = 1  # Comprar una acción
                            buy_prices[ticker] = close_prices[ticker]
                            buy_dates[ticker] = date  # Registrar la fecha de compra
                    elif rsis[ticker] > 70 and portfolio[ticker] > 0:
                        cash += portfolio[ticker] * close_prices[ticker] # Vender todas las acciones
                        portfolio[ticker] = 0
                        # Calcular duración de retención y añadir a la lista
                        hold_durations.append((date - buy_dates[ticker]).days)
                        if date.year == 2020 or date.year == 2021 or date.year == 2022 or date.year == 2023 or date.year == 2024:
                            if buy_dates[ticker] is not None and isinstance(buy_dates[ticker], pd.Timestamp):
                                print(f'Fecha: {type(date)}, lo otro: {type(buy_dates[ticker])}')
                                hold_durations_2020.append((date - buy_dates[ticker]).days)
                            else:
                                print(f'Fecha: {type(date)}, lo otro: {type(buy_dates[ticker])}')
                                print(f'El valor de {buy_dates[ticker]} es None o no es un Timestamp válido.')
                        buy_prices[ticker] = None
                        buy_dates[ticker] = (
                            None  # Limpiar la fecha de compra registrada
                        )
                    elif (
                        buy_prices[ticker] is not None
                        and close_prices[ticker] < buy_prices[ticker] * 0.9
                    ):
                        cash += portfolio[ticker] * close_prices[ticker] # Vender todas las acciones
                        portfolio[ticker] = 0
                        # Calcular duración de retención y añadir a la lista
                        hold_durations.append((date - buy_dates[ticker]).days)
                        if date.year == 2020 or date.year == 2021 or date.year == 2022 or date.year == 2023 or date.year == 2024:
                            if buy_dates[ticker] is not None and isinstance(buy_dates[ticker], pd.Timestamp):
                                print(f'Fecha: {type(date)}, lo otro: {type(buy_dates[ticker])}')
                                hold_durations_2020.append((date - buy_dates[ticker]).days)
                            else:
                                print(f'Fecha: {type(date)}, lo otro: {type(buy_dates[ticker])}')
                                print(f'El valor de {buy_dates[ticker]} es None o no es un Timestamp válido.')
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
        # temp_df_cleaned = temp_df.dropna(how='all', axis=1)
        # Concatenar el DataFrame temporal al DataFrame de seguimiento
        df_portfolio_tracking = pd.concat(
            [df_portfolio_tracking, temp_df], ignore_index=True
        )

    if hold_durations:
        average_hold_duration = sum(hold_durations) / len(hold_durations)

    if hold_durations_2020:
        average_hold_duration_2020 = sum(hold_durations_2020) / len(hold_durations_2020)

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
    total_months_2020 = await calculate_month_diff("2020-01-01")
    print(f"Cantidad de alertas: {buy_notification}, meses totales: {total_months}, media: {buy_notification/total_months}")        
    print(f"Cantidad de alertas a partir del 2020: {buy_notification_2020}, meses totales: {total_months_2020}, media: {buy_notification_2020/total_months_2020}")
    print(f"Media de dias que se tiene una accion: {average_hold_duration}")
    print(f"Media de dias que se tiene una accion a partir del 2020: {average_hold_duration_2020}")


@router.message(Command(commands=["backtest", "BACKTEST", "Backtest", "BackTest"]))
async def backtest_handler(message: Message):

    a = await calculate_maximum_drawdown()

    print(a, "AAAAAAA")
    # print(result_avg_alerts)
    # if result_avg_alerts:
    #     symb_msg = ", ".join(symbols)
    #     await message.answer(
    #         **Text(
    #             f"🧪BackTest\nEmpresas analizadas: {symb_msg}🧪",
    #             "\n🧮 Media de alertas mensuales: \n" "🔹 Compra: ",
    #             Bold(result_avg_alerts["avg_below_25"]),
    #         ).as_kwargs()
    #     )

    return