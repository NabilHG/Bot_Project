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


async def fetch_rsi(session, symbol, message):
    api_key = config.ALPHA_VANTAGE_API_KEY
    print(api_key)
    url = f"https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=daily&time_period=10&series_type=close&apikey={api_key}"
    print(url)
    async with session.get(url) as response:
        if response.status == 200:
            try:
                data = await response.json()
                if not data:
                    await message.answer(
                        **Text(
                            "⚠️ Simbolo: ",
                            Bold(symbol),
                            " no encontrado ❗️❗️\n", Bold("Backtest cancelado")
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
        # tasks = [fetch_rsi(session, symbol, message) for symbol in symbols]
        # responses = await asyncio.gather(*tasks)

        # responses = [
        #     {
        #         "Meta Data": {
        #             "1: Symbol": "AAPL",
        #             "2: Indicator": "Relative Strength Index (RSI)",
        #             "3: Last Refreshed": "2024-06-11",
        #             "4: Interval": "daily",
        #             "5: Time Period": 10,
        #             "6: Series Type": "close",
        #             "7: Time Zone": "US/Eastern Time",
        #         },
        #         "Technical Analysis: RSI": {
        #             "2024-06-11": {"RSI": "77.5889"},
        #             "2024-06-10": {"RSI": "57.7764"},
        #             "2024-06-07": {"RSI": "73.4878"},
        #             "2024-06-06": {"RSI": "68.5706"},
        #             "2024-06-05": {"RSI": "75.8756"},
        #             "2024-06-04": {"RSI": "73.0500"},
        #             "2024-06-03": {"RSI": "72.4383"},
        #             "2024-05-31": {"RSI": "68.9053"},
        #             "2024-05-30": {"RSI": "66.8422"},
        #             "2024-05-29": {"RSI": "64.6429"},
        #             "2024-05-28": {"RSI": "63.9981"},
        #             "2024-05-24": {"RSI": "63.9784"},
        #             "2024-05-23": {"RSI": "57.4860"},
        #             "2024-05-22": {"RSI": "72.7997"},
        #             "2024-05-21": {"RSI": "79.6911"},
        #             "2024-05-20": {"RSI": "77.9976"},
        #             "2024-05-17": {"RSI": "76.4168"},
        #             "2024-05-16": {"RSI": "76.3776"},
        #             "2024-05-15": {"RSI": "76.2355"},
        #             "2024-05-14": {"RSI": "73.4978"},
        #             "2024-05-13": {"RSI": "72.0422"},
        #             "2024-05-10": {"RSI": "67.5345"},
        #             "2024-05-09": {"RSI": "71.6149"},
        #             "2024-05-08": {"RSI": "69.2017"},
        #             "2024-05-07": {"RSI": "68.7575"},
        #             "2024-05-06": {"RSI": "67.9124"},
        #             "2024-05-03": {"RSI": "72.1648"},
        #             "2024-05-02": {"RSI": "57.2252"},
        #             "2024-05-01": {"RSI": "48.2094"},
        #             "2024-04-30": {"RSI": "50.8743"},
        #             "2024-04-29": {"RSI": "60.0723"},
        #             "2024-04-26": {"RSI": "49.0985"},
        #             "2024-04-25": {"RSI": "50.8660"},
        #             "2024-04-24": {"RSI": "48.4009"},
        #             "2024-04-23": {"RSI": "42.0214"},
        #             "2024-04-22": {"RSI": "38.6056"},
        #             "2024-04-19": {"RSI": "35.9128"},
        #             "2024-04-18": {"RSI": "39.7207"},
        #             "2024-04-17": {"RSI": "41.5884"},
        #             "2024-04-16": {"RSI": "44.2821"},
        #             "2024-04-15": {"RSI": "51.4801"},
        #             "2024-04-12": {"RSI": "62.0693"},
        #             "2024-04-11": {"RSI": "59.1079"},
        #             "2024-04-10": {"RSI": "38.2448"},
        #             "2024-04-09": {"RSI": "43.4372"},
        #             "2024-04-08": {"RSI": "38.5938"},
        #             "2024-04-05": {"RSI": "41.5604"},
        #             "2024-04-04": {"RSI": "38.7086"},
        #             "2024-04-03": {"RSI": "40.6587"},
        #             "2024-04-02": {"RSI": "37.9113"},
        #             "2024-04-01": {"RSI": "40.3835"},
        #             "2024-03-28": {"RSI": "43.4938"},
        #             "2024-03-27": {"RSI": "47.6635"},
        #             "2024-03-26": {"RSI": "36.9640"},
        #             "2024-03-25": {"RSI": "39.2509"},
        #             "2024-03-22": {"RSI": "42.1984"},
        #             "2024-03-21": {"RSI": "39.6008"},
        #             "2024-03-20": {"RSI": "58.6208"},
        #             "2024-03-19": {"RSI": "51.1251"},
        #             "2024-03-18": {"RSI": "42.5977"},
        #             "2024-03-15": {"RSI": "38.0646"},
        #             "2024-03-14": {"RSI": "39.0227"},
        #             "2024-03-13": {"RSI": "31.3722"},
        #             "2024-03-12": {"RSI": "35.9282"},
        #             "2024-03-11": {"RSI": "33.9551"},
        #             "2024-03-08": {"RSI": "25.2350"},
        #             "2024-03-07": {"RSI": "16.7641"},
        #             "2024-03-06": {"RSI": "16.8836"},
        #             "2024-03-05": {"RSI": "17.8365"},
        #             "2024-03-04": {"RSI": "23.8766"},
        #             "2024-03-01": {"RSI": "33.1190"},
        #             "2024-02-29": {"RSI": "36.1276"},
        #             "2024-02-28": {"RSI": "38.0392"},
        #             "2024-02-27": {"RSI": "41.6186"},
        #             "2024-02-26": {"RSI": "34.9232"},
        #             "2024-02-23": {"RSI": "38.6102"},
        #             "2024-02-22": {"RSI": "44.3412"},
        #             "2024-02-21": {"RSI": "34.6703"},
        #             "2024-02-20": {"RSI": "30.6497"},
        #             "2024-02-16": {"RSI": "32.4219"},
        #             "2024-02-15": {"RSI": "36.3289"},
        #             "2024-02-14": {"RSI": "37.0813"},
        #             "2024-02-13": {"RSI": "39.3313"},
        #             "2024-02-12": {"RSI": "45.1808"},
        #             "2024-02-09": {"RSI": "50.6422"},
        #             "2024-02-08": {"RSI": "48.0874"},
        #             "2024-02-07": {"RSI": "51.4824"},
        #             "2024-02-06": {"RSI": "51.1693"},
        #             "2024-02-05": {"RSI": "46.6016"},
        #             "2024-02-02": {"RSI": "40.9896"},
        #             "2024-02-01": {"RSI": "43.2473"},
        #             "2024-01-31": {"RSI": "35.4542"},
        #             "2024-01-30": {"RSI": "43.3884"},
        #             "2024-01-29": {"RSI": "54.5201"},
        #             "2024-01-26": {"RSI": "56.9803"},
        #             "2024-01-25": {"RSI": "63.5235"},
        #             "2024-01-24": {"RSI": "64.7861"},
        #             "2024-01-23": {"RSI": "67.2655"},
        #             "2024-01-22": {"RSI": "64.9770"},
        #             "2024-01-19": {"RSI": "60.4864"},
        #             "2024-01-18": {"RSI": "53.7793"},
        #             "2024-01-17": {"RSI": "32.9911"},
        #             "2024-01-16": {"RSI": "35.2706"},
        #             "2024-01-12": {"RSI": "41.4899"},
        #             "2024-01-11": {"RSI": "40.1205"},
        #             "2024-01-10": {"RSI": "41.7183"},
        #             "2024-01-09": {"RSI": "37.8181"},
        #             "2024-01-08": {"RSI": "38.7517"},
        #             "2024-01-05": {"RSI": "20.2816"},
        #             "2024-01-04": {"RSI": "21.2425"},
        #             "2024-01-03": {"RSI": "24.6056"},
        #             "2024-01-02": {"RSI": "26.8808"},
        #             "2023-12-29": {"RSI": "45.7548"},
        #             "2023-12-28": {"RSI": "50.6306"},
        #             "2023-12-27": {"RSI": "48.6123"},
        #             "2023-12-26": {"RSI": "48.1687"},
        #             "2023-12-22": {"RSI": "50.3184"},
        #             "2023-12-21": {"RSI": "54.6268"},
        #             "2023-12-20": {"RSI": "55.2178"},
        #             "2023-12-19": {"RSI": "63.9809"},
        #             "2023-12-18": {"RSI": "61.2249"},
        #             "2023-12-15": {"RSI": "68.8061"},
        #             "2023-12-14": {"RSI": "71.3623"},
        #             "2023-12-13": {"RSI": "71.0939"},
        #             "2023-12-12": {"RSI": "64.6273"},
        #             "2023-12-11": {"RSI": "60.9235"},
        #             "2023-12-08": {"RSI": "72.1697"},
        #             "2023-12-07": {"RSI": "69.2633"},
        #             "2023-12-06": {"RSI": "64.7805"},
        #             "2023-12-05": {"RSI": "69.9607"},
        #             "2023-12-04": {"RSI": "59.3487"},
        #             "2023-12-01": {"RSI": "69.3512"},
        #             "2023-11-30": {"RSI": "65.6363"},
        #             "2023-11-29": {"RSI": "63.8639"},
        #             "2023-11-28": {"RSI": "69.6014"},
        #             "2023-11-27": {"RSI": "68.0726"},
        #             "2023-11-24": {"RSI": "68.9941"},
        #             "2023-11-22": {"RSI": "75.8763"},
        #             "2023-11-21": {"RSI": "74.7425"},
        #             "2023-11-20": {"RSI": "78.7705"},
        #             "2023-11-17": {"RSI": "76.2696"},
        #             "2023-11-16": {"RSI": "76.3616"},
        #             "2023-11-15": {"RSI": "73.9586"},
        #             "2023-11-14": {"RSI": "73.1344"},
        #             "2023-11-13": {"RSI": "69.0516"},
        #             "2023-11-10": {"RSI": "75.2929"},
        #             "2023-11-09": {"RSI": "68.5346"},
        #             "2023-11-08": {"RSI": "70.5042"},
        #             "2023-11-07": {"RSI": "68.6995"},
        #             "2023-11-06": {"RSI": "63.8859"},
        #             "2023-11-03": {"RSI": "58.1103"},
        #             "2023-11-02": {"RSI": "61.2542"},
        #             "2023-11-01": {"RSI": "52.1342"},
        #             "2023-10-31": {"RSI": "41.0300"},
        #             "2023-10-30": {"RSI": "39.1235"},
        #             "2023-10-27": {"RSI": "30.3884"},
        #             "2023-10-26": {"RSI": "24.0898"},
        #             "2023-10-25": {"RSI": "32.4560"},
        #             "2023-10-24": {"RSI": "39.2801"},
        #             "2023-10-23": {"RSI": "37.0399"},
        #             "2023-10-20": {"RSI": "36.4645"},
        #             "2023-10-19": {"RSI": "44.2979"},
        #             "2023-10-18": {"RSI": "45.5963"},
        #             "2023-10-17": {"RSI": "50.1577"},
        #             "2023-10-16": {"RSI": "56.2246"},
        #             "2023-10-13": {"RSI": "56.7360"},
        #             "2023-10-12": {"RSI": "64.2631"},
        #             "2023-10-11": {"RSI": "62.0459"},
        #             "2023-10-10": {"RSI": "58.4513"},
        #             "2023-10-09": {"RSI": "60.6512"},
        #             "2023-10-06": {"RSI": "57.0108"},
        #             "2023-10-05": {"RSI": "49.8248"},
        #             "2023-10-04": {"RSI": "45.8800"},
        #             "2023-10-03": {"RSI": "41.7236"},
        #             "2023-10-02": {"RSI": "45.0607"},
        #             "2023-09-29": {"RSI": "36.4544"},
        #             "2023-09-28": {"RSI": "34.5657"},
        #             "2023-09-27": {"RSI": "33.6787"},
        #             "2023-09-26": {"RSI": "36.2837"},
        #             "2023-09-25": {"RSI": "44.6541"},
        #             "2023-09-22": {"RSI": "40.8060"},
        #             "2023-09-21": {"RSI": "38.2291"},
        #             "2023-09-20": {"RSI": "41.1539"},
        #             "2023-09-19": {"RSI": "48.8776"},
        #             "2023-09-18": {"RSI": "46.0791"},
        #             "2023-09-15": {"RSI": "37.8382"},
        #             "2023-09-14": {"RSI": "39.1669"},
        #             "2023-09-13": {"RSI": "34.8517"},
        #             "2023-09-12": {"RSI": "38.1814"},
        #             "2023-09-11": {"RSI": "43.6804"},
        #             "2023-09-08": {"RSI": "40.7172"},
        #             "2023-09-07": {"RSI": "39.2046"},
        #             "2023-09-06": {"RSI": "48.8928"},
        #             "2023-09-05": {"RSI": "68.1216"},
        #             "2023-09-01": {"RSI": "67.7177"},
        #             "2023-08-31": {"RSI": "65.0798"},
        #             "2023-08-30": {"RSI": "64.7208"},
        #             "2023-08-29": {"RSI": "58.5702"},
        #             "2023-08-28": {"RSI": "49.8012"},
        #             "2023-08-25": {"RSI": "45.6378"},
        #             "2023-08-24": {"RSI": "39.2363"},
        #             "2023-08-23": {"RSI": "50.6451"},
        #             "2023-08-22": {"RSI": "37.1462"},
        #             "2023-08-21": {"RSI": "31.0845"},
        #             "2023-08-18": {"RSI": "24.7401"},
        #             "2023-08-17": {"RSI": "22.4067"},
        #             "2023-08-16": {"RSI": "26.2483"},
        #             "2023-08-15": {"RSI": "27.7125"},
        #             "2023-08-14": {"RSI": "31.3021"},
        #             "2023-08-11": {"RSI": "23.9348"},
        #             "2023-08-10": {"RSI": "23.6704"},
        #             "2023-08-09": {"RSI": "23.9450"},
        #             "2023-08-08": {"RSI": "25.9259"},
        #             "2023-08-07": {"RSI": "22.5221"},
        #             "2023-08-04": {"RSI": "26.0882"},
        #             "2023-08-03": {"RSI": "44.7192"},
        #             "2023-08-02": {"RSI": "49.6175"},
        #             "2023-08-01": {"RSI": "62.9261"},
        #             "2023-07-31": {"RSI": "67.4762"},
        #             "2023-07-28": {"RSI": "65.8453"},
        #             "2023-07-27": {"RSI": "57.8348"},
        #             "2023-07-26": {"RSI": "64.5132"},
        #             "2023-07-25": {"RSI": "61.7826"},
        #             "2023-07-24": {"RSI": "58.9737"},
        #             "2023-07-21": {"RSI": "56.2812"},
        #             "2023-07-20": {"RSI": "61.6291"},
        #             "2023-07-19": {"RSI": "71.7928"},
        #             "2023-07-18": {"RSI": "68.5461"},
        #             "2023-07-17": {"RSI": "69.9208"},
        #             "2023-07-14": {"RSI": "60.9828"},
        #             "2023-07-13": {"RSI": "60.5027"},
        #             "2023-07-12": {"RSI": "58.1218"},
        #             "2023-07-11": {"RSI": "52.4614"},
        #             "2023-07-10": {"RSI": "54.5421"},
        #             "2023-07-07": {"RSI": "63.3783"},
        #             "2023-07-06": {"RSI": "68.8592"},
        #             "2023-07-05": {"RSI": "67.7944"},
        #             "2023-07-03": {"RSI": "73.0891"},
        #         },
        #     }
        # ]

        # print(responses)
        responses = await load_dummy_data()
        has_none = any(filter(lambda x: x is None, responses))
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
        total_actions_rsi_below_25 = sum(entry["RSI below 25"] for entry in data.values())

        # total_months = len(data)
        total_months = await calculate_month_diff()
        print(total_months, "MONTHS")
        average_rsi_below_25 = round(total_actions_rsi_below_25 / total_months, 2)

        # result should be a dictionary to store the averages
        result = {
            "avg_below_25": average_rsi_below_25,
        }
    return result


@router.message(Command(commands=["backtest"]))
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


"""
    iterate through all symbols, for each one, execute backtest
    backtest: 
      ✅-avarage number of actions monthly, when rsi is lower than 25 (rsi < 25), or rsi is higher than 70 (rsi > 70), that's an action
      -maximum drawdown
      -profit yearly 
"""
