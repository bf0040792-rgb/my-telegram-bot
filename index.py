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
def home(): return "Bot is Running! 🤖"

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_web_server).start()

# ---------------------------
# BOT CONFIGURATION
# ---------------------------
TOKEN = "8434467890:AAEN2tmdRU3lbDLoLjFHlqUlB1Yh_baFdTM"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_ID = 8190715241 
GROUP_ID = "@A1Android" # Aapka Group Username

DATA_FILE = "keywords.json"

def load_keywords():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {}

def save_keywords(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

keywords = load_keywords()

# ---------------------------
# FUNCTIONS
# ---------------------------
def send_message(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup: payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(BASE_URL + "sendMessage", data=payload)

def delete_message(chat_id, message_id):
    requests.post(BASE_URL + "deleteMessage", data={"chat_id": chat_id, "message_id": message_id})

def send_welcome(chat_id):
    welcome_text = "Welcome! Main aapke Group ko manage karunga.\n\nAdmin keywords add karne ke liye niche button use karein."
    buttons = {
        "keyboard": [
            [{"text": "My YouTube Channel"}, {"text": "Join Telegram Channel"}],
            [{"text": "Add Keyword (Admin)"}, {"text": "Help"}]
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
    print("Bot starting...")
    
    while True:
        try:
            response = requests.get(BASE_URL + f"getUpdates?offset={offset}&timeout=10").json()
            if "result" in response:
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    if "message" not in update: continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    msg_id = msg["message_id"]
                    text = msg.get("text", "")
                    user_id = msg.get("from", {}).get("id")

                    # --- PRIVATE CHAT LOGIC ---
                    if msg["chat"]["type"] == "private":
                        if text == "/start":
                            send_welcome(chat_id)
                        
                        elif text == "Add Keyword (Admin)" and user_id == ADMIN_ID:
                            send_message(chat_id, "📝 Naya link add karne ke liye niche diye format mein message bhejein:\n\n`/add keyword|link` \n\nExample: `/add GitHub|https://github.com`")
                        
                        elif text.startswith("/add") and user_id == ADMIN_ID:
                            try:
                                content = text.split(" ", 1)[1]
                                key, val = content.split("|", 1)
                                keywords[key.strip().lower()] = val.strip()
                                save_keywords(keywords)
                                send_message(chat_id, f"✅ Done! Ab jab koi group mein `{key.strip()}` likhega, main link bhej dunga.")
                                # Group mein notify karein
                                send_message(GROUP_ID, f"📢 Naya resource add kiya gaya hai: *{key.strip()}*")
                            except:
                                send_message(chat_id, "❌ Galat format! Use: `/add keyword|link`")

                        elif text == "Help":
                            send_message(chat_id, "Aap sirf wahi words likh sakte hain jo admin ne set kiye hain. Baki saare messages delete ho jayenge.")

                    # --- GROUP CHAT LOGIC ---
                    elif msg["chat"]["type"] in ["group", "supergroup"]:
                        if user_id == ADMIN_ID: continue # Admin ke messages delete nahi honge
                        
                        clean_text = text.lower().strip()
                        if clean_text in keywords:
                            reply = f"🤖 **Link found for {clean_text}:**\n\n{keywords[clean_text]}"
                            send_message(chat_id, reply)
                        else:
                            # Agar keyword match nahi hua, to message delete kar do
                            delete_message(chat_id, msg_id)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    keep_alive()
    run_bot()            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    keep_alive()
    run_bot()
