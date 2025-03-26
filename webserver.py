from flask import Flask
from threading import Thread

app = Flask("")
@app.route("/")
def home():
    return "Discord bot ok"

def run():
    from waitress import serve
    serve(app, host="0.0.0.0", port=8000)

def keep_alive():
    t = Thread(target=run)
    t.start()