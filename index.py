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
GROUP_USERNAME = "@A1Android" # Aapke group ka username

# Database file
DATA_FILE = "database.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

keywords = load_data()

# ---------------------------
# TELEGRAM FUNCTIONS
# ---------------------------
def send_message(chat_id, text):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    requests.post(BASE_URL + "sendMessage", data=payload)

def delete_message(chat_id, message_id):
    payload = {"chat_id": chat_id, "message_id": message_id}
    requests.post(BASE_URL + "deleteMessage", data=payload)

# ---------------------------
# MAIN BOT LOGIC
# ---------------------------
def run_bot():
    global keywords
    offset = 0
    print("Bot is Active...")
    
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

                    # 1. Admin Command: /add key|link (Private mein ya Group mein)
                    if text.startswith("/add") and user_id == ADMIN_ID:
                        content = text.replace("/add", "").strip()
                        if "|" in content:
                            key, link = content.split("|", 1)
                            keywords[key.strip().lower()] = link.strip()
                            save_data(keywords)
                            send_message(chat_id, f"✅ Keyword Saved: {key.strip()}")
                        continue

                    # 2. Group Control Logic
                    # Hum check karenge ki message group se aaya hai
                    if msg["chat"]["type"] in ["group", "supergroup"]:
                        # Agar Admin message kar raha hai to ignore karein (taki admin chat kar sake)
                        if user_id == ADMIN_ID:
                            continue
                        
                        word = text.lower().strip()
                        
                        # Agar word database mein hai to link bhejo
                        if word in keywords:
                            reply = f"📦 **Available Link for {word.upper()}:**\n\n🔗 {keywords[word]}"
                            send_message(chat_id, reply)
                        else:
                            # AGAR WORD NAHI HAI TO MESSAGE DELETE KARO
                            delete_message(chat_id, msg_id)
                            print(f"Deleted unauthorized message: {text}")

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    keep_alive()
    run_bot()
