import os
import logging
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from flask import Flask
import threading

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
PORT = int(os.environ.get('PORT', 8080))

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Server is Online and Running!"

def start(update, context):
    update.message.reply_text("👋 আমি ইন্ডিয়ান লিংক বাইপাস বোট। দয়া করে যেকোনো শর্টেনার লিংক (যেমন adrinolinks) পাঠান।")

def get_direct_link_via_api(url):
    try:
        # বাইপাস ভিআইপি (Bypass.VIP) এপিআই ব্যবহার করা হলো
        api_url = f"https://api.bypass.vip/?url={url}"
        response = requests.get(api_url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 200:
                return data.get("result", "লিংক পাওয়া যায়নি।")
            else:
                return f"এপিআই ইরর: {data.get('message', 'বাইপাস ব্যর্থ হয়েছে।')}"
        else:
            return "সার্ভার থেকে রেসপন্স আসেনি।"
    except Exception as e:
        return f"ত্রুটি: {str(e)}"

def handle_message(update, context):
    text = update.message.text
    if text.startswith('http://') or text.startswith('https://'):
        update.message.reply_text("⏳ লিংক বাইপাস হচ্ছে, দয়া করে অপেক্ষা করুন...")
        direct_url = get_direct_link_via_api(text)
        update.message.reply_text(f"🔗 সরাসরি ডাউনলোড লিংক:\n\n{direct_url}", disable_web_page_preview=True)
    else:
        update.message.reply_text("⚠️ দয়া করে একটি সঠিক URL (http বা https সহ) পাঠান।")

def run_flask():
    app.run(host="0.0.0.0", port=PORT)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    print("🤖 Bot is starting via API Bypass method...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
