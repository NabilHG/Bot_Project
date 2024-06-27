from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Token Telgram bot
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")

# external API keys
# External API keys
# ALPHA_VANTAGE_API_KEYS = [
#     getenv("ALPHA_VANTAGE_API_KEY_1"),
#     getenv("ALPHA_VANTAGE_API_KEY_2"),
#     getenv("ALPHA_VANTAGE_API_KEY_3"),
#     getenv("ALPHA_VANTAGE_API_KEY_4"),
#     getenv("ALPHA_VANTAGE_API_KEY_5"),
#     getenv("ALPHA_VANTAGE_API_KEY_6"),
#     getenv("ALPHA_VANTAGE_API_KEY_7"),
#     getenv("ALPHA_VANTAGE_API_KEY_8"),
#     getenv("ALPHA_VANTAGE_API_KEY_9"),
#     getenv("ALPHA_VANTAGE_API_KEY_10"),
#     getenv("ALPHA_VANTAGE_API_KEY_11"),
#     getenv("ALPHA_VANTAGE_API_KEY_12"),
#     getenv("ALPHA_VANTAGE_API_KEY_13"),
#     getenv("ALPHA_VANTAGE_API_KEY_14"),
#     getenv("ALPHA_VANTAGE_API_KEY_15"),
#     getenv("ALPHA_VANTAGE_API_KEY_16"),
#     getenv("ALPHA_VANTAGE_API_KEY_17"),
#     getenv("ALPHA_VANTAGE_API_KEY_18"),
#     getenv("ALPHA_VANTAGE_API_KEY_19"),
#     getenv("ALPHA_VANTAGE_API_KEY_20"),
# ]

ALPHA_VANTAGE_API_KEY = getenv("ALPHA_VANTAGE_API_KEY")
ALPHA_VANTAGE_API_KEY_DAILY = getenv("ALPHA_VANTAGE_API_KEY_DAILY")

# Function to get the next available API key
# def get_next_api_key(current_index=0):
#     return ALPHA_VANTAGE_API_KEYS[current_index % len(ALPHA_VANTAGE_API_KEYS)]


TIINGO_API_KEY = getenv("TIINGO_API_KEY")
