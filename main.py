import os
import telebot
from flask import Flask
from threading import Thread
from database import init_db, get_user, create_user
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
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

@bot.message_handler(commands=["союз"])
def send_alliance(message):
    args = message.text.split()
    target = None

    if message.reply_to_message:
        target_id = message.reply_to_message.from_user.id
        target = get_user(target_id)
        if not target:
            bot.send_message(message.chat.id, "Игрок не найден ❌")
            return
        target_id = target.id

    elif len(args) >= 2 and args[1].startswith("@"):
        username = args[1][1:]
        target = get_user_by_username(username)
        if not target:
            bot.send_message(message.chat.id, "Игрок не найден ❌")
            return
        target_id = target.id

    else:
        bot.send_message(message.chat.id, "Укажите пользователя ❌")
        return

    bot.send_message(message.chat.id, f"Союз с игроком {target.username} ✅")
    
# --- Иначе ошибка ---
else:
    bot.send_message(message.chat.id, "Используй: /союз @username или ответь на сообщение")
    return

    # Нельзя с собой
    if target_id == message.from_user.id:
        bot.send_message(message.chat.id, "Нельзя заключить союз с самим собой 😅")
        return

    # Уже союз?
    friends = get_friends(message.from_user.id)
    for friend in friends:
        if friend[1] == target_id:
            bot.send_message(message.chat.id, "Вы уже союзники ⚔")
            return

    # Встречная заявка?
    reverse_request = get_friend_request(target_id, message.from_user.id)

    if reverse_request:
        delete_friend_request(target_id, message.from_user.id)
        add_friend(target_id, message.from_user.id)

        text = (
            "🌪 Воздух сгущается...\n\n"
            "✨ Две силы притянулись друг к другу...\n"
            "🔮 Круг союза вспыхивает ярким светом...\n\n"
            f"🤝 Теперь @{username} — твой союзник!"
        )

        bot.send_message(message.chat.id, text)
        bot.send_message(target_id, text)
        return

    # Уже отправлял заявку?
    existing = get_friend_request(message.from_user.id, target_id)
    if existing:
        bot.send_message(message.chat.id, "Ты уже отправил предложение союза 📩")
        return

    # Отправляем заявку
    send_friend_request(message.from_user.id, target_id)

    sender_username = message.from_user.username or f"id{message.from_user.id}"

    bot.send_message(
        message.chat.id,
        f"🕊 Ты предложил союз @{username}!"
    )

    bot.send_message(
        target_id,
        f"⚔ Игрок @{sender_username} предлагает тебе союз!\n\n"
        f"Ответь на его сообщение и напиши:\n"
        f"/союз"
        )

@bot.message_handler(commands=["мои_союзы"])
def my_alliances(message):
    friends = get_friends(message.from_user.id)

    if not friends:
        bot.send_message(message.chat.id, "⚔ У тебя пока нет союзников.")
        return

    markup = InlineKeyboardMarkup()

    for friend in friends:
        friend_id = friend[1]  # tg_id союзника
        user = get_user(friend_id)

        if user:
            # ⚠ ВАЖНО: если username — последний столбец
            username = user[-1]

            if username:
                text = f"⚔ @{username}"
            else:
                text = f"⚔ Игрок {friend_id}"
        else:
            text = f"⚔ Игрок {friend_id}"

        markup.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"ally_{friend_id}"
            )
        )

    bot.send_message(
        message.chat.id,
        "🤝 Твои союзы:\n\nВыбери союзника:",
        reply_markup=markup
    )

@bot.message_handler(commands=["мои_союзы"])
def my_alliances(message):
    friends = get_friends(message.from_user.id)

    if not friends:
        bot.send_message(message.chat.id, "⚔ У тебя пока нет союзников.")
        return

    markup = InlineKeyboardMarkup()

    for friend in friends:
        friend_id = friend[1]
        user = get_user(friend_id)

        if user and user[-1]:
            username = user[-1]
            text = f"⚔ @{username}"
        else:
            text = f"⚔ Игрок {friend_id}"

        markup.add(
            InlineKeyboardButton(
                text=text,
                callback_data=f"allymenu_{friend_id}"
            )
        )

    bot.send_message(
        message.chat.id,
        "🤝 Твои союзы:\n\nВыбери союзника:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("ally_"))
def alliance_menu(call):
    friend_id = int(call.data.split("_")[1])
    user = get_user(friend_id)

    if user and user[-1]:
        username = user[-1]
        name_text = f"@{username}"
    else:
        name_text = f"Игрок {friend_id}"

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            text="❌ Разорвать союз",
            callback_data=f"break_{friend_id}"
        )
    )

    bot.edit_message_text(
        f"⚔ Союз с {name_text}\n\nЧто хочешь сделать?",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("break_"))
def break_alliance(call):
    friend_id = int(call.data.split("_")[1])
    user_id = call.from_user.id

    # Удаляем союз у обоих
    remove_friend(user_id, friend_id)
    remove_friend(friend_id, user_id)

    text = (
        "💔 Круг союза трескается...\n"
        "🌫 Магия рассеивается...\n\n"
        "⚔ Союз разорван."
    )

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id
    )

    try:
        bot.send_message(
            friend_id,
            "💔 Один из союзов был разорван..."
        )
    except:
        pass

# === Запуск бота ===
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
