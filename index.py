import os
import json
import telebot
from flask import Flask
from threading import Thread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- CONFIGURATION ---
TOKEN = "8434467890:AAEN2tmdRU3lbDLoLjFHlqUlB1Yh_baFdTM"
ADMIN_ID = 8190715241
bot = telebot.TeleBot(TOKEN)

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

# Database structure: { "keyword": {"type": "text/doc", "content": "data/file_id"} }
db = load_data()

# --- WEB SERVER ---
app = Flask(__name__)
@app.route('/')
def home(): return "Bot is Running! 🤖"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- ADMIN COMMANDS ---

# 1. Add Text/Link: /add keyword|link
@bot.message_handler(commands=['add'])
def add_text(m):
    if m.from_user.id != ADMIN_ID: return
    try:
        content = m.text.replace("/add ", "").strip()
        if "|" in content:
            key, val = content.split("|", 1)
            db[key.strip().lower()] = {"type": "text", "content": val.strip()}
            save_data(db)
            bot.reply_to(m, f"✅ Text Saved for keyword: *{key.strip()}*", parse_mode="Markdown")
        else:
            bot.reply_to(m, "❌ Format: `/add keyword|link`", parse_mode="Markdown")
    except:
        bot.reply_to(m, "Error adding text.")

# 2. Add APK/File: Send File with Caption "/add keyword"
@bot.message_handler(content_types=['document', 'audio', 'video', 'photo'])
def add_file(m):
    if m.from_user.id != ADMIN_ID: return
    if m.caption and m.caption.startswith("/add"):
        try:
            key = m.caption.replace("/add", "").strip().lower()
            if not key:
                bot.reply_to(m, "❌ Please provide a keyword. Example caption: `/add myapp`")
                return
            
            file_id = ""
            file_type = ""
            
            if m.document:
                file_id = m.document.file_id
                file_type = "doc"
            elif m.photo:
                file_id = m.photo[-1].file_id
                file_type = "photo"
            
            db[key] = {"type": file_type, "content": file_id}
            save_data(db)
            bot.reply_to(m, f"✅ File/APK saved for keyword: *{key}*", parse_mode="Markdown")
        except:
            bot.reply_to(m, "Error saving file.")

# 3. List & Delete Menu
@bot.message_handler(commands=['list'])
def list_items(m):
    if m.from_user.id != ADMIN_ID: return
    if not db:
        bot.reply_to(m, "Database khali hai.")
        return
    
    bot.send_message(m.chat.id, "📂 **Saved Keywords List:**\nClick on Delete button to remove.")
    
    for key in db:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(f"Delete {key} 🗑️", callback_data=f"del_{key}"))
        item_type = db[key]['type']
        bot.send_message(m.chat.id, f"🔑 **Keyword:** `{key}`\n📁 **Type:** {item_type}", 
                         parse_mode="Markdown", reply_markup=markup)

# Callback for Delete Button
@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def delete_callback(call):
    key_to_del = call.data.replace("del_", "")
    if key_to_del in db:
        del db[key_to_del]
        save_data(db)
        bot.answer_callback_query(call.id, "Deleted successfully!")
        bot.edit_message_text(f"❌ Deleted: {key_to_del}", call.message.chat.id, call.message.message_id)

# --- GROUP PROTECTION LOGIC ---
@bot.message_handler(func=lambda m: True)
def group_filter(m):
    uid = m.from_user.id
    cid = m.chat.id
    
    if m.chat.type in ['group', 'supergroup']:
        if uid == ADMIN_ID: return # Admin bypass
        
        if m.text:
            msg_text = m.text.lower().strip()
            if msg_text in db:
                item = db[msg_text]
                if item['type'] == "text":
                    bot.send_message(cid, f"🔗 **Link:**\n{item['content']}")
                elif item['type'] == "doc":
                    bot.send_document(cid, item['content'], caption=f"📦 File for: {msg_text}")
                elif item['type'] == "photo":
                    bot.send_photo(cid, item['content'], caption=f"🖼️ Photo for: {msg_text}")
            else:
                try:
                    bot.delete_message(cid, m.message_id)
                except:
                    pass

# --- START ---
if __name__ == "__main__":
    Thread(target=run_web).start()
    print("Bot is starting...")
    bot.infinity_polling()
