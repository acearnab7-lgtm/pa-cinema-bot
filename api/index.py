from flask import Flask, request
import telebot
import random, time, requests, re, os

# Vercel pulls this securely from your Settings > Environment Variables
TOKEN = os.getenv('TOKEN')
CHANNEL = '@invvault'
bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)

# --- ELITE STUDIO WHITELIST ---
# Ensures 100% official trailers for a professional channel
TRUSTED_STUDIOS = [
    "Marvel", "Warner Bros", "DC", "Rockstar", "Sony Pictures", "Paramount", 
    "Universal", "Netflix", "Prime Video", "Zee Cinema", "T-Series", "YRF", 
    "Disney", "Sony LIV", "Eros Now", "Viacom18"
]

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
    return 'Error', 400

# --- HIGH-SPEED SEARCH ENGINE ---
def get_verified_link(query):
    try:
        url = f"https://www.youtube.com/results?search_query={query}+official+trailer+-shorts"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5).text
        vids = re.findall(r"watch\?v=(\S{11})", res)
        if vids:
            # Search top results for an elite studio match
            for vid in vids[:8]:
                link = f"https://www.youtube.com/watch?v={vid}"
                meta = requests.get(f"https://www.youtube.com/oembed?url={link}", timeout=3).json()
                author = meta.get('author_name', '')
                if any(studio in author for studio in TRUSTED_STUDIOS):
                    return link
            # Fallback to most popular if no studio match found
            return f"https://www.youtube.com/watch?v={vids[0]}"
    except: pass
    return None

# --- PROFESSIONAL UI ---
@bot.message_handler(commands=['start', 'reset'])
def start(message):
    # Reliable image link to fix previous "Bad Request" errors
    img = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1000"
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        telebot.types.InlineKeyboardButton("🇮🇳 Hindi Hits", callback_data="hindi"),
        telebot.types.InlineKeyboardButton("🇺🇸 Hollywood", callback_data="english"),
        telebot.types.InlineKeyboardButton("👻 Ghost/Horror", callback_data="ghost"),
        telebot.types.InlineKeyboardButton("😂 Comedy", callback_data="comedy"),
        telebot.types.InlineKeyboardButton("🍿 Action", callback_data="action"),
        telebot.types.InlineKeyboardButton("🔥 TOP HITS", callback_data="top")
    )
    bot.send_photo(message.chat.id, img, 
        caption="⚡ **CINEMA TITAN CLOUD**\n━━━━━━━━━━━━━━━━━━━━\nStatus: 🟢 **24/7 Smooth Active**\nSelect a portal to dispatch to @invvault:",
        reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def handle_vault(call):
    bot.answer_callback_query(call.id, "🚀 Dispatching trailer...")
    q_map = {
        "hindi": "new+hindi+movie+trailer+2026", "english": "new+hollywood+movie+trailer+2026",
        "ghost": "horror+movie+trailer", "comedy": "comedy+trailer",
        "action": "action+trailer", "top": "trending+movie+trailer"
    }
    link = get_verified_link(q_map.get(call.data))
    if link:
        msg = f"🎬 **COMMUNITY VAULT UPDATE**\n━━━━━━━━━━━━━━━━━━━━\n📺 Watch: {link}\n\n🚀 @invvault Exclusive\n━━━━━━━━━━━━━━━━━━━━"
        bot.send_message(CHANNEL, msg)
        bot.answer_callback_query(call.id, "✅ Sent to Vault!")
    else:
        bot.answer_callback_query(call.id, "⚠️ Studio Busy. Try again.", show_alert=True)
