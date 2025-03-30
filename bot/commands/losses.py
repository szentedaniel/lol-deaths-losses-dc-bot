import logging

import aiohttp
import discord
from discord import app_commands

from configuration import RIOT_API_KEY
from general.lol_functions import create_stats_embed, get_losses_in_last_week

if not RIOT_API_KEY:
    logging.error("Error: RIOT_API_KEY is missing from the .env file!")
    exit(1)


@app_commands.command(name="losses", description="Retrieve a player's losses and deaths over the past week.")
@app_commands.describe(summoner="SummonerName#tag")
async def losses(interaction: discord.Interaction, summoner: str):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        try:
            summoner_name, summoner_tag = summoner.split("#")
        except ValueError:
            await interaction.followup.send("Invalid summoner name format. Please use 'SummonerName#tag'.")
            return

        result = None

        try:
            result = await get_losses_in_last_week(session, summoner_name, summoner_tag)
        except Exception as e:
            await interaction.followup.send(f"{e}")

        if result is not None:
            losses, total_deaths = result
        else:
            losses = total_deaths = 0

        embed = create_stats_embed(losses, total_deaths, summoner_name)

        await interaction.followup.send(embed=embed)
        # await interaction.followup.send(f"{summoner_name}#{summoner_tag} lost {losses} matches and died {total_deaths} times in the past week.")
