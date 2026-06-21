import import os
import re
import telebot
import requests
from bs4 import BeautifulSoup
from flask import Flask, request

BOT_TOKEN = "8818835832:AAGkz81AY6ACsFXwd8ikGvKqYkvfBLJnA8"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# 
def get_direct_link(url):
    """
    যেকোনো শর্ট লিংক থেকে ডিরেক্ট লিংক বের করার ফাংশন 
    (লিংক শর্টেনার সাইট ভেদে এখানে লজিক আপডেট করতে হয়)
    """
    try:
        # ব্রাউজার হিসেবে রিকোয়েস্ট পাঠানো যেন সাইট ব্লক না করে
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        session = requests.Session()
        response = session.get(url, headers=headers, allow_redirects=True, timeout=15)
        
        # যদি লিংকের ভেতরে adrinolinks থাকে, তবে সেটির এপিআই থেকে সরাসরি ডিরেক্ট ইউআরএল বের করা
        if "adrinolinks.in" in url:
            api_url = f"https://adrinolinks.in/api?api=05061dfd717773f6447b2fa218a28dd91fefdc2c&url={url}"
            api_res = session.get(api_url).json()
            if 'url' in api_res:
                return api_res['url']
        
        # পেজের HTML থেকে রিডাইরেক্ট লিংক বা ডাউনলোড লিংক ক্র্যাক করা
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ১. মেটা রিডাইরেক্ট চেক করা
        meta_refresh = soup.find('meta', attrs={'http-equiv': 'refresh'})
        if meta_refresh:
            content = meta_refresh.get('content', '')
            match = re.search(r'url=(https?://.+)', content, re.IGNORECASE)
            if match:
                return match.group(1)
                
        # ২. কোনো ' a ' ট্যাগের ভেতরে ডিরেক্ট ডাউনলোড লিংক থাকলে সেটি খোঁজা
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'drive.google.com' in href or 'mediafire.com' in href or 'mega.nz' in href:
                return href
                
        # যদি বাইপাস না হয়, তবে ফাইনাল রিডাইরেক্ট হওয়া লিংকটি রিটার্ন করা
        return response.url
        
    except Exception as e:
        return url

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 স্বাগতম! যেকোনো শর্ট লিংক পাঠান, আমি সরাসরি ডিরেক্ট ডাউনলোড লিংক বের করে দেব।")

@bot.message_handler(func=lambda message: True)
def process_link(message):
    url = message.text
    if url.startswith("http://") or url.startswith("https://"):
        waiting_msg = bot.reply_to(message, "⏳ ডিরেক্ট লিংক খোঁজা হচ্ছে, দয়া করে অপেক্ষা করুন...")
        
        # বাইপাস ফাংশন কল করা
        direct_url = get_direct_link(url)
        
        if direct_url:
            bot.edit_message_text(f"✅ **সফলভাবে ডিরেক্ট লিংক পাওয়া গেছে!**\n\n🔗 **ডাউনলোড লিংক:** `{direct_url}`",
                                  chat_id=message.chat.id, message_id=waiting_msg.message_id, parse_mode="Markdown")
        else:
            bot.edit_message_text("❌ দুঃখিত, এই লিংকটি বাইপাস করা সম্ভব হয়নি।",
                                  chat_id=message.chat.id, message_id=waiting_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ দয়া করে একটি সঠিক URL (http/https সহ) পাঠান।")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route("/")
def index():
    return "Direct Link Bypasser Bot is running!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url="https://bypass-bot-om04.onrender.com" + "/" + BOT_TOKEN)
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
