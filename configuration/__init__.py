import os

from dotenv import load_dotenv

from .logger import init_logger

init_logger()

# Load .env file
load_dotenv()

# Discord bot token
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# Discord webhook url for weekly stats report
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
# Riot API key
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
# Region of Riot API
REGION = "europe"
# Retry configuration for 429 status code
RETRY_DELAY = 5  # seconds
