import os
import telebot
import requests
from flask import Flask, request

BOT_TOKEN = "8818835832:AAGkz81AY6ACXsFXwd8ikGvKqYkvfBLJnA8"
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 স্বাগতম! যেকোনো vplink বা শর্টলিংক পাঠান, আমি আসল লিংক বের করে দেব।")

@bot.message_handler(func=lambda message: True)
def bypass_link(message):
    url = message.text
    if "http" in url:
        waiting_msg = bot.reply_to(message, "⏳ বাইপাস করা হচ্ছে, দয়া করে একটু অপেক্ষা করুন...")
        try:
            api_url = f"https://adrinolinks.in/api?api=9eeef64bb93bf40ea318cbbf34cb74438fa741ea&url={url}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                data = response.json()
                # API রেসপন্স থেকে লিংক বের করার আধুনিক মেথড
                bypassed_url = data.get("url") or data.get("shortenedUrl") or str(data)
                bot.edit_message_text(f"✅ **সফলভাবে বাইপাস হয়েছে!**\n\n🔗 **আসল লিংক:** {bypassed_url}", 
                                      chat_id=message.chat.id, message_id=waiting_msg.message_id)
            else:
                bot.edit_message_text("❌ দুঃখিত! সার্ভার থেকে সঠিক রেসপন্স আসেনি।", 
                                      chat_id=message.chat.id, message_id=waiting_msg.message_id)
        except Exception as e:
            bot.edit_message_text(f"⚠️ সমস্যা হয়েছে: {str(e)}", 
                                  chat_id=message.chat.id, message_id=waiting_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ দয়া করে একটি সঠিক লিংক (http/https সহ) পাঠান।")

@app.route('/' + BOT_TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

@app.route("/")
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    # নিচের লিংকের জায়গায় পরবর্তীতে রেন্ডার সার্ভারের লিংক বসবে
    bot.set_webhook(url="https://bypass-bot-om04.onrender.com" + "/" + BOT_TOKEN)
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
