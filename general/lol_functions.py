import asyncio
import datetime
import logging
from typing import Any, Iterable

import aiohttp
from discord import Color, Embed

from configuration import REGION, RETRY_DELAY, RIOT_API_KEY
from general.custom_exceptions import MyCustomError


async def get_puuid(session: aiohttp.ClientSession, summoner_name: str, summoner_tag: str) -> str:
    """Fetch the summoner's PUUID."""
    summoner_url = f"https://{REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}?api_key={RIOT_API_KEY}"
    try:
        async with session.get(summoner_url) as summoner_response:
            summoner_response.raise_for_status()
            summoner_data = await summoner_response.json()
            if "puuid" not in summoner_data:
                raise MyCustomError("Summoner not found.")
            return summoner_data["puuid"]
    except aiohttp.ClientResponseError as e:
        if e.status == 429:
            logging.warning("Rate limited (429). Retrying...")
            await asyncio.sleep(RETRY_DELAY)
            return await get_puuid(session, summoner_name, summoner_tag)
        logging.error(f"Failed to fetch summoner data: {e}")
        raise MyCustomError("Failed to retrieve summoner data. Please try again later.")
    except Exception as e:
        logging.error(f"Unexpected error while fetching summoner data: {e}")
        raise MyCustomError("Unexpected error while fetching summoner data.")


async def fetch_match_history(session: aiohttp.ClientSession, puuid: str, start_time: int | None = None):
    """Fetch match IDs."""
    matches_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=100{f"&startTime={start_time}" if start_time else "f"}&api_key={RIOT_API_KEY}"
    try:
        async with session.get(matches_url) as matches_response:
            matches_response.raise_for_status()
            match_ids = await matches_response.json()
            return match_ids
    except aiohttp.ClientResponseError as e:
        if e.status == 429:
            logging.warning("Rate limited (429). Retrying...")
            await asyncio.sleep(RETRY_DELAY)
            return await fetch_match_history(session, puuid, start_time)
        logging.error(f"Failed to fetch match history: {e}")
        raise MyCustomError("Failed to retrieve match history. Please try again later.")
    except Exception as e:
        logging.error(f"Unexpected error while fetching match history: {e}")
        raise MyCustomError("Unexpected error while fetching match history")


async def fetch_last_match(session: aiohttp.ClientSession, puuid: str):
    """Fetch the most recent match ID."""
    matches_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?count=1&api_key={RIOT_API_KEY}"
    try:
        async with session.get(matches_url) as response:
            response.raise_for_status()
            match_ids = await response.json()
            return match_ids[0] if match_ids else None
    except aiohttp.ClientResponseError as e:
        if e.status == 429:
            logging.warning("Rate limited (429). Retrying...")
            await asyncio.sleep(RETRY_DELAY)
            return await fetch_match_history(session, puuid)  # type: ignore
        logging.error(f"Failed to fetch the last match: {e}")
        raise MyCustomError("Failed to retrieve the last match. Please try again later.")
    except Exception as e:
        logging.error(f"Unexpected error while fetching the last match: {e}")
        raise MyCustomError("Unexpected error while fetching the last match")


async def fetch_match_data(session: aiohttp.ClientSession, match_id):
    """Fetch the match data."""
    match_url = f"https://{REGION}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={RIOT_API_KEY}"
    try:
        async with session.get(match_url) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientResponseError as e:
        if e.status == 429:
            logging.warning("Rate limited (429). Retrying...")
            await asyncio.sleep(RETRY_DELAY)
            return await fetch_match_data(session, match_id)  # type: ignore
        logging.error(f"Failed to fetch match data: {e}")
        raise MyCustomError("Failed to fetch match data. Please try again later.")
    except Exception as e:
        logging.error(f"Unexpected error while fetching match data: {e}")
        raise MyCustomError("Unexpected error while fetching match data.")


async def count_losses_and_deaths(session: aiohttp.ClientSession, match_ids: Iterable[Any], puuid: str):
    losses: int = 0
    total_deaths: int = 0

    for match_id in match_ids:
        try:
            match_data = await fetch_match_data(session, match_id)
        except Exception as e:
            logging.error(f"Skipping match {match_id} due to request error: {e}")
            raise e

        participant = next((p for p in match_data.get("info", {}).get("participants", []) if p.get("puuid") == puuid), None)
        if participant and not participant.get("win", True):
            losses += 1
            total_deaths += participant.get("deaths", 0)

    return losses, total_deaths


async def get_losses_in_last_week(session: aiohttp.ClientSession, summoner_name: str, summoner_tag: str):
    try:
        puuid = await get_puuid(session, summoner_name, summoner_tag)
    except Exception as e:
        raise e

    one_week_ago = int((datetime.datetime.now(datetime.UTC) - datetime.timedelta(days=7)).timestamp())

    try:
        match_ids = await fetch_match_history(session, puuid, start_time=one_week_ago)
    except Exception as e:
        raise e

    return await count_losses_and_deaths(session, match_ids, puuid)


def create_stats_embed(losses: int, total_deaths: int, summoner_name: str) -> Embed:
    if summoner_name.lower() == "onthefumes":
        color = Color.red()
        thumbnail_url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fadmin.esports.gg%2Fwp-content%2Fuploads%2F2024%2F05%2FHoL2024_Azir_All-Roads-Lead-to-Me_FINAL.png&f=1&nofb=1&ipt=113d53b2a04d3176bc038f31b05ef5928bf5e154f5289392db07de5fccbe427a&ipo=images"
        footer_text = "Pathetic"
    else:
        color = Color.green()
        thumbnail_url = "https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fi0.kym-cdn.com%2Fphotos%2Fimages%2Foriginal%2F001%2F244%2F891%2Fd1f.png&f=1&nofb=1&ipt=9bdcd3a6f4cc0ecd278b0e0199be98a1015febc9b3291931321e0fa6c7feac21&ipo=images"
        footer_text = "Outstanding"

    embed = Embed(title=f"{summoner_name}'s weekly stats", color=color)
    embed.add_field(name="Stat", value="Losses: \nDeaths:")
    embed.add_field(name="Counter", value=f"{losses} \n{total_deaths}", inline=True)
    embed.set_thumbnail(url=thumbnail_url)
    embed.set_footer(text=footer_text)

    return embed
