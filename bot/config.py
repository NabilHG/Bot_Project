from dotenv import load_dotenv
from os import getenv
load_dotenv()

# Token Telgram bot
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN")

# external API keys 
ALPHA_VANTAGE_API_KEY = getenv("ALPHA_VANTAGE_API_KEY")
TIINGO_API_KEY = getenv("TIINGO_API_KEY")