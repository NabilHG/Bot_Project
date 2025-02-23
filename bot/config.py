from dotenv import load_dotenv
from os import getenv

load_dotenv(override=True)
# Token Telgram bot
BOT_TOKEN = getenv("BOT_TOKEN")

FIRST_ADMIN = getenv("FIRST_ADMIN")

#db url
MYSQL_ROOT_PASSWORD= getenv("MYSQL_ROOT_PASSWORD")
MYSQL_DATABASE= getenv("MYSQL_DATABASE")

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": "db", 
                "port": 3306,
                "user": "root",
                "password": MYSQL_ROOT_PASSWORD, 
                "database": MYSQL_DATABASE , 
                "minsize": 1,  
                "maxsize": 1,  
            },
        }
    },
    "apps": {
        "models": {
            "models": ["bot.db.models"],
            "default_connection": "default",
        }
    },
}

#dict with all tickers
MATRIX = {
    "2000": ["MSFT", "GE", "CSCO", "WMT", "XOM", "INTC", "C", "PFE", "NOK", "TM", "DTE", "HD", "ORCL", "MRK"],
    "2005": ["XOM", "GE", "MSFT", "C", "BP", "SHEL", "TM", "WMT", "IBM", "JNJ", "COP", "INTC", "AIG", "PFE"],
    "2010": ["XOM", "MSFT", "AAPL", "GE", "WMT", "BRK-B", "PG", "BAC", "JNJ", "WFC", "GOOG", "KO", "CVX", "PFE", "CSCO"],
    "2015": ["AAPL", "GOOG", "XOM", "BRK-B", "MSFT", "WFC", "JNJ", "NVS", "WMT", "GE", "PG", "JPM", "CVX", "ORCL", "VZ"],
    "2020": ["AAPL", "MSFT", "AMZN", "GOOG", "META", "BRK-B", "TSM", "ASML", "TSLA", "BABA", "JPM", "V", "MA", "UNH", "HD"],
    "2025": ["MSFT", "AAPL", "NVDA", "GOOG", "AMZN", "META", "BRK-B", "LLY", "AVGO", "TSM", "NVO", "JPM"],
}


FIRST_ADMIN = getenv("FIRST_ADMIN")
SECOND_ADMIN = getenv("SECOND_ADMIN")

# External API keys
ALPHA_VANTAGE_API_KEYS = [
    getenv("ALPHA_VANTAGE_API_KEY_1"),
    getenv("ALPHA_VANTAGE_API_KEY_2"),
    getenv("ALPHA_VANTAGE_API_KEY_3"),
    getenv("ALPHA_VANTAGE_API_KEY_4"),
    getenv("ALPHA_VANTAGE_API_KEY_5"),
    getenv("ALPHA_VANTAGE_API_KEY_6"),
    getenv("ALPHA_VANTAGE_API_KEY_7"),
    getenv("ALPHA_VANTAGE_API_KEY_8"),
]

#ALPHA_VANTAGE_API_KEY = getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_API_KEY_DAILY = getenv("ALPHA_VANTAGE_API_KEY_DAILY")

# Function to get the next available API key
def get_next_api_key(current_index=0):
    return ALPHA_VANTAGE_API_KEYS[current_index % len(ALPHA_VANTAGE_API_KEYS)]

VPN_SERVERS = [
    getenv("VPN_SERVER_DENMARCK"),
    getenv("VPN_SERVER_CANADA"),
    getenv("VPN_SERVER_UK"),
    getenv("VPN_SERVER_FRANCE"),
    getenv("VPN_SERVER_POLAND"),
    getenv("VPN_SERVER_US1"),
    getenv("VPN_SERVER_US2"),
]

def get_next_vpn_server(current_index=0):
    return VPN_SERVERS[current_index % len(VPN_SERVERS)]
