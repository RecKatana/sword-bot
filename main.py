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

# === Команда /profile ===
@bot.message_handler(commands=["profile"])
def profile(message):
    user = get_user(message.from_user.id)

    if not user:
        bot.send_message(message.chat.id, "Ты ещё не зарегистрирован. Напиши /start")
        return

    text = (
    f"🧙 Персонаж: {user[2]}\n"
    f"⚔ Уровень: {user[5]}\n"
    f"✨ Опыт: {user[6]}\n"
    f"❤️ HP: {user[7]}/{user[8]}\n"
    f"🔋 Энергия: {user[11]}/{user[12]}\n"
    f"🗡 Атака: {user[9]}\n"
    f"🛡 Защита: {user[10]}\n"
    f"💰 Серебро: {user[13]}"
    )

    bot.send_message(message.chat.id, text)
    
# === Запуск бота ===
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
