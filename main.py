import os
import requests
import telebot

# Bot Token Direct (Railway environment variable ka issue khatam karne ke liye)
BOT_TOKEN = "8945120303:AAGPsZrxh5suDZOVrMBKX2tcwPO5usra7ZM"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Apna Mobile Number ya CNIC bhejain search karne ke liye.")

@bot.message_handler(func=lambda message: True)
def get_sim_details(message):
    query = message.text.strip()
    bot.reply_to(message, "Searching data, please wait...")
    
    url = f"https://wasifali.biz.id/public_apis/sim-info-api.php?num={query}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.text
            if data:
                bot.send_message(message.chat.id, f"**Result:**\n\n{data}", parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "Koi record nahi mila.")
        else:
            bot.send_message(message.chat.id, "API Server par issue hai, baad mein try karein.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

print("Bot status: Running...")
bot.infinity_polling()
