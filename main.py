import os
import telebot
from flask import Flask
from threading import Thread
from database import init_db

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

init_db()

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Бот работает 🔥")

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
