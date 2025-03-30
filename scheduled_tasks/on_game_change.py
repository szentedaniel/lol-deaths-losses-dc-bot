import asyncio
import logging
import time

import aiohttp
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler
from discord import Embed, Webhook

from configuration import DISCORD_WEBHOOK_URL
from general.lol_functions import create_stats_embed, fetch_last_match, fetch_match_data, get_losses_in_last_week, get_puuid

# Define the summoner's details
SUMMONER_NAME = "OnTheFumes"
SUMMONER_TAG = "112"

# Store the previous match result
previous_match_id = None
first_check_for_new_game = True

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GameMonitor")


async def send_discord_message(message, session, embed: Embed | None = None):
    """Send a message to the Discord webhook."""
    try:
        webhook = Webhook.from_url(DISCORD_WEBHOOK_URL, session=session)  # type: ignore
        if embed:
            await webhook.send(content=message, embed=embed)
        else:
            await webhook.send(content=message)
    except Exception as e:
        logger.error(f"Failed to send Discord message: {e}")


async def check_for_new_game():
    """Check the last game result and send a message if it changed."""
    global previous_match_id
    global first_check_for_new_game
    async with aiohttp.ClientSession() as session:
        try:
            # Step 1: Fetch the summoner's PUUID
            puuid = await get_puuid(session, SUMMONER_NAME, SUMMONER_TAG)
            if not puuid:
                logger.warning("Could not retrieve PUUID.")
                return

            # Step 2: Get the most recent match ID
            match_id = await fetch_last_match(session, puuid)
            if not match_id:
                logger.warning("No match data found.")
                return

            # Step 3: Fetch match details
            match_data = await fetch_match_data(session, match_id)
            if not match_data:
                logger.warning("Failed to fetch match data.")
                return

            # Step 4: Check the match result (win or loss)
            participant = next((p for p in match_data.get("info", {}).get("participants", []) if p.get("puuid") == puuid), None)
            if participant:
                result = "won" if participant.get("win", False) else "lost"
            else:
                logger.warning("Participant data not found.")
                return

            # Step 5: Compare with the previous result and send message if changed
            if match_id != previous_match_id:
                previous_match_id = match_id
                if result == "won":
                    message = f"Somehow, luck turned to **{SUMMONER_NAME}#{SUMMONER_TAG}** and he accidentally won a game!"
                else:
                    message = f"**{SUMMONER_NAME}#{SUMMONER_TAG}** was unlucky again and of course lost a game!"
                if not first_check_for_new_game:
                    await send_discord_message(message, session=session)
                    logger.info(f"Sent message: {message}")
            first_check_for_new_game = False
        except Exception as e:
            logger.error(f"Error while checking for new game: {e}")


async def weekly_stats():
    """Check the last game result and send a message if it changed."""
    global previous_match_id
    global first_check_for_new_game
    async with aiohttp.ClientSession() as session:
        try:
            losses, total_deaths = await get_losses_in_last_week(session, SUMMONER_NAME, SUMMONER_TAG)
            embed = create_stats_embed(losses, total_deaths, SUMMONER_NAME)
            await send_discord_message(message="", session=session, embed=embed)

        except Exception as e:
            logger.error(f"Error while checking for new game: {e}")


def job_check_for_new_game():
    """Wrap the check_for_new_game in a job for APScheduler."""
    asyncio.run(check_for_new_game())


def job_weekly_stats():
    """Wrap the check_for_new_game in a job for APScheduler."""
    asyncio.run(check_for_new_game())


def main():
    # Initialize the scheduler
    scheduler = BackgroundScheduler()

    # Schedule the task to run every 1 minutes
    scheduler.add_job(job_check_for_new_game, "interval", minutes=1)
    # Schedule the task to run every Sunday at 20:00
    scheduler.add_job(job_weekly_stats, "cron", day_of_week="sun", hour=20, minute=00)

    # Set up the logger for the job execution
    def job_listener(event):
        if event.exception:
            logger.error(f"Job {event.job_id} failed")
        else:
            logger.info(f"Job {event.job_id} executed successfully")

    scheduler.add_listener(job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

    # Start the scheduler
    scheduler.start()

    # Run indefinitely to keep the scheduler running
    try:
        while True:
            # Just keep the main thread alive so the background job can keep running
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        # Gracefully shutdown the scheduler
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully")


if __name__ == "__main__":
    main()
