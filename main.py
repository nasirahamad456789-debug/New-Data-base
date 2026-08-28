import os
import json
import requests
import telebot

BOT_TOKEN = os.getenv("8945120303:AAGPsZrxh5suDZOVrMBKX2tcwPO5usra7ZM")
API_URL = "https://wasifali.biz.id/public_apis/sim-info-api.php"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "🎯 **SIM DATABASE BOT** 🎯\n\nMujhe koi bhi mobile number bhejein (e.g. 030123456789)."
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    number = message.text.strip()
    
    if not number.isdigit():
        bot.reply_to(message, "⚠️ Kripya sirf digits/mobile number bhejein.")
        return

    wait_msg = bot.reply_to(message, "🔍 Searching details, please wait...")
    
    try:
        response = requests.get(API_URL, params={"search": number}, timeout=12)
        
        if response.status_code == 200:
            raw_text = response.text.strip()
            
            start_idx = raw_text.find('{')
            end_idx = raw_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                clean_json_str = raw_text[start_idx:end_idx+1]
                data = json.loads(clean_json_str)
            else:
                bot.edit_message_text("❌ Invalid API response format.", chat_id=message.chat.id, message_id=wait_msg.message_id)
                return

            records = data.get("records", [])
            
            if records:
                reply_text = "🎯 **SIM DATABASE RESULTS** 🎯\n\n"
                
                for index, record in enumerate(records, 1):
                    name = record.get("name", "None")
                    mobile = record.get("mobile", number)
                    cnic = record.get("cnic", "None")
                    address = record.get("address", "None")

                    reply_text += (
                        f"👤 **Record #{index}**\n"
                        f"├── 📛 **Name:** `{name}`\n"
                        f"├── 📱 **Mobile:** `{mobile}`\n"
                        f"├── 🆔 **CNIC:** `{cnic}`\n"
                        f"└── 📍 **Address:** `{address}`\n\n"
                    )

                reply_text += (
                    "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
                    "⚙️ **Status:** ✨ Full Access\n"
                    "💬 **Support:** [Telegram Support](https://t.me/FREEHACKS95)\n"
                    "📢 **Channels:** [Telegram](https://t.me/+zLVbS12-FxMyMmM0)"
                )

                bot.edit_message_text(
                    reply_text, 
                    chat_id=message.chat.id, 
                    message_id=wait_msg.message_id, 
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
            else:
                bot.edit_message_text("❌ Is number ka koi record nahi mila.", chat_id=message.chat.id, message_id=wait_msg.message_id)
        else:
            bot.edit_message_text("❌ API Server Error. Please try again later.", chat_id=message.chat.id, message_id=wait_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", chat_id=message.chat.id, message_id=wait_msg.message_id)

print("Bot is running...")
bot.infinity_polling()
