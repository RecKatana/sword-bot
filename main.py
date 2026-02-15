import telebot
import os

TOKEN = os.getenv("8215636432:AAFbkLxl2VSdFgLyho7uD12aITWMttfXZFQ")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот работает 🔥")

print("Bot started...")
bot.infinity_polling()
