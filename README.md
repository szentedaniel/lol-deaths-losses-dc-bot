# LoL Deaths & Losses Discord Bot

A Discord bot that tracks deaths and losses in **League of Legends**, providing stats and notifications. 🚀

This bot was created for personal use, but feel free to modify and adapt it to your needs.

## Features

- Tracks player deaths and losses in LoL matches so it can annoy your friends.
- Sends automated updates and notifications in Discord.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/szentedaniel/lol-deaths-losses-dc-bot.git
   cd lol-deaths-losses-dc-bot
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up your `.env` file with the required API keys and bot token:
   ```ini
   RIOT_API_KEY=your_riot_api_key
   DISCORD_BOT_TOKEN=your_discord_bot_token
   DISCORD_WEBHOOK_URL=your_discord_webhook_url
   ```
4. Start the application with the desired module:
   ```sh
   python main.py [--bot | --web | --tasks | --all]
   ```
   - `--bot` → Run the Discord bot
   - `--web` → Run the webserver
   - `--tasks` → Run the scheduler
   - `--all` → Run all modules in parallel

## Usage

- Invite the bot to your Discord server.
- Use bot commands to track stats and receive notifications.
- Customize settings based on your needs.

## Contributing

Pull requests are welcome! Feel free to submit issues or feature requests.

## License

MIT License

