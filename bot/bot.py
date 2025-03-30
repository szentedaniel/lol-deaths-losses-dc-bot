import logging

from discord import Client, Intents, app_commands

from bot.commands.losses import losses
from configuration import DISCORD_BOT_TOKEN

if not DISCORD_BOT_TOKEN:
    logging.error("Error: DISCORD_BOT_TOKEN is missing from the .env file!")
    exit(1)


def start():
    try:
        intents = Intents.default()
        bot = Client(intents=intents)
        tree = app_commands.CommandTree(bot)

        @bot.event
        async def on_ready():
            try:
                await tree.sync()
                logging.info("Slash commands synchronized.")
            except Exception as e:
                logging.error(f"Error synchronizing commands: {e}")
            logging.info(f"Logged in as {bot.user}")

        tree.add_command(losses)  # type: ignore
        bot.run(DISCORD_BOT_TOKEN)  # type: ignore
    except (KeyboardInterrupt, SystemExit):
        # Gracefully shutdown the bot
        logging.info("Bot shut down successfully")
