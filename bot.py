import os
import logging
import requests
from bs4 import BeautifulSoup
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
    update.message.reply_text("👋 আমি সরাসরি লিংক বাইপাস বোট। দয়া করে একটি লিংক পাঠান।")

def get_direct_link(url):
    try:
        # উন্নত হেডার যুক্ত করা হলো যেন সাইটগুলো সহজে ব্লক না করে
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        session = requests.Session()
        # allow_redirects=True দিয়ে সব রিডাইরেক্ট ফলো করা হচ্ছে
        response = session.get(url, headers=headers, allow_redirects=True, timeout=20)
        
        # যদি ফাইনাল ইউআরএল বদলে যায়, সেটিই সরাসরি লিংক
        if response.history:
            return response.url
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # মেটা রিফ্রেশ চেক
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            if 'url=' in content:
                return content.split('url=')[1].strip('\'"')
        
        # জাভাস্ক্রিপ্ট উইন্ডোজ লোকেশন রিডাইরেক্ট চেক
        for script in soup.find_all('script'):
            if 'window.location.href' in script.text:
                start_idx = script.text.find('http')
                if start_idx != -1:
                    end_idx = script.text.find('"', start_idx) or script.text.find("'", start_idx)
                    return script.text[start_idx:end_idx].strip()

        # গুগল ড্রাইভ বা মেগা লিংক অ্যাঙ্কর ট্যাগে খুঁজবে
        for a in soup.find_all('a', href=True):
            if 'drive.google.com' in a['href'] or 'mega.nz' in a['href'] or 'terabox.com' in a['href']:
                return a['href']
                
        return response.url
    except Exception as e:
        return f"ব বাইপাস করতে গিয়ে ত্রুটি: {str(e)}"

def handle_message(update, context):
    text = update.message.text
    if text.startswith('http://') or text.startswith('https://'):
        update.message.reply_text("⏳ লিংক প্রসেস হচ্ছে, দয়া করে অপেক্ষা করুন...")
        direct_url = get_direct_link(text)
        update.message.reply_text(f"🔗 সরাসরি লিংক পাওয়া গেছে:\n\n`{direct_url}`", parse_mode='Markdown')
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

    print("🤖 Bot and Web Server are starting...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
