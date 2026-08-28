import os
import requests
import telebot

BOT_TOKEN = "8945120303:AAGPsZrxh5suDZOVrMBKX2tcwPO5usra7ZM"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! Mobile Number ya CNIC bhejain search karne ke liye.")

@bot.message_handler(func=lambda message: True)
def get_sim_details(message):
    query = message.text.strip()
    bot.reply_to(message, "Searching data, please wait...")
    
    url = f"https://wasifali.biz.id/public_apis/sim-info-api.php?num={query}"
    
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # Agar response JSON hai
            try:
                res_json = response.json()
                bot.send_message(message.chat.id, f"```json\n{res_json}\n```", parse_mode="Markdown")
            except:
                # Agar raw text/HTML response hai
                bot.send_message(message.chat.id, response.text)
        else:
            bot.send_message(message.chat.id, f"API Error: Status Code {response.status_code}")
            
    except Exception as e:
        bot.send_message(message.chat.id, f"Connection Error: {str(e)}")

print("Bot status: Running...")
bot.infinity_polling()
