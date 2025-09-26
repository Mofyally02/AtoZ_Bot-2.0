import threading
import time

from flask import Flask, jsonify, render_template

from config import BOT_CONFIG
from persistent_bot import run_persistent_bot

app = Flask(__name__)

bot_thread = None
BOT_CONFIG["bot_running"] = False


@app.route("/")
def index():
    status = "Running" if BOT_CONFIG["bot_running"] else "Stopped"
    return render_template("index.html", bot_status=status)


@app.route("/toggle_bot", methods=["POST"])
def toggle_bot():
    global bot_thread
    if not BOT_CONFIG["bot_running"]:
        BOT_CONFIG["bot_running"] = True
        bot_thread = threading.Thread(target=bot_loop, daemon=True)
        bot_thread.start()
        return jsonify({"status": "Bot started"})
    else:
        BOT_CONFIG["bot_running"] = False
        if bot_thread and bot_thread.is_alive():
            bot_thread.join(timeout=5)
        return jsonify({"status": "Bot stopped"})


def bot_loop():
    run_persistent_bot()


if __name__ == "__main__":
    app.run(port=int(BOT_CONFIG.get("host_port", 5000)), debug=True)


