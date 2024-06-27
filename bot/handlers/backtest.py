from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold
from bot import config
from datetime import datetime
from dateutil.relativedelta import relativedelta
import aiohttp
import asyncio
import os
import json
import random


router = Router()


async def load_dummy_data():
    data_list = []
    # folder_path = '..\\..\\dummy_data'
    folder_path = r"C:\Users\Nabil\Desktop\bot_project\dummy_data"
    # print(folder_path)
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                data_list.append(data)

    return data_list


"""TODO get more alpha vantage keys and swap them when monthly_action_counts is empty"""


async def fetch_rsi(session, symbol, message, current_api_key_index):
    api_key = config.ALPHA_VANTAGE_API_KEY
    # api_key = config.get_next_api_key(current_api_key_index)
    print(api_key, "KEY")
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "RSI",
        "symbol": symbol,
        "interval": "daily",
        "time_period": 10,
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


async def get_monthly_alerts_counts(symbols, message, current_api_key_index):
    # print(symbols)
    monthly_action_counts = {}
    async with aiohttp.ClientSession() as session:
        tasks = [
            fetch_rsi(
                session,
                symbol,
                message,
                current_api_key_index,
            )
            for symbol in symbols
        ]
        responses = await asyncio.gather(*tasks)

        # substring = "rate limit is 25 requests per day"

        # if await contains_info(responses, substring):
        #     print("CONTAINS")
        #     current_api_key_index += 1
        #     await get_monthly_alerts_counts(symbols, message, current_api_key_index)
        # else:
        #     print("NOT CONTAINS")

        # responses = await load_dummy_data()
        print(responses, "????")

        has_none = any(
            filter(lambda x: x is None, responses)
        )  # if true, not calculating backtest
        if not has_none:
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
    
    print(monthly_action_counts, "HERE")

    return monthly_action_counts


async def calculate_month_diff():
    # First date with info
    ancient_date = datetime.strptime("1999-11-15", "%Y-%m-%d")

    current_date = datetime.now()

    # Calculate difference
    delta = relativedelta(current_date, ancient_date)

    total_months = delta.years * 12 + delta.months

    return total_months


async def calculate_monthly_avg_alerts(data):
    print(data, "DATA")
    result = {}
    if data:
        # data is a dictionary, so use its values
        total_actions_rsi_below_25 = sum(
            entry["RSI below 25"] for entry in data.values()
        )

        # total_months = len(data)
        total_months = await calculate_month_diff()
        # print(total_months, "MONTHS")
        average_rsi_below_25 = round(total_actions_rsi_below_25 / total_months, 2)

        # result should be a dictionary to store the averages
        result = {
            "avg_below_25": average_rsi_below_25,
        }
    return result


current_api_key_index = 0


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
                " de las empresas.\nEjemplo: /backtest AAPL,GOOGL,MSFT o /backtest AAPL GOOGL MSFT",
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

    data = await get_monthly_alerts_counts(symbols, message, current_api_key_index)
    result_avg_alerts = await calculate_monthly_avg_alerts(data)
    print(result_avg_alerts)
    if result_avg_alerts:
        symb_msg = ", ".join(symbols)
        await message.answer(
            **Text(
                f"🧪BackTest\nEmpresas analizadas: {symb_msg}",
                "\n🧮 Media de alertas mensuales: \n" "🔹 Compra: ",
                Bold(result_avg_alerts["avg_below_25"]),
            ).as_kwargs()
        )
    return


# TODO
# Trim code, only is necessary show avg alerts when rsi < 25
# make a file with all the symbols of all bussines. Before executing a call,
# verify the symbols exists in symbols_list.json

"""
    iterate through all symbols, for each one, execute backtest
    backtest: 
      ✅-avarage number of actions monthly, when rsi is lower than 25 (rsi < 25), or rsi is higher than 70 (rsi > 70), that's an action
      -maximum drawdown
      -profit yearly 
"""
