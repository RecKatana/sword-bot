import os
import telebot
import time
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

@bot.message_handler(commands=["профиль"])
def профиль(message):
    user_id = message.from_user.id
    user = get_user(user_id)  # Получаем объект User

    if not user:
        bot.send_message(message.chat.id, "Ты ещё не зарегистрирован. Напиши /start")
        return

    # Получаем союзников, если есть
    allies = alliances.get(user_id, set())

    # Формируем текст профиля
    text = (
        f"👤 Персонаж: {user.username}\n"
        f"📈 Уровень: {user.level}\n"
        f"✨ Опыт: {getattr(user, 'exp', 0)}\n"   # если есть опыт, иначе 0
        f"❤️ HP: {getattr(user, 'hp', 100)}/{getattr(user, 'max_hp', 100)}\n"
        f"🔋 Энергия: {getattr(user, 'energy', 50)}/{getattr(user, 'max_energy', 50)}\n"
        f"⚔ Атака: {getattr(user, 'attack', 10)}\n"
        f"🛡 Защита: {getattr(user, 'defense', 5)}\n"
        f"💰 Серебро: {getattr(user, 'silver', 0)}\n"
        f"🛡 Союзников: {len(allies)}"
    )

    bot.send_message(message.chat.id, text)

# --- Класс пользователя ---
class User:
    def __init__(self, id, username, level=1, power=10):
        self.id = id
        self.username = username
        self.level = level
        self.power = power

# --- База пользователей ---
users = {}

def get_user(user_id):
    if user_id not in users:
        users[user_id] = User(user_id, f"user{user_id}")
    return users[user_id]

# --- Заявки и союзы ---
alliance_requests = {}  # key=отправитель id, value=целевой id
alliances = {}           # key=user id, value=set союзников
last_request_time = {}   # key=user id, value=time последней заявки

COOLDOWN = 10 * 60  # 10 минут

# --- Команда Союз ---
@bot.message_handler(func=lambda m: m.text.lower() == "союз")
def send_alliance_request(message):
    sender_id = message.from_user.id
    sender_user = get_user(sender_id)

    if not message.reply_to_message:
        bot.send_message(message.chat.id, "❌ Напишите 'Союз' в ответ на сообщение игрока.")
        return

    target_id = message.reply_to_message.from_user.id
    target_user = get_user(target_id)

    if target_id == sender_id:
        bot.send_message(message.chat.id, "❌ Нельзя создать союз с самим собой.")
        return

    # Проверка таймера
    now = time.time()
    if sender_id in last_request_time and now - last_request_time[sender_id] < COOLDOWN:
        remaining = int(COOLDOWN - (now - last_request_time[sender_id]))
        bot.send_message(message.chat.id, f"⏳ Подождите {remaining} секунд перед новой заявкой.")
        return

    last_request_time[sender_id] = now

    # Проверяем взаимность
    if target_id in alliance_requests and alliance_requests[target_id] == sender_id:
        # Автоматическое принятие
        alliances.setdefault(sender_id, set()).add(target_id)
        alliances.setdefault(target_id, set()).add(sender_id)
        del alliance_requests[target_id]

        text = (
            f"✨ Союз между {sender_user.username} и {target_user.username} заключён! ✨\n\n"
            f"🔹 {sender_user.username}: уровень {sender_user.level}, сила {sender_user.power}\n"
            f"🔹 {target_user.username}: уровень {target_user.level}, сила {target_user.power}\n\n"
            "Складываются печати... ⚔️\n"
            "Магические потоки сливаются... 🔮\n"
            "Союз создан! 🛡️"
        )
        bot.send_message(message.chat.id, text)
        return

    # Если нет взаимной заявки, создаём её и добавляем кнопку "Принять союз"
    alliance_requests[sender_id] = target_id
    text = (
        f"📨 {sender_user.username} отправил заявку в союз {target_user.username}!\n"
        f"Характеристики:\n"
        f"🔹 Уровень: {sender_user.level}\n"
        f"🔹 Сила: {sender_user.power}\n\n"
        f"{target_user.username}, нажмите кнопку ниже, чтобы принять союз!"
    )

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🤝 Принять союз", callback_data=f"accept_{sender_id}"))
    bot.send_message(message.chat.id, text, reply_markup=markup)

# --- Обработка кнопки "Принять союз" ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_"))
def callback_accept_alliance(call):
    sender_id = int(call.data.split("_")[1])  # id игрока, который отправил заявку
    target_id = call.from_user.id             # кто нажал кнопку
    target_user = get_user(target_id)
    sender_user = get_user(sender_id)

    # Проверка, существует ли заявка
    if sender_id not in alliance_requests or alliance_requests[sender_id] != target_id:
        bot.answer_callback_query(call.id, "❌ Эта заявка больше недействительна.")
        return

    # Создание союза
    alliances.setdefault(sender_id, set()).add(target_id)
    alliances.setdefault(target_id, set()).add(sender_id)
    del alliance_requests[sender_id]

    # Красивое оформление
    text = (
        f"✨ Союз между {sender_user.username} и {target_user.username} заключён! ✨\n\n"
        f"🔹 {sender_user.username}: уровень {sender_user.level}, сила {sender_user.power}\n"
        f"🔹 {target_user.username}: уровень {target_user.level}, сила {target_user.power}\n\n"
        "Складываются печати... ⚔️\n"
        "Магические потоки сливаются... 🔮\n"
        "Союз создан! 🛡️"
    )
    bot.send_message(call.message.chat.id, text)
    bot.answer_callback_query(call.id, "✅ Вы приняли союз!")

# --- Кнопка Мои союзы ---
@bot.message_handler(commands=["мои_союзы"])
def my_alliances(message):
    send_alliances_list(message.from_user.id, message.chat.id)

def send_alliances_list(user_id, chat_id):
    user_allies = alliances.get(user_id, set())
    if not user_allies:
        bot.send_message(chat_id, "У вас пока нет союзников.")
        return

    text = "🛡️ Ваши союзники:\n"
    for ally_id in user_allies:
        ally = get_user(ally_id)
        text += f"🔹 {ally.username} (уровень {ally.level}, сила {ally.power})\n"

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔄 Обновить союзников", callback_data="show_alliances"))
    bot.send_message(chat_id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "show_alliances")
def callback_show_alliances(call):
    user_id = call.from_user.id
    send_alliances_list(user_id, call.message.chat.id)

# --- Удаление союза ---
@bot.message_handler(commands=["удалить_союз"])
def remove_alliance(message):
    user_id = message.from_user.id
    if not message.reply_to_message:
        bot.send_message(message.chat.id, "❌ Ответьте на сообщение союзника, чтобы удалить союз.")
        return
    target_id = message.reply_to_message.from_user.id

    if user_id in alliances and target_id in alliances[user_id]:
        alliances[user_id].remove(target_id)
        alliances[target_id].remove(user_id)
        bot.send_message(message.chat.id, f"⚔️ Союз с {get_user(target_id).username} удалён.")
    else:
        bot.send_message(message.chat.id, "❌ Союз с этим игроком не найден.")

# === Запуск бота ===
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    Thread(target=run_bot).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
