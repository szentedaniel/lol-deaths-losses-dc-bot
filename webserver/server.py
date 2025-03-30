import logging

from flask import Flask


def run():
    try:
        app = Flask(__name__)

        @app.route("/")
        def home():
            return "Discord bot ok"

        from waitress import serve

        serve(app, host="0.0.0.0", port=8000)
    except (KeyboardInterrupt, SystemExit):
        # Gracefully shutdown the webserver
        logging.info("Webserver shut down successfully")
