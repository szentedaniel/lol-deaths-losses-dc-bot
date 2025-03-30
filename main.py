import argparse
import logging
import threading

# Configuration
import configuration  # keep it
from bot import bot
from scheduled_tasks import on_game_change
from webserver import server


def start_bot():
    print("Running Discord bot...")
    bot.start()


def start_webserver():
    print("Running webserver...")
    server.run()


def start_scheduler():
    print("Running scheduler...")
    on_game_change.main()


def main():
    parser = argparse.ArgumentParser(description="Launch the desired module")
    parser.add_argument("--bot", action="store_true", help="Run Discord bot")
    parser.add_argument("--web", action="store_true", help="Run webserver")
    parser.add_argument("--tasks", action="store_true", help="Run scheduler")
    parser.add_argument("--all", action="store_true", help="Running all module paralell")
    args = parser.parse_args()

    threads = []
    if args.bot or args.all:
        threads.append(threading.Thread(target=start_bot))
    if args.web or args.all:
        threads.append(threading.Thread(target=start_webserver))
    if args.tasks or args.all:
        threads.append(threading.Thread(target=start_scheduler))

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Main thread ")
