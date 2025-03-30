import argparse
import logging
import threading

# Configuration
import configuration
from bot import bot
from scheduled_tasks import on_game_change
from webserver import server

# from scheduled_tasks import scheduler


def start_bot():
    print("Discord bot indítása...")
    bot.start()


def start_webserver():
    print("Webszerver indítása...")
    server.run()


def start_scheduler():
    print("Időzített feladatok ütemezése...")
    on_game_change.main()


def main():
    parser = argparse.ArgumentParser(description="Indítsd el a kívánt modult.")
    parser.add_argument("--bot", action="store_true", help="Discord bot indítása")
    parser.add_argument("--web", action="store_true", help="Webszerver indítása")
    parser.add_argument("--tasks", action="store_true", help="Időzített feladatok indítása")
    parser.add_argument("--all", action="store_true", help="Minden modul párhuzamos futtatása")
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
