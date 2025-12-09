import requests
import time
import json
import os

# ---------------------------
# Configuration
# ---------------------------
# Yahan apna Token daalo ya GitHub Secrets se load karo
TOKEN = os.environ.get(TOKEN = "8434467890:AAEN2tmdRU3lbDLoLjFHlqUlB1Yh_baFdTM") 
BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# Admin ID (Integer hona chahiye)
ADMIN_ID = 8190715241 

# ---------------------------
# Send Message Function
# ---------------------------
def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    try:
        requests.post(BASE_URL + "sendMessage", data=payload)
    except Exception as e:
        print(f"Message Sending Error: {e}")

# ---------------------------
# Welcome Message
# ---------------------------
def send_welcome(chat_id):
    welcome_text = (
        "<b>Welcome!</b>\n\n"
        "This bot supports:\n"
        "• Auto Reply\n"
        "• Keyword System\n"
        "• Admin Panel\n"
        "• Fast Response\n\n"
        "Subscribe: <a href='https://www.youtube.com'>YouTube</a>"
    )

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
        "<b>Admin Panel</b>\n"
        "Use commands to add keywords:\n"
        "Format: <code>/add hello|Hi there!</code>"
    )
    send_message(chat_id, panel_text)

# ---------------------------
# Keyword Storage (RAM)
# Note: Bot restart hone par ye data udd jayega.
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
            # Getting updates with timeout
            response = requests.get(BASE_URL + f"getUpdates?offset={offset}&timeout=10")
            data = response.json()

            if "result" in data:
                for update in data["result"]:
                    # Update offset to not read same message again
                    offset = update["update_id"] + 1

                    if "message" not in update:
                        continue

                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "")

                    print(f"New Message from {chat_id}: {text}")

                    # --- Commands Handling ---

                    # /start command
                    if text == "/start":
                        send_welcome(chat_id)
                        continue
                    
                    # Open Admin Panel (Only for Admin)
                    if text == "/admin" and chat_id == ADMIN_ID:
                        send_admin_panel(chat_id)
                        continue

                    # Add Keyword Logic: /add key|reply
                    if text.startswith("/add") and chat_id == ADMIN_ID:
                        try:
                            # Remove /add and split by |
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

                    # --- Auto Reply Logic ---
                    # Check if text matches any keyword
                    if text.lower() in keywords:
                        send_message(chat_id, keywords[text.lower()])
                    else:
                        # Optional: Echo or ignore unknown messages
                        # send_message(chat_id, "I don't understand.")
                        pass

        except Exception as e:
            print("Connection Error:", e)
            time.sleep(2)

if __name__ == "__main__":
    run_bot()