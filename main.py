import telebot
import requests
import json
import os
from telebot import types

# =========================================================
#                    YOUR SETTINGS
# =========================================================

BOT_TOKEN = "8945120303:AAGPsZrxh5suDZOVrMBKX2tcwPO5usra7ZM"

# Apni Telegram Numeric User ID yahan lagao
OWNER_ID = 5091149246

# API URL Updated
API_URL = "https://wasifali.biz.id/public_apis/sim-info-api.php"


# =========================================================
#                    BOT SETUP
# =========================================================

bot = telebot.TeleBot(BOT_TOKEN)

APPROVED_FILE = "approved_users.json"
REQUESTS_FILE = "access_requests.json"


# =========================================================
#                    FILE FUNCTIONS
# =========================================================

def load_json(filename):
    if not os.path.exists(filename):
        return {}

    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# =========================================================
#                    ACCESS CHECK
# =========================================================

def has_access(user_id):
    # Owner ko hamesha access
    if user_id == OWNER_ID:
        return True

    approved = load_json(APPROVED_FILE)
    return str(user_id) in approved


# =========================================================
#                    ACCESS BUTTON
# =========================================================

def access_button():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "🔐 Request Access",
            callback_data="request_access"
        )
    )
    return keyboard


# =========================================================
#                    START
# =========================================================

@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id

    # OWNER / APPROVED USER
    if has_access(user_id):
        welcome_text = (
            "🎯 **SIM DATABASE BOT** 🎯\n\n"
            "Mujhe koi bhi mobile number bhejein.\n\n"
            "📱 Example: `03012345678`"
        )
        bot.reply_to(
            message,
            welcome_text,
            parse_mode="Markdown"
        )
        return

    # NEW USER
    bot.reply_to(
        message,
        "🔒 **ACCESS REQUIRED**\n\n"
        "Is bot ko use karne ke liye owner se access lena zaroori hai.\n\n"
        "Neeche **Request Access** button dabayein.",
        reply_markup=access_button(),
        parse_mode="Markdown"
    )


