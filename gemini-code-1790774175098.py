import os
import telebot
from telebot import types
import google.generativeai as genai
from flask import Flask
from threading import Thread
import urllib.parse

# এনভায়রনমেন্ট ভ্যারিয়েবল বা সরাসরি টোকেন বসাতে পারেন
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

# Gemini API সেটআপ
genai.configure(api_key=GEMINI_API_KEY)

system_instruction = (
    "তুমি একজন খুব চটপটে, রসিক, রোমান্টিক এবং জ্ঞানী এআই বট। "
    "ব্যবহারকারী চাইলে তুমি ১. দুষ্টু-মিষ্টি গল্প ও ফান জোকস, "
    "২. রিলেশনশিপ টিপস ও মিষ্টি রোমান্টিক কথা, এবং "
    "৩. মানুষের মন ভালো করার মতো গভীর, সুন্দর ও অনুপ্রেরণামূলক ভালো কথা বলতে পারো। "
    "তোমার ভাষা হবে খুবই জীবন্ত, বন্ধুসুলভ এবং আকর্ষণীয় বাংলা।"
)

generation_config = {
    "temperature": 0.8,
    "max_output_tokens": 1000,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=system_instruction
)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# ফ্লাস্ক সার্ভার তৈরি (বটকে সবসময় জাগিয়ে রাখার জন্য)
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 8080)))

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

# টেলিগ্রাম কমান্ড হ্যান্ডলার (স্বাগত বার্তা ও বাটন সহ)
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "✨ আমাদের বটে ঢোকার জন্য স্বাগতম! ✨\n\n"
        "আমি আপনার পার্সোনাল এআই ফ্রেন্ড বট। আমার সাথে যা করতে পারবেন:\n"
        "📖 দুষ্টু-মিষ্টি গল্প ও ফান জোকস\n"
        "❤️ রোমান্টিক কথা ও রিলেশনশিপ টিপস\n"
        "🌟 মন ভালো করা গভীর ও সুন্দর ভালো কথা\n"
        "🎨 ছবি তৈরি করতে লিখুন: `/image [ছবির বর্ণনা]`\n\n"
        "💡 **আপনিও কি এমন একটি বট বানাতে চান?** নিচের বাটনে ক্লিক করে কোড ও সিস্টেম কপি করে নিজের বট বানিয়ে নিন!"
    )
    
    # ইনলাইন কিবোর্ড বাটন তৈরি (বট কপি করার লিংক বা সোর্স কোডের জন্য)
    markup = types.InlineKeyboardMarkup()
    # এখানে আপনার গিটহাব বা সোর্স কোডের লিংক বসিয়ে দিতে পারেন
    source_button = types.InlineKeyboardButton("🛠️ আমার মতো বট কপি করুন", url="https://github.com/your-username/your-repo-name")
    markup.add(source_button)
    
    bot.reply_to(message, welcome_text, reply_markup=markup)

@bot.message_handler(commands=['image'])
def generate_ai_image(message):
    query = message.text.replace('/image', '').strip()
    if not query:
        bot.reply_to(message, "⚠ ছবি তৈরির জন্য `/image` লিখে ছবির বর্ণনা দিন। যেমন: `/image a cute anime cat`")
        return
    
    bot.reply_to(message, "🎨 আপনার মনের মতো ছবি আঁকছি... একটু অপেক্ষা করুন!")
    
    try:
        encoded_query = urllib.parse.quote(query)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_query}"
        bot.send_photo(message.chat.id, image_url, caption=f"🖼️ আপনার ছবির বিষয়: *{query}*", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(message, "উফ! ছবি তৈরি করতে গিয়ে একটু সমস্যা হয়েছে। আবার চেষ্টা করুন!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "উফ! একটু সমস্যা হয়েছে, আবার চেষ্টা করো তো বন্ধু! 😉")

if __name__ == "__main__":
    keep_alive()
    print("Bot is running 24/7 with welcome message and copy link...")
    bot.infinity_polling()