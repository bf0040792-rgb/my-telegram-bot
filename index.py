import requests
import time
import json
import os

# ---------------------------
# Configuration
# ---------------------------
# Tumhara Token (Fixed)
TOKEN = "8434467890:AAEN2tmdRU3lbDLoLjFHlqUlB1Yh_baFdTM"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# Admin ID
ADMIN_ID = 8190715241 

# ---------------------------
# Send Message Function
# ---------------------------
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        # HTML mode hata diya taaki links waise hi dikhein jaise image mein hain
        # aur link preview (image) generate ho sake
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    try:
        requests.post(BASE_URL + "sendMessage", data=payload)
    except Exception as e:
        print(f"Message Sending Error: {e}")

# ---------------------------
# Welcome Message (UPDATED)
# ---------------------------
def send_welcome(chat_id):
    # Ye text bilkul tumhare screenshot jaisa hai
    welcome_text = (
        "Welcome!\n\n"
        "This bot supports:\n"
        "• Auto Reply\n"
        "• Keyword System\n"
        "• Admin Panel\n"
        "• Fast Response\n\n"
        "My YouTube Channel:\n"
        "https://www.youtube.com/@Aiapplication1\n"
        "Telegram Channel:\n"
        "https://t.me/A1Android"
    )

    # Buttons (Agar tumhe buttons nahi chahiye to niche wali 4 lines hata dena)
    buttons = {
        "keyboard": [
            [{"text": "My YouTube Channel"}, {"text": "Join Telegram Channel"}],
            [{"text": "Add Keyword (Admin)"}, {"text": "Help"}]
        ],
        "resize_keyboard": True
    }

    send_message(chat_id, welcome_text, buttons)

# ---------------------------
# Admin Panel
# ---------------------------
def send_admin_panel(chat_id):
    panel_text = (
        "Admin Panel\n"
        "Use commands to add keywords:\n"
        "Format: /add hello|Hi there!"
    )
    send_message(chat_id, panel_text)

# ---------------------------
# Keyword Storage (RAM)
# ---------------------------
keywords = {}

# ---------------------------
# Long Polling Bot Runner
# ---------------------------
def run_bot():
    offset = 0
    print("Bot is running...")
    
    while True:
        try:
            response = requests.get(BASE_URL + f"getUpdates?offset={offset}&timeout=10")
            data = response.json()

            if "result" in data:
                for update in data["result"]:
                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")

                    print(f"New Message from {chat_id}: {text}")

                    # /start command
                    if text == "/start":
                        send_welcome(chat_id)
                        continue
                    
                    # Admin Panel
                    if text == "/admin" and chat_id == ADMIN_ID:
                        send_admin_panel(chat_id)
                        continue

                    # Add Keyword
                    if text.startswith("/add") and chat_id == ADMIN_ID:
                        try:
                            content = text.replace("/add", "").strip()
                            if "|" in content:
                                key, reply = content.split("|", 1)
                                keywords[key.strip().lower()] = reply.strip()
                                send_message(chat_id, f"✅ Keyword Saved:\nKey: {key}\nReply: {reply}")
                            else:
                                send_message(chat_id, "❌ Format Wrong. Use: /add hello|Hi there")
                        except Exception as e:
                            send_message(chat_id, f"Error: {e}")
                        continue

                    # Auto Reply
                    if text.lower() in keywords:
                        send_message(chat_id, keywords[text.lower()])

        except Exception as e:
            print("Connection Error:", e)
            time.sleep(2)

if __name__ == "__main__":
    run_bot()