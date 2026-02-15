import telebot
import os
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот работает 🔥")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://sword-bot.onrender.com/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
