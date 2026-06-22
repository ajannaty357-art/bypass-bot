import os
import logging
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
PORT = int(os.environ.get('PORT', 5000))

def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 আমি সরাসরি লিংক বাইপাস বোট। দয়া করে একটি লিংক পাঠান।")

def get_direct_link(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        session = requests.Session()
        response = session.get(url, headers=headers, allow_redirects=True, timeout=15)
        
        if "gdtot" in url or "terabox" in url:
            # Add your specific bypass logic for GDTot/TeraBox here
            return response.url
        
        # General scraping logic for direct links
        soup = BeautifulSoup(response.content, 'html.parser')
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            if 'url=' in content:
                return content.split('url=')[1].strip()
        
        for a in soup.find_all('a', href=True):
            if 'drive.google.com' in a['href'] or 'mega.nz' in a['href']:
                return a['href']
                
        return response.url
    except Exception as e:
        return f"Error: {str(e)}"

def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    if text.startswith('http://') or text.startswith('https://'):
        update.message.reply_text("⏳ লিংক প্রসেস হচ্ছে, দয়া করে অপেক্ষা করুন...")
        direct_url = get_direct_link(text)
        update.message.reply_text(f"🔗 সরাসরি লিংক পাওয়া গেছে:\n\n`{direct_url}`", parse_mode='Markdown')
    else:
        update.message.reply_text("⚠️ দয়া করে একটি সঠিক URL (http বা https সহ) পাঠান।")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Railway Webhook / Polling setup (Webhook is preferred for Railway)
    # Use Railway assigned PORT
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
    updater.bot.set_webhook(f"https://{os.environ.get('RAILWAY_PUBLIC_DOMAIN')}/{TOKEN}")
    
    updater.idle()

if __name__ == '__main__':
    main()