# =========================================================
#                    REQUEST ACCESS
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data == "request_access"
)
def request_access(call):
    user = call.from_user
    user_id = user.id

    # Already approved
    if has_access(user_id):
        bot.answer_callback_query(
            call.id,
            "Aapko already access hai."
        )
        return

    requests = load_json(REQUESTS_FILE)

    # Already requested
    if str(user_id) in requests:
        bot.answer_callback_query(
            call.id,
            "Aapki request pehle hi bheji ja chuki hai."
        )
        return

    username = (
        "@" + user.username
        if user.username
        else "No Username"
    )

    # Save request
    requests[str(user_id)] = {
        "user_id": user_id,
        "name": user.first_name or "Unknown",
        "username": username
    }

    save_json(REQUESTS_FILE, requests)

    # Owner buttons
    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(
        types.InlineKeyboardButton(
            "✅ APPROVE",
            callback_data=f"approve:{user_id}"
        ),
        types.InlineKeyboardButton(
            "❌ REJECT",
            callback_data=f"reject:{user_id}"
        )
    )

    # Owner notification
    owner_message = (
        "🔔 **NEW ACCESS REQUEST**\n\n"
        f"👤 Name: `{user.first_name or 'Unknown'}`\n"
        f"🔹 Username: `{username}`\n"
        f"🆔 User ID: `{user_id}`\n\n"
        "Kya is user ko access dena hai?"
    )

    try:
        bot.send_message(
            OWNER_ID,
            owner_message,
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    except Exception as e:
        print("Owner notification error:", e)

    bot.answer_callback_query(
        call.id,
        "✅ Request owner ko bhej di gayi."
    )

    bot.edit_message_text(
        "⏳ **ACCESS REQUEST SENT**\n\n"
        "Aapki request owner ke paas bhej di gayi hai.\n"
        "Approval ka wait karein.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )


# =========================================================
#                    APPROVE USER
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("approve:")
)
def approve_user(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(
            call.id,
            "❌ You are not authorized."
        )
        return

    user_id = call.data.split(":", 1)[1]

    approved = load_json(APPROVED_FILE)
    requests = load_json(REQUESTS_FILE)

    # Add user & Remove pending request
    approved[user_id] = True
    requests.pop(user_id, None)

    save_json(APPROVED_FILE, approved)
    save_json(REQUESTS_FILE, requests)

    # Update owner message
    try:
        bot.edit_message_text(
            "✅ **ACCESS APPROVED**\n\n"
            f"🆔 User ID: `{user_id}`\n\n"
            "Ab ye user bot use kar sakta hai.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
    except:
        pass

    # Notify user
    try:
        bot.send_message(
            int(user_id),
            "🎉 **ACCESS APPROVED!**\n\n"
            "Owner ne aapki request approve kar di hai.\n\n"
            "Ab aap mobile number bhej kar bot use kar sakte hain.",
            parse_mode="Markdown"
        )
    except Exception as e:
        print("User notification error:", e)

    bot.answer_callback_query(
        call.id,
        "✅ User approved."
    )


# =========================================================
#                    REJECT USER
# =========================================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("reject:")
)
def reject_user(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(
            call.id,
            "❌ You are not authorized."
        )
        return

    user_id = call.data.split(":", 1)[1]

    requests = load_json(REQUESTS_FILE)
    requests.pop(user_id, None)

    save_json(REQUESTS_FILE, requests)

    # Update owner message
    try:
        bot.edit_message_text(
            "❌ **ACCESS REQUEST REJECTED**\n\n"
            f"🆔 User ID: `{user_id}`",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
    except:
        pass

    # Notify user
    try:
        bot.send_message(
            int(user_id),
            "❌ **ACCESS DENIED**\n\n"
            "Aapki access request approve nahi hui.",
            parse_mode="Markdown"
        )
    except:
        pass

    bot.answer_callback_query(
        call.id,
        "❌ Request rejected."
    )


# =========================================================
#                    REVOKE ACCESS
# =========================================================

@bot.message_handler(commands=["revoke"])
def revoke_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(
            message,
            "❌ Ye command sirf owner use kar sakta hai."
        )
        return

    parts = message.text.split()

    if len(parts) != 2:
        bot.reply_to(
            message,
            "Usage:\n/revoke USER_ID"
        )
        return

    user_id = parts[1]
    approved = load_json(APPROVED_FILE)

    if user_id in approved:
        del approved[user_id]
        save_json(APPROVED_FILE, approved)

        bot.reply_to(
            message,
            f"✅ Access revoked.\n\nUser ID: `{user_id}`",
            parse_mode="Markdown"
        )

        try:
            bot.send_message(
                int(user_id),
                "🚫 **ACCESS REVOKED**\n\n"
                "Owner ne aapka access remove kar diya hai.",
                parse_mode="Markdown"
            )
        except:
            pass
    else:
        bot.reply_to(
            message,
            "❌ Ye user approved list mein nahi hai."
        )


# =========================================================
#                    MAIN SEARCH
# =========================================================

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id

    if not has_access(user_id):
        bot.reply_to(
            message,
            "🔒 **ACCESS DENIED**\n\n"
            "Aapko pehle owner se access lena hoga.",
            reply_markup=access_button(),
            parse_mode="Markdown"
        )
        return

    number = message.text.strip()

    if not number.isdigit():
        bot.reply_to(
            message,
            "⚠️ Kripya sirf digits/mobile number bhejein."
        )
        return

    wait_msg = bot.reply_to(
        message,
        "🔍 Searching details, please wait..."
    )

    try:
        response = requests.get(
            API_URL,
            params={"search": number},
            timeout=12
        )

        if response.status_code != 200:
            bot.edit_message_text(
                "❌ API Server Error. Please try again later.",
                chat_id=message.chat.id,
                message_id=wait_msg.message_id
            )
            return

        raw_text = response.text.strip()

        start_idx = raw_text.find("{")
        end_idx = raw_text.rfind("}")

        if start_idx == -1 or end_idx == -1:
            bot.edit_message_text(
                "❌ Invalid API response format.",
                chat_id=message.chat.id,
                message_id=wait_msg.message_id
            )
            return

        clean_json_str = raw_text[start_idx:end_idx + 1]
        data = json.loads(clean_json_str)

        records = data.get("records", [])

        if not records:
            bot.edit_message_text(
                "❌ Is number ka koi record nahi mila.",
                chat_id=message.chat.id,
                message_id=wait_msg.message_id
            )
            return

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

    except json.JSONDecodeError:
        bot.edit_message_text(
            "❌ API ne valid JSON return nahi kiya.",
            chat_id=message.chat.id,
            message_id=wait_msg.message_id
        )

    except requests.exceptions.Timeout:
        bot.edit_message_text(
            "⏱️ API response timeout. Please try again.",
            chat_id=message.chat.id,
            message_id=wait_msg.message_id
        )

    except requests.exceptions.RequestException:
        bot.edit_message_text(
            "❌ API connection error. Please try again later.",
            chat_id=message.chat.id,
            message_id=wait_msg.message_id
        )

    except Exception as e:
        bot.edit_message_text(
            f"❌ Error: {str(e)}",
            chat_id=message.chat.id,
            message_id=wait_msg.message_id
        )


# =========================================================
#                    START BOT
# =========================================================

print("====================================")
print("      SIM DATABASE BOT RUNNING")
print("====================================")
print("Owner ID:", OWNER_ID)

bot.infinity_polling(skip_pending=True)
            
