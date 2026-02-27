from flask import Flask, request
import telebot
import os, requests, re

# Security: TOKEN is pulled from your Vercel Environment Variables
TOKEN = os.getenv('TOKEN')
CHANNEL = '@invvault'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# Trusted Studios for official content
TRUSTED_STUDIOS = ["Marvel", "Warner Bros", "DC", "Sony Pictures", "Paramount", "Universal", "Netflix", "Prime Video", "Zee Cinema", "T-Series", "YRF", "Disney"]

@app.route('/', methods=['GET'])
def index():
    return "P.A Bot Cloud Engine is Online 🟢"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Error', 400

def get_verified_link(query):
    try:
        url = f"https://www.youtube.com/results?search_query={query}+official+trailer+-shorts"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).text
        vids = re.findall(r"watch\?v=(\S{11})", res)
        if vids:
            for vid in vids[:8]:
                link = f"https://www.youtube.com/watch?v={vid}"
                meta = requests.get(f"https://www.youtube.com/oembed?url={link}", timeout=3).json()
                if any(s in meta.get('author_name', '') for s in TRUSTED_STUDIOS):
                    return link
            return f"https://www.youtube.com/watch?v={vids[0]}"
    except: pass
    return None

@bot.message_handler(commands=['start', 'reset'])
def start(message):
    img = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1000"
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🇮🇳 Hindi Hits", callback_data="hindi"),
        telebot.types.InlineKeyboardButton("🇺🇸 Hollywood", callback_data="english"),
        telebot.types.InlineKeyboardButton("👻 Ghost/Horror", callback_data="ghost"),
        telebot.types.InlineKeyboardButton("🍿 Action", callback_data="action"),
        telebot.types.InlineKeyboardButton("🔥 TOP HITS", callback_data="top")
    )
    bot.send_photo(message.chat.id, img, caption="⚡ **CINEMA TITAN CLOUD**\nSelect a portal:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_vault(call):
    bot.answer_callback_query(call.id, "🚀 Fetching blockbuster...")
    q_map = {"hindi": "hindi+trailer", "english": "hollywood+trailer", "ghost": "horror+trailer", "action": "action+trailer", "top": "trending+trailer"}
    link = get_verified_link(q_map.get(call.data))
    if link:
        bot.send_message(CHANNEL, f"🎬 **VAULT UPDATE**\n━━━━━━━━━━━━━━━━━━━━\n📺 Watch: {link}\n\n🚀 @invvault Exclusive\n━━━━━━━━━━━━━━━━━━━━")
    else:
        bot.answer_callback_query(call.id, "⚠️ Studio Busy.", show_alert=True)
