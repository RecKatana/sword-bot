import os
import telebot
from flask import Flask
from threading import Thread
from database import init_db, get_user, create_user

# === Токен ===
TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# === Инициализация базы ===
init_db()

# === Flask для Render ===
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# === Команда /start ===
@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)

    if user:
        bot.send_message(message.chat.id, "Ты уже зарегистрирован ⚔")
    else:
        create_user(message.from_user.id, message.from_user.first_name)
        bot.send_message(message.chat.id, "Персонаж создан ⚔🔥")

# === Запуск бота ===
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
