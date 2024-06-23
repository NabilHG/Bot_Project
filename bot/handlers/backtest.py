from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.formatting import Text, Bold
from bot import config
from datetime import datetime
from dateutil.relativedelta import relativedelta
from aiohttp_socks import ProxyType, ProxyConnector
import aiohttp
import asyncio
import os
import json
import random
import ssl
import certifi

router = Router()


async def load_dummy_data():
    data_list = []
    # folder_path = '..\\..\\dummy_data'
    folder_path = r"C:\Users\Nabil\Desktop\bot_project\dummy_data"
    print(folder_path)
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r") as file:
                data = json.load(file)
                data_list.append(data)

    return data_list


async def get_proxy(session, message):
    url = "https://api.proxyscrape.com/v3/free-proxy-list/get?request=displayproxies&country=us,es,fr,it,ca,pt,gb,de&protocol=socks4&proxy_format=ipport&format=text&anonymity=Elite&timeout=819"
    print(url)
    async with session.get(url) as response:
        if response.status == 200:
            try:
                data = await response.text()
                if not data:
                    await message.answer(
                        **Text(
                            "⚠️ Servidor para hacer Backtest ",
                            Bold("no encontrado"),
                            " prueba más tarde",
                        ).as_kwargs()
                    )
                    return None
                return data.strip().split(
                    "\n"
                )  # Divide el texto por líneas para obtener una lista de proxies
            except Exception as e:
                print("Error decoding JSON:", e)
                return None
        else:
            await message.answer(
                **Text(
                    "⚠️ Servidor para hacer Backtest ",
                    Bold("no encontrado"),
                    " prueba más tarde",
                ).as_kwargs()
            )
            return None


"""TODO get more alpha vantage keys and swap them when monthly_action_counts is empty"""


async def fetch_rsi(session, symbol, message, proxy_ip, proxy_port):
    api_key = config.ALPHA_VANTAGE_API_KEY
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "RSI",
        "symbol": symbol,
        "interval": "daily",
        "time_period": 10,
        "series_type": "close",
        "apikey": api_key,
    }

    # proxies = await get_proxy(session, message)
    # proxy = random.choice(proxies).strip()  # Elige un proxy al azar y quita espacios en blanco
    # print(proxy, "TESTETTEST")
    # proxy_ip, proxy_port = proxy.split(':')  # Divide el proxy en IP y puerto
    print(f"Selected Proxy: IP={proxy_ip}, Port={proxy_port}")

    # Configuración del contexto SSL con certificados confiables
    ssl_context = ssl.create_default_context(cafile=certifi.where())

    # Configuración del TCPConnector con el contexto SSL
    connector = aiohttp.TCPConnector(
        ssl_context=ssl_context,
        limit=None,  # Sin límite de conexiones
        verify_ssl=True,  # Verificar SSL
        use_dns_cache=True,  # Usar caché DNS
    )

    # Configuración del ProxyConnector con el TCPConnector
    proxy_connector = ProxyConnector(
        proxy_type=ProxyType.SOCKS4,
        host=proxy_ip,
        port=int(proxy_port),
        rdns=True,  # Resolver DNS remoto
    )

    async with aiohttp.ClientSession(connector=connector) as session:
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


async def get_monthly_alerts_counts(symbols, message):
    # print(symbols)
    monthly_action_counts = {}
    async with aiohttp.ClientSession() as session:
        proxies = await get_proxy(session, message)
        proxy = random.choice(proxies).strip()
        proxy_ip, proxy_port = proxy.split(":")

        if proxy:
            tasks = [
                fetch_rsi(session, symbol, message, proxy_ip, proxy_port)
                for symbol in symbols
            ]
            responses = await asyncio.gather(*tasks)

            # print(responses)

            # responses = await load_dummy_data()
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
        print(total_months, "MONTHS")
        average_rsi_below_25 = round(total_actions_rsi_below_25 / total_months, 2)

        # result should be a dictionary to store the averages
        result = {
            "avg_below_25": average_rsi_below_25,
        }
    return result


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

    data = await get_monthly_alerts_counts(symbols, message)
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
