from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Token Telgram bot
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")

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


