import datetime
import logging
import os

import discord
import requests
from discord import app_commands
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Riot API key and region
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
REGION = "europe"

# Validate API keys
if not RIOT_API_KEY:
    logging.error("Error: RIOT_API_KEY is missing from the .env file!")
    exit(1)

if not DISCORD_BOT_TOKEN:
    logging.error("Error: DISCORD_BOT_TOKEN is missing from the .env file!")
    exit(1)

# Set up Discord bot
intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)


@bot.event
async def on_ready():
    try:
        synced = await tree.sync()
        logging.info(f"Slash commands synchronized: {len(synced)} commands")
    except Exception as e:
        logging.error(f"Error synchronizing commands: {e}")
    logging.info(f"Logged in as {bot.user}")


@tree.command(name="losses", description="Retrieve a player's losses and deaths over the past week.")
@app_commands.describe(summoner="SummonerName#tag")
async def losses(interaction: discord.Interaction, summoner: str):
    await interaction.response.defer()

    try:
        summoner_name, summoner_tag = summoner.split("#")
    except ValueError:
        await interaction.followup.send("Invalid summoner name format. Please use 'SummonerName#tag'.")
        return

    try:
        # Fetch summoner data
        summoner_url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}?api_key={RIOT_API_KEY}"
        summoner_response = requests.get(summoner_url)
        summoner_response.raise_for_status()
        summoner_data = summoner_response.json()
    except requests.RequestException as e:
        await interaction.followup.send("Failed to retrieve summoner data. Please try again later.")
        logging.error(f"Summoner request error: {e}")
        return

    if "puuid" not in summoner_data:
        await interaction.followup.send("Summoner not found.")
        return

    puuid = summoner_data["puuid"]
    one_week_ago = int((datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)).timestamp())

    try:
        # Fetch match history
        matches_url = (
            f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?startTime={one_week_ago}&count=100&api_key={RIOT_API_KEY}"
        )
        matches_response = requests.get(matches_url)
        matches_response.raise_for_status()
        match_ids = matches_response.json()
    except requests.RequestException as e:
        await interaction.followup.send("Failed to retrieve match history. Please try again later.")
        logging.error(f"Match history request error: {e}")
        return

    losses = 0
    total_deaths = 0

    for match_id in match_ids:
        try:
            match_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
            match_response = requests.get(match_url)
            match_response.raise_for_status()
            match_data = match_response.json()
        except requests.RequestException as e:
            logging.warning(f"Skipping match {match_id} due to request error: {e}")
            continue

        participant = next((p for p in match_data.get("info", {}).get("participants", []) if p.get("puuid") == puuid), None)
        if participant and not participant.get("win", True):
            losses += 1
            total_deaths += participant.get("deaths", 0)

    await interaction.followup.send(f"{summoner_name}#{summoner_tag} lost {losses} matches and died {total_deaths} times in the past week.")


bot.run(DISCORD_BOT_TOKEN)
