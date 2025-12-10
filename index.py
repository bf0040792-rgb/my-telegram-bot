import requests
import time
import json
import os
from flask import Flask
from threading import Thread

# ---------------------------
# FAKE WEB SERVER (Render ko khush rakhne ke liye)
# ---------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running! 🤖"

def run_web_server():
    # Render se PORT lo ya default 8080 use karo
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()

# ---------------------------
# BOT CONFIGURATION
# ---------------------------
TOKEN = "8434467890:AAEN2tmdRU3lbDLoLjFHlqUlB1Yh_baFdTM"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_ID = 8190715241 

# ---------------------------
# FUNCTIONS
# ---------------------------
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(BASE_URL + "sendMessage", data=payload)
    except Exception as e:
        print(f"Error: {e}")

def send_welcome(chat_id):
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
    buttons = {
        "keyboard": [
            [{"text": "My YouTube Channel"}, {"text": "Join Telegram Channel"}],
            [{"text": "Add Keyword (Admin)"}, {"text": "Help"}]
        ],
        "resize_keyboard": True
    }
    send_message(chat_id, welcome_text, buttons)

def send_admin_panel(chat_id):
    panel_text = "Admin Panel\nUse: /add hello|Hi there!"
    send_message(chat_id, panel_text)

# ---------------------------
# MAIN BOT LOOP
# ---------------------------
keywords = {}

def run_bot():
    offset = 0
    print("Bot is starting...")
    
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

                    # Commands
                    if text == "/start":
                        send_welcome(chat_id)
                    elif text == "/admin" and chat_id == ADMIN_ID:
                        send_admin_panel(chat_id)
                    elif text.startswith("/add") and chat_id == ADMIN_ID:
                        try:
                            content = text.replace("/add", "").strip()
                            if "|" in content:
                                key, reply = content.split("|", 1)
                                keywords[key.strip().lower()] = reply.strip()
                                send_message(chat_id, f"✅ Saved: {key} -> {reply}")
                            else:
                                send_message(chat_id, "❌ Use: /add key|reply")
                        except:
                            send_message(chat_id, "❌ Error adding keyword")
                    
                    # Auto Reply
                    elif text.lower() in keywords:
                        send_message(chat_id, keywords[text.lower()])

        except Exception as e:
            print(f"Connection Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    # Pehle Fake Server start karo
    keep_alive()
    # Fir Bot start karo
    run_bot()