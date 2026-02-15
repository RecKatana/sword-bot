import os
import telebot
from flask import Flask
from threading import Thread
from database import init_db, get_user, create_user
from database import (
    send_friend_request,
    get_friend_request,
    delete_friend_request,
    add_friend,
    get_friends
)

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
    
@bot.message_handler(commands=["start"])
def start(message):
    user = get_user(message.from_user.id)

    if user:
        bot.send_message(message.chat.id, "Ты уже зарегистрирован ⚔")
    else:
        username = message.from_user.username
        if username is None:
            username = f"id{message.from_user.id}"

        create_user(
            message.from_user.id,
            message.from_user.first_name,
            username
        )

        bot.send_message(message.chat.id, "Персонаж создан ⚔🔥")

@bot.message_handler(commands=["profile"])
def profile(message):
    user = get_user(message.from_user.id)

    if not user:
        bot.send_message(message.chat.id, "Ты ещё не зарегистрирован. Напиши /start")
        return

    text = (
    f"👤 Персонаж: {user[0]}\n"
    f"📈 Уровень: {user[1]}\n"
    f"✨ Опыт: {user[2]}\n"
    f"❤️ HP: {user[3]}/{user[4]}\n"
    f"🔋 Энергия: {user[7]}/{user[8]}\n"
    f"⚔ Атака: {user[5]}\n"
    f"🛡 Защита: {user[6]}\n"
    f"💰 Серебро: {user[9]}"
)

    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=["принять"])
def accept_ally(message):
    args = message.text.split()
    
    if len(args) < 2:
        bot.send_message(message.chat.id, "Используй: /принять @username")
        return

    username = args[1].replace("@", "")
    target = get_user_by_username(username)

    if not target:
        bot.send_message(message.chat.id, "Игрок не найден ❌")
        return

    if target[1] == message.from_user.id:
    bot.send_message(message.chat.id, "Ты не можешь заключить союз с самим собой 🤨")
    return

    request = get_friend_request(target[1], message.from_user.id)

    if not request:
        bot.send_message(message.chat.id, "Заявки нет ❌")
        return

    delete_friend_request(target[1], message.from_user.id)
    add_friend(target[1], message.from_user.id)

    text = (
        "🌌 Воздух сгущается...\n\n"
        "✨ Между вами вспыхивает древний круг союза...\n"
        "🔮 Руны загораются алым светом...\n\n"
        "⚔ Клятва произнесена.\n"
        "🤝 Союз скреплён силой стали!\n\n"
        f"🔥 Теперь @{username} — твой союзник!"
    )

    bot.send_message(message.chat.id, text)
    
# === Запуск бота ===
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
