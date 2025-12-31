import requests
import time
import json
import os
from flask import Flask
from threading import Thread

# ---------------------------
# FAKE WEB SERVER
# ---------------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running! 🤖"

def run_web_server():
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
GROUP_ID = "@A1Android" 

DATA_FILE = "keywords.json"

def load_keywords():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_keywords(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

keywords = load_keywords()

# ---------------------------
# TELEGRAM FUNCTIONS
# ---------------------------
def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        requests.post(BASE_URL + "sendMessage", data=payload)
    except:
        pass

def delete_message(chat_id, message_id):
    try:
        requests.post(BASE_URL + "deleteMessage", data={"chat_id": chat_id, "message_id": message_id})
    except:
        pass

def send_welcome(chat_id):
    welcome_text = "👋 Welcome!\n\nMain Group ko manage karta hoon. Sirf wahi messages allow honge jinka link admin ne save kiya hai."
    buttons = {
        "keyboard": [
            [{"text": "Add Keyword (Admin)"}],
            [{"text": "Help"}]
        ],
        "resize_keyboard": True
    }
    send_message(chat_id, welcome_text, buttons)

# ---------------------------
# MAIN BOT LOOP
# ---------------------------
def run_bot():
    global keywords
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
                    msg_id = msg["message_id"]
                    text = msg.get("text", "")
                    user_id = msg.get("from", {}).get("id")

                    # --- PRIVATE CHAT ---
                    if msg["chat"]["type"] == "private":
                        if text == "/start":
                            send_welcome(chat_id)
                        elif text == "Add Keyword (Admin)" and user_id == ADMIN_ID:
                            send_message(chat_id, "📝 Likhein: `/add keyword|link`")
                        elif text.startswith("/add") and user_id == ADMIN_ID:
                            try:
                                parts = text.split(" ", 1)[1]
                                key, val = parts.split("|", 1)
                                keywords[key.strip().lower()] = val.strip()
                                save_keywords(keywords)
                                send_message(chat_id, f"✅ Saved: {key.strip()}")
                                send_message(GROUP_ID, f"📢 New link added for: *{key.strip()}*")
                            except:
                                send_message(chat_id, "❌ Error! Format: `/add keyword|link`")

                    # --- GROUP CHAT ---
                    elif msg["chat"]["type"] in ["group", "supergroup"]:
                        if user_id == ADMIN_ID:
                            continue
                        
                        query = text.lower().strip()
                        if query in keywords:
                            send_message(chat_id, f"📦 **Link:** {keywords[query]}")
                        else:
                            # Agar keyword nahi mila to message delete karo
                            delete_message(chat_id, msg_id)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    keep_alive()
    run_bot()
