import os
import json
import telebot
import time
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURATION ---
TOKEN = "8434467890:AAEN2tmdRU3lbDLoLjFHlqUlB1Yh_baFdTM"
ADMIN_ID = 8190715241
bot = telebot.TeleBot(TOKEN, threaded=False) # Threaded False se conflict kam hota hai

# --- DATABASE ---
DATA_FILE = "database.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

db = load_data()

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running! 🤖"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ADMIN COMMANDS ---

# Add Text/Link
@bot.message_handler(commands=['add'])
def add_text(m):
    if m.from_user.id != ADMIN_ID: return
    try:
        content = m.text.replace("/add ", "").strip()
        if "|" in content:
            key, val = content.split("|", 1)
            db[key.strip().lower()] = {"type": "text", "content": val.strip()}
            save_data(db)
            bot.reply_to(m, f"✅ Saved: *{key.strip()}*", parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ Format: `/add keyword|link`")
    except: pass

# Add APK/File (Send file with caption /add keyword)
@bot.message_handler(content_types=['document', 'audio', 'video', 'photo'])
def add_file(m):
    if m.from_user.id != ADMIN_ID: return
    if m.caption and m.caption.startswith("/add"):
        try:
            key = m.caption.replace("/add", "").strip().lower()
            file_id = m.document.file_id if m.document else (m.photo[-1].file_id if m.photo else None)
            if file_id:
                db[key] = {"type": "file", "content": file_id}
                save_data(db)
                bot.reply_to(m, f"✅ APK/File saved for: *{key}*", parse_mode="Markdown")
        except: pass

# List & Delete
@bot.message_handler(commands=['list'])
def list_items(m):
    if m.from_user.id != ADMIN_ID: return
    if not db:
        bot.send_message(m.chat.id, "Database khali hai.")
        return
    for key in db:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"Delete {key} 🗑️", callback_data=f"del_{key}"))
        bot.send_message(m.chat.id, f"🔑 Keyword: `{key}`", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def delete_callback(call):
    key = call.data.replace("del_", "")
    if key in db:
        del db[key]
        save_data(db)
        bot.edit_message_text(f"🗑️ Deleted: {key}", call.message.chat.id, call.message.message_id)

# --- GROUP LOGIC ---
@bot.message_handler(func=lambda m: True)
def group_filter(m):
    if m.chat.type in ['group', 'supergroup']:
        if m.from_user.id == ADMIN_ID: return
        
        msg_text = m.text.lower().strip() if m.text else ""
        if msg_text in db:
            item = db[msg_text]
            if item['type'] == "text":
                bot.send_message(m.chat.id, f"🔗 **Link:**\n{item['content']}", parse_mode="Markdown")
            else:
                bot.send_document(m.chat.id, item['content'], caption=f"📦 File: {msg_text}")
        else:
            try: bot.delete_message(m.chat.id, m.message_id)
            except: pass

# --- STARTUP WITH RETRY LOGIC ---
if __name__ == "__main__":
    Thread(target=run_web).start()
    print("Bot starting...")
    while True:
        try:
            # skip_pending=True purane conflict wale messages ko clear kar deta hai
            bot.infinity_polling(skip_pending=True)
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(5) # 5 second wait karke firse try karega
