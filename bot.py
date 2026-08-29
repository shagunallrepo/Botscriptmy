import requests
import time
import json
import os
import uuid
import threading
import random
import re
import html
import pyotp
from collections import Counter 
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from datetime import datetime 
from urllib.parse import urljoin

# ==========================================
# Configuration (Token & Owner ID)
# ==========================================
TOKEN = os.environ.get("BOT_TOKEN", "")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
FILE_URL = f"https://api.telegram.org/file/bot{TOKEN}/"

OWNER_ID = int(os.environ.get("BOT_OWNER_ID", "8450343222"))
BOT_USERNAME = ""
BOT_NAME = ""
DB_PATH = "data/bot.db"

# ==========================================
# Premium Emoji Database
# ==========================================
PEM = {
    "ok": '<tg-emoji emoji-id="5352694861990501856">✅</tg-emoji>',
    "no": '<tg-emoji emoji-id="5420130255174145507">❌</tg-emoji>',
    "warn": '<tg-emoji emoji-id="5336944168944047463">⚠️</tg-emoji>',
    "admin": '<tg-emoji emoji-id="5949327894567195412">📊</tg-emoji>',
    "user": '<tg-emoji emoji-id="5352861489541714456">👤</tg-emoji>',
    "file": '<tg-emoji emoji-id="5352721946054268944">📁</tg-emoji>',
    "rocket": '<tg-emoji emoji-id="5352597830089347330">🚀</tg-emoji>',
    "graph": '<tg-emoji emoji-id="5352877703043258544">📊</tg-emoji>',
    "money": '<tg-emoji emoji-id="5359437015752401733">💵</tg-emoji>',
    "gift": '<tg-emoji emoji-id="5420396762189831222">🎁</tg-emoji>',
    "msg": '<tg-emoji emoji-id="5337302974806922068">💬</tg-emoji>',
    "gear": '<tg-emoji emoji-id="5420155432272438703">⚙️</tg-emoji>',
    "link": '<tg-emoji emoji-id="5839375134061761681">🔗</tg-emoji>',
    "trash": '<tg-emoji emoji-id="5422557736330106570">🗑</tg-emoji>',
    "upload": '<tg-emoji emoji-id="5353001161878182134">📤</tg-emoji>',
    "world": '<tg-emoji emoji-id="5336972142066047577">🌐</tg-emoji>',
    "lock": '<tg-emoji emoji-id="5353022963132174959">🔐</tg-emoji>',
    "phone": '<tg-emoji emoji-id="5337132498965010628">📱</tg-emoji>',
    "num": '<tg-emoji emoji-id="5841276284155467413">🔢</tg-emoji>',
    "pin": '<tg-emoji emoji-id="5352922460897452503">📍</tg-emoji>',
    "star": '✨',
    "hi": '<tg-emoji emoji-id="5353027129250453493">👋</tg-emoji>',
    "tether": '<tg-emoji emoji-id="5359437015752401733">💵</tg-emoji>',
    "binance": '<tg-emoji emoji-id="5888561507557447441">🪙</tg-emoji>',
    "card": '<tg-emoji emoji-id="5472250091332993630">💳</tg-emoji>',
    "id": '<tg-emoji emoji-id="5841276284155467413">🆔</tg-emoji>',
    "group": '<tg-emoji emoji-id="5841494459904168607">👥</tg-emoji>',
    "owner": '<tg-emoji emoji-id="5951518619945931024">👑</tg-emoji>'
}

GLOBAL_BODY_EMOJIS = {
    "➖": "5870818207383686839", "🚫": "5334807341109908955", "😒": "5334763399299506604",
    "🖥": "5334880948259427772", "🌐": "5334590977837403844", "🌟": "5337102391244263212",
    "🕓": "5336983442125001376", "⌛": "5337172996211648018", "💬": "5337302974806922068",
    "🔐": "5337255927735163754", "🍏": "5337132498965010628", "❔": "5336850036145823599",
    "⚠️": "5336944168944047463", "🔥": "5337267511261960341", "💸": "5348469219761626211",
    "🥚": "5348390922507817684", "👨‍⚖": "5334763399299506604", "🐁": "5348494358205207761",
    "🧻": "5348486915026884464", "⚗": "5346311574221000149", "🛴": "5348075478634766440",
    "📊": "5353032893096567467", "🔢": "5352862640592949843", "👤": "5352861489541714456",
    "📁": "5352721946054268944", "🚀": "5352597830089347330", "💎": "5352838545826420397",
    "📍": "5352922460897452503", "👋": "5353027129250453493", "✅": "5352694861990501856",
    "1️⃣": "5352651766288652742", "2️⃣": "5355186458418257716", "3️⃣": "5352867219028091093",
    "4️⃣": "5352566657216714037", "5️⃣": "5353086880835474989", "6️⃣": "5354859211975071385",
    "7️⃣": "5352859127309707652", "8️⃣": "5352957533600389988", "9️⃣": "5353060913463204207",
    "🔤": "5352727417842606016", "📣": "5352980533150259581", "📤": "5353001161878182134",
    "✨": "5352552689983067014", "🔹": "5352638632278660622", "🎙": "5355102594886833928",
    "💴": "5352985330628730418", "📅": "5352585194295564660", "📴": "5352974971167611327",
    "✏️": "5395444784611480792", "📱": "5337132498965010628", "🔗": "5420517437885943844",
    "❌": "5420130255174145507", "⚙️": "5420155432272438703", "🫂": "5420145051336485498",
    "➕": "5420323438508155202", "🗑": "5422557736330106570", "🎁": "5420396762189831222",
    "➤": "5420618897898381296", "🏢": "5420156334215565595", "💳": "5190899075968441286",
    "📝": "5192739271886282680", "🛡": "5190447043545438788", "🤝": "5192805934073685937",
    "💰": "5190576863226933563", "👀": "5190645917711114179", "🕹": "5193100774988617665",
    "🟢": "5192812028632274956", "🧪": "5190781475468915802", "🎨": "5190751148704833975",
    "📂": "5257969839313526622", "🌍": "5780471598922337683", "📌": "5318986077455795572",
    "📢": "5789428375261023681", "🆔": "5352862640592949843", "📈": "5352877703043258544",
    "🔔": "5352980533150259581", "🏦": "5348469219761626211", "🧾": "5192739271886282680",
    "👨‍⚖️": "5334763399299506604", "🔍": "5463352748751753567",
    "🔑": "5197288647275071607",
    "👥": "5841494459904168607"
}

DEFAULT_CUSTOM_MESSAGES = {
    "start": {"text": "━━━━━━━━━━━━━━━\n👋 Hello <b>{name}</b>!\n━━━━━━━━━━━━━━━\n\n🚀 Welcome to <b>Amir OTP Bot</b>\n\n✨ Get instant OTP codes &amp; earn money with every verification!\n\n💎 <b>Fast • Reliable • Premium Service</b>\n\n━━━━━━━━━━━━━━━\n📱 Bot: @{bot_username}", "buttons": []},
    "get_number": {"text": f"{PEM['pin']} Select a service:", "buttons": []},
    "select_country": {"text": f"📌 Select a country for {{service}}:", "buttons": []}, 

    "traffic": {"text": f"{PEM['graph']} <b>Traffic Overview</b>\n\n{PEM['ok']} Available Numbers: {{avail}}\n{PEM['rocket']} Assigned Numbers: {{assigned}}", "buttons": []},
    "refer": {"text": f"➖➖➖➖➖➖➖\n« {PEM['gift']} REFER & EARN »\n➖➖➖➖➖➖➖\n{PEM['link']} YOUR LINK:\n<code>{{ref_link}}</code>\n➖➖➖➖➖➖➖\n{PEM['user']} TOTAL REFERS: <b>{{total_ref}}</b>\n➖➖➖➖➖➖➖\n{PEM['tether']} PER REFER: <b>{{ref_reward}} USDT</b>\n➖➖➖➖➖➖➖", "buttons": []},
    "withdrawal": {"text": f"➖➖➖➖➖➖➖\n《 {PEM['card']} WITHDRAWAL 》\n➖➖➖➖➖➖➖\n{PEM['msg']} Total OTP: {{total_otp}}\n➖➖➖➖➖➖➖\n{PEM['gift']} Total Refers: {{total_ref}}\n➖➖➖➖➖➖➖\n{PEM['tether']} BALANCE: {{bal}}\n➖➖➖➖➖➖➖\n{PEM['lock']} MINIMUM: {{min_w}}\n➖➖➖➖➖➖➖\nSELECT METHOD:", "buttons": []},
    "support": {"text": f"{PEM['msg']} Contact us for any help:", "buttons": []}
}

# ==========================================
# Database Setup (SQLite)
# ==========================================
import sqlite3

os.makedirs("data", exist_ok=True)

# ==========================================
# Local Numbers Folder (human-readable file backup, per service+country)
# e.g. numbers/egypt_whatsapp.txt — survives restarts even if the DB is reset.
# ==========================================
NUMBERS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "numbers")
os.makedirs(NUMBERS_DIR, exist_ok=True)

db_lock = threading.Lock()

def get_db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db_lock:
        conn = get_db_conn()
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0.0,
            total_refers INTEGER DEFAULT 0,
            total_otps INTEGER DEFAULT 0,
            banned INTEGER DEFAULT 0,
            verified INTEGER DEFAULT 0,
            referred_by INTEGER DEFAULT NULL,
            ref_paid INTEGER DEFAULT 0,
            username TEXT DEFAULT NULL,
            first_name TEXT DEFAULT NULL
        )""")
        # Migrate existing DBs — add columns if missing
        for col, typ in [("username", "TEXT"), ("first_name", "TEXT"), ("language", "TEXT")]:
            try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {typ} DEFAULT NULL")
            except: pass
        c.execute("""CREATE TABLE IF NOT EXISTS withdrawals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            method TEXT,
            account TEXT,
            status TEXT DEFAULT 'Pending',
            timestamp REAL
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS bot_settings_store (
            key TEXT PRIMARY KEY,
            value TEXT
        )""")
        conn.commit()
        conn.close()
    print("✅ SQLite Database Ready! (data/bot.db)")

init_db()


bot_settings = {
    "admins": [OWNER_ID],
    "panels": [], 
    "fw_groups": [],

    "otp_link": "https://t.me/your_otp_group",
    "fw_channel_link": "",
    "withdraw_on": True,
    "min_withdraw": 30.0,
    "otp_reward": 0.1,
    "refer_reward": 0.2,
    "service_otp_prices": {},
    "cooldown": 10,
    "num_req": 3,
    "num_share": 1, 
    "support_link": "https://t.me/your_support",
    "w_methods": [],
    "w_group": "", 
    
    "fj_on": False,
    "fj_channels": [],
    "refer_on": True,
    "voltx_keys": [],
    "voltx_services": {},
    "premium_flags": {
        "93": {"char": "🇦🇫", "iso": "AF", "name": "Afghanistan", "id": "5291937511591925566"},
        "358": {"char": "🇫🇮", "iso": "FI", "name": "Finland", "id": "5294049961191690629"},
        "355": {"char": "🇦🇱", "iso": "AL", "name": "Albania", "id": "5294202819077756005"},
        "213": {"char": "🇩🇿", "iso": "DZ", "name": "Algeria", "id": "5294048127240655242"},
        "1684": {"char": "🇦🇸", "iso": "AS", "name": "American Samoa", "id": "5291994273879709721"},
        "376": {"char": "🇦🇩", "iso": "AD", "name": "Andorra", "id": "5294215205763434181"},
        "244": {"char": "🇦🇴", "iso": "AO", "name": "Angola", "id": "5294516785482062829"},
        "1264": {"char": "🇦🇮", "iso": "AI", "name": "Anguilla", "id": "5292186323342350940"},
        "1268": {"char": "🇦🇬", "iso": "AG", "name": "Antigua & Barbuda", "id": "5294005972136647964"},
        "54": {"char": "🇦🇷", "iso": "AR", "name": "Argentina", "id": "5292208210495689627"},
        "374": {"char": "🇦🇲", "iso": "AM", "name": "Armenia", "id": "5291978717508164018"},
        "297": {"char": "🇦🇼", "iso": "AW", "name": "Aruba", "id": "5294007002928798927"},
        "61": {"char": "🇦🇺", "iso": "AU", "name": "Australia", "id": "5294444247779399477"},
        "43": {"char": "🇦🇹", "iso": "AT", "name": "Austria", "id": "5291975174160145850"},
        "994": {"char": "🇦🇿", "iso": "AZ", "name": "Azerbaijan", "id": "5294323533428579078"},
        "1242": {"char": "🇧🇸", "iso": "BS", "name": "Bahamas", "id": "5294031587321600012"},
        "973": {"char": "🇧🇭", "iso": "BH", "name": "Bahrain", "id": "5294108398516720753"},
        "880": {"char": "🇧🇩", "iso": "BD", "name": "Bangladesh", "id": "5291824687096027834"},
        "1246": {"char": "🇧🇧", "iso": "BB", "name": "Barbados", "id": "5294526187165471742"},
        "375": {"char": "🇧🇾", "iso": "BY", "name": "Belarus", "id": "5294134426018536120"},
        "32": {"char": "🇧🇪", "iso": "BE", "name": "Belgium", "id": "5291774466043435275"},
        "501": {"char": "🇧🇿", "iso": "BZ", "name": "Belize", "id": "5294171848068584842"},
        "229": {"char": "🇧🇯", "iso": "BJ", "name": "Benin", "id": "5293984969746566866"},
        "975": {"char": "🇧🇹", "iso": "BT", "name": "Bhutan", "id": "5294121983498277263"},
        "591": {"char": "🇧🇴", "iso": "BO", "name": "Bolivia", "id": "5294201479047957700"},
        "267": {"char": "🇧🇼", "iso": "BW", "name": "Botswana", "id": "5294026179957772585"},
        "55": {"char": "🇧🇷", "iso": "BR", "name": "Brazil", "id": "5291892229751723900"},
        "673": {"char": "🇧🇳", "iso": "BN", "name": "Brunei", "id": "5292098293692650297"},
        "359": {"char": "🇧🇬", "iso": "BG", "name": "Bulgaria", "id": "5294308947719640437"},
        "226": {"char": "🇧🇫", "iso": "BF", "name": "Burkina Faso", "id": "5294153164960848949"},
        "257": {"char": "🇧🇮", "iso": "BI", "name": "Burundi", "id": "5294051631933967760"},
        "855": {"char": "🇰🇭", "iso": "KH", "name": "Cambodia", "id": "5294225191562400452"},
        "237": {"char": "🇨🇲", "iso": "CM", "name": "Cameroon", "id": "5291997306126626950"},
        "1": {"char": "🇺🇸", "iso": "US", "name": "United States", "id": "5294244076533600593"},
        "238": {"char": "🇨🇻", "iso": "CV", "name": "Cape Verde", "id": "5292203503211535593"},
        "236": {"char": "🇨🇫", "iso": "CF", "name": "Central African Republic", "id": "5294210571493724819"},
        "235": {"char": "🇹🇩", "iso": "TD", "name": "Chad", "id": "5291780728105753403"},
        "56": {"char": "🇨🇱", "iso": "CL", "name": "Chile", "id": "5294231037012888049"},
        "86": {"char": "🇨🇳", "iso": "CN", "name": "China", "id": "5294068833277990704"},
        "57": {"char": "🇨🇴", "iso": "CO", "name": "Colombia", "id": "5294010206974397371"},
        "269": {"char": "🇰🇲", "iso": "KM", "name": "Comoros", "id": "5294351381996521508"},
        "242": {"char": "🇨🇬", "iso": "CG", "name": "Congo", "id": "5294035229453865597"},
        "682": {"char": "🇨🇰", "iso": "CK", "name": "Cook Islands", "id": "5292098684534675100"},
        "506": {"char": "🇨🇷", "iso": "CR", "name": "Costa Rica", "id": "5292063805105263554"},
        "225": {"char": "🇨🇮", "iso": "CI", "name": "Cote d Ivoire", "id": "5293991322003200135"},
        "385": {"char": "🇭🇷", "iso": "HR", "name": "Croatia", "id": "5291999676948569127"},
        "53": {"char": "🇨🇺", "iso": "CU", "name": "Cuba", "id": "5291963947115631526"},
        "357": {"char": "🇨🇾", "iso": "CY", "name": "Cyprus", "id": "5294062721539526918"},
        "420": {"char": "🇨🇿", "iso": "CZ", "name": "Czech Republic", "id": "5294242852467923382"},
        "45": {"char": "🇩🇰", "iso": "DK", "name": "Denmark", "id": "5294531860817268837"},
        "253": {"char": "🇩🇯", "iso": "DJ", "name": "Djibouti", "id": "5294127214768468283"},
        "1767": {"char": "🇩🇲", "iso": "DM", "name": "Dominica", "id": "5294485513825178032"},
        "1809": {"char": "🇩🇴", "iso": "DO", "name": "Dominican Republic", "id": "5294522197140857947"},
        "593": {"char": "🇪🇨", "iso": "EC", "name": "Ecuador", "id": "5292083733753517221"},
        "20": {"char": "🇪🇬", "iso": "EG", "name": "Egypt", "id": "5293992082212409502"},
        "503": {"char": "🇸🇻", "iso": "SV", "name": "El Salvador", "id": "5294337307388695687"},
        "240": {"char": "🇬🇶", "iso": "GQ", "name": "Equatorial Guinea", "id": "5292170045416297012"},
        "291": {"char": "🇪🇷", "iso": "ER", "name": "Eritrea", "id": "5291922054004625949"},
        "372": {"char": "🇪🇪", "iso": "EE", "name": "Estonia", "id": "5291951143818123103"},
        "251": {"char": "🇪🇹", "iso": "ET", "name": "Ethiopia", "id": "5292245976143124155"},
        "388": {"char": "🇪🇺", "iso": "EU", "name": "European Union", "id": "5291992809295861098"},
        "350": {"char": "🇬🇮", "iso": "GI", "name": "Gibraltar", "id": "5292055799286224027"},
        "220": {"char": "🇬🇲", "iso": "GM", "name": "Gambia", "id": "5294399820637688352"},
        "299": {"char": "🇬🇱", "iso": "GL", "name": "Greenland", "id": "5292014752283774878"},
        "33": {"char": "🇫🇷", "iso": "FR", "name": "France", "id": "5291817660529533837"},
        "241": {"char": "🇬🇦", "iso": "GA", "name": "Gabon", "id": "5294321325815389139"},
        "995": {"char": "🇬🇪", "iso": "GE", "name": "Georgia", "id": "5294349389131697267"},
        "49": {"char": "🇩🇪", "iso": "DE", "name": "Germany", "id": "5292013274815028523"},
        "233": {"char": "🇬🇭", "iso": "GH", "name": "Ghana", "id": "5294347396266873249"},
        "30": {"char": "🇬🇷", "iso": "GR", "name": "Greece", "id": "5291948395039054764"},
        "245": {"char": "🇬🇼", "iso": "GW", "name": "Guinea-Bissau", "id": "5294409819321550432"},
        "502": {"char": "🇬🇹", "iso": "GT", "name": "Guatemala", "id": "5294336633078831209"},
        "224": {"char": "🇬🇳", "iso": "GN", "name": "Guinea", "id": "5291892096607739008"},
        "592": {"char": "🇬🇾", "iso": "GY", "name": "Guyana", "id": "5292062692708736193"},
        "509": {"char": "🇭🇹", "iso": "HT", "name": "Haiti", "id": "5292045130587462814"},
        "504": {"char": "🇭🇳", "iso": "HN", "name": "Honduras", "id": "5291901034434682297"},
        "852": {"char": "🇭🇰", "iso": "HK", "name": "Hong Kong", "id": "5292166459118606932"},
        "36": {"char": "🇭🇺", "iso": "HU", "name": "Hungary", "id": "5294229581018975260"},
        "354": {"char": "🇮🇸", "iso": "IS", "name": "Iceland", "id": "5294354358408859664"},
        "91": {"char": "🇮🇳", "iso": "IN", "name": "India", "id": "5291933173674957761"},
        "98": {"char": "🇮🇷", "iso": "IR", "name": "Iran", "id": "5294220170745630736"},
        "964": {"char": "🇮🇶", "iso": "IQ", "name": "Iraq", "id": "5294325010897327367"},
        "353": {"char": "🇮🇪", "iso": "IE", "name": "Ireland", "id": "5294471971793293647"},
        "44": {"char": "🇬🇧", "iso": "GB", "name": "United Kingdom", "id": "5293993521026453119"},
        "972": {"char": "🇮🇱", "iso": "IL", "name": "Israel", "id": "5294069056616289553"},
        "39": {"char": "🇮🇹", "iso": "IT", "name": "Italy", "id": "5291826830284709120"},
        "1876": {"char": "🇯🇲", "iso": "JM", "name": "Jamaica", "id": "5294505107465982830"},
        "81": {"char": "🇯🇵", "iso": "JP", "name": "Japan", "id": "5291799063321139445"},
        "962": {"char": "🇯🇴", "iso": "JO", "name": "Jordan", "id": "5291988613112814801"},
        "7": {"char": "🇷🇺", "iso": "RU", "name": "Russia", "id": "5294335323113807278"},
        "254": {"char": "🇰🇪", "iso": "KE", "name": "Kenya", "id": "5292111852904416801"},
        "686": {"char": "🇰🇮", "iso": "KI", "name": "Kiribati", "id": "5294538934628405146"},
        "850": {"char": "🇰🇵", "iso": "KP", "name": "North Korea", "id": "5294193812531333564"},
        "82": {"char": "🇰🇷", "iso": "KR", "name": "South Korea", "id": "5294408281723262763"},
        "965": {"char": "🇰🇼", "iso": "KW", "name": "Kuwait", "id": "5292066437920218075"},
        "996": {"char": "🇰🇬", "iso": "KG", "name": "Kyrgyzstan", "id": "5292091954320922577"},
        "856": {"char": "🇱🇦", "iso": "LA", "name": "Laos", "id": "5291981530711746037"},
        "371": {"char": "🇱🇻", "iso": "LV", "name": "Latvia", "id": "5292236016113966127"},
        "961": {"char": "🇱🇧", "iso": "LB", "name": "Lebanon", "id": "5294193108156699621"},
        "266": {"char": "🇱🇸", "iso": "LS", "name": "Lesotho", "id": "5292040693886247604"},
        "231": {"char": "🇱🇷", "iso": "LR", "name": "Liberia", "id": "5291793810576137439"},
        "218": {"char": "🇱🇾", "iso": "LY", "name": "Libya", "id": "5291858711826946840"},
        "423": {"char": "🇱🇮", "iso": "LI", "name": "Liechtenstein", "id": "5292048742654957785"},
        "370": {"char": "🇱🇹", "iso": "LT", "name": "Lithuania", "id": "5294343084119708700"},
        "352": {"char": "🇱🇺", "iso": "LU", "name": "Luxembourg", "id": "5294423709245787718"},
        "389": {"char": "🇲🇰", "iso": "MK", "name": "Macedonia", "id": "5294023611567332075"},
        "261": {"char": "🇲🇬", "iso": "MG", "name": "Madagascar", "id": "5291991568050312348"},
        "265": {"char": "🇲🇼", "iso": "MW", "name": "Malawi", "id": "5294241881805312589"},
        "60": {"char": "🇲🇾", "iso": "MY", "name": "Malaysia", "id": "5291858351049696702"},
        "960": {"char": "🇲🇻", "iso": "MV", "name": "Maldives", "id": "5292004203844097218"},
        "223": {"char": "🇲🇱", "iso": "ML", "name": "Mali", "id": "5292086972158858331"},
        "356": {"char": "🇲🇹", "iso": "MT", "name": "Malta", "id": "5294532213004588353"},
        "692": {"char": "🇲🇭", "iso": "MH", "name": "Marshall Islands", "id": "5294180730060954484"},
        "222": {"char": "🇲🇷", "iso": "MR", "name": "Mauritania", "id": "5294429743674840973"},
        "230": {"char": "🇲🇺", "iso": "MU", "name": "Mauritius", "id": "5294127824653797277"},
        "52": {"char": "🇲🇽", "iso": "MX", "name": "Mexico", "id": "5294535073452809778"},
        "691": {"char": "🇫🇲", "iso": "FM", "name": "Micronesia", "id": "5291838156113470124"},
        "373": {"char": "🇲🇩", "iso": "MD", "name": "Moldova", "id": "5294158486425325375"},
        "377": {"char": "🇲🇨", "iso": "MC", "name": "Monaco", "id": "5294378161117614233"},
        "976": {"char": "🇲🇳", "iso": "MN", "name": "Mongolia", "id": "5294316532631883496"},
        "212": {"char": "🇲🇦", "iso": "MA", "name": "Morocco", "id": "5292108962391414885"},
        "258": {"char": "🇲🇿", "iso": "MZ", "name": "Mozambique", "id": "5294086708931874940"},
        "95": {"char": "🇲🇲", "iso": "MM", "name": "Myanmar", "id": "5294254478944393569"},
        "264": {"char": "🇳🇦", "iso": "NA", "name": "Namibia", "id": "5292021761670404922"},
        "674": {"char": "🇳🇷", "iso": "NR", "name": "Nauru", "id": "5294463274484521342"},
        "977": {"char": "🇳🇵", "iso": "NP", "name": "Nepal", "id": "5294458756178924088"},
        "31": {"char": "🇳🇱", "iso": "NL", "name": "Netherlands", "id": "5291917797692042265"},
        "64": {"char": "🇳🇿", "iso": "NZ", "name": "New Zealand", "id": "5294189019347833274"},
        "505": {"char": "🇳🇮", "iso": "NI", "name": "Nicaragua", "id": "5294240825243358100"},
        "227": {"char": "🇳🇪", "iso": "NE", "name": "Niger", "id": "5291809418487290691"},
        "234": {"char": "🇳🇬", "iso": "NG", "name": "Nigeria", "id": "5294456308047563965"},
        "683": {"char": "🇳🇺", "iso": "NU", "name": "Niue", "id": "5294471336138134209"},
        "47": {"char": "🇳🇴", "iso": "NO", "name": "Norway", "id": "5291761718580502030"},
        "968": {"char": "🇴🇲", "iso": "OM", "name": "Oman", "id": "5291813666209946812"},
        "92": {"char": "🇵🇰", "iso": "PK", "name": "Pakistan", "id": "5291825606219029010"},
        "970": {"char": "🇵🇸", "iso": "PS", "name": "Palestine", "id": "5294289826525238172"},
        "507": {"char": "🇵🇦", "iso": "PA", "name": "Panama", "id": "5291959935616178405"},
        "675": {"char": "🇵🇬", "iso": "PG", "name": "Papua New Guinea", "id": "5291917995260533077"},
        "595": {"char": "🇵🇾", "iso": "PY", "name": "Paraguay", "id": "5294525611639852679"},
        "63": {"char": "🇵🇭", "iso": "PH", "name": "Philippines", "id": "5291798075478661634"},
        "51": {"char": "🇵🇪", "iso": "PE", "name": "Peru", "id": "5292099427564018941"},
        "48": {"char": "🇵🇱", "iso": "PL", "name": "Poland", "id": "5292190970496963836"},
        "351": {"char": "🇵🇹", "iso": "PT", "name": "Portugal", "id": "5294436555492973610"},
        "1787": {"char": "🇵🇷", "iso": "PR", "name": "Puerto Rico", "id": "5292121516580820347"},
        "974": {"char": "🇶🇦", "iso": "QA", "name": "Qatar", "id": "5292166360334357676"},
        "40": {"char": "🇷🇴", "iso": "RO", "name": "Romania", "id": "5294107724206856227"},
        "250": {"char": "🇷🇼", "iso": "RW", "name": "Rwanda", "id": "5294191265615729158"},
        "378": {"char": "🇸🇲", "iso": "SM", "name": "San Marino", "id": "5292147350809106831"},
        "239": {"char": "🇸🇹", "iso": "ST", "name": "Sao Tome & Principe", "id": "5292183188016222701"},
        "966": {"char": "🇸🇦", "iso": "SA", "name": "Saudi Arabia", "id": "5294163983983463099"},
        "221": {"char": "🇸🇳", "iso": "SN", "name": "Senegal", "id": "5292087023698466689"},
        "381": {"char": "🇷🇸", "iso": "RS", "name": "Serbia", "id": "5294458584380230360"},
        "248": {"char": "🇸🇨", "iso": "SC", "name": "Seychelles", "id": "5291891186074672309"},
        "232": {"char": "🇸🇱", "iso": "SL", "name": "Sierra Leone", "id": "5294494314213167952"},
        "65": {"char": "🇸🇬", "iso": "SG", "name": "Singapore", "id": "5294451304410663668"},
        "421": {"char": "🇸🇰", "iso": "SK", "name": "Slovakia", "id": "5294538440707166931"},
        "386": {"char": "🇸🇮", "iso": "SI", "name": "Slovenia", "id": "5294279359689938006"},
        "677": {"char": "🇸🇧", "iso": "SB", "name": "Solomon Islands", "id": "5294283890880433237"},
        "252": {"char": "🇸🇴", "iso": "SO", "name": "Somalia", "id": "5294058817414255960"},
        "27": {"char": "🇿🇦", "iso": "ZA", "name": "South Africa", "id": "5294325281480266304"},
        "34": {"char": "🇪🇸", "iso": "ES", "name": "Spain", "id": "5294513087515216901"},
        "94": {"char": "🇱🇰", "iso": "LK", "name": "Sri Lanka", "id": "5292102670264328257"},
        "249": {"char": "🇸🇩", "iso": "SD", "name": "Sudan", "id": "5294177148058228060"},
        "597": {"char": "🇸🇷", "iso": "SR", "name": "Suriname", "id": "5294396668131692138"},
        "268": {"char": "🇸🇿", "iso": "SZ", "name": "Swaziland", "id": "5294312482477724867"},
        "46": {"char": "🇸🇪", "iso": "SE", "name": "Sweden", "id": "5291737091238026321"},
        "41": {"char": "🇨🇭", "iso": "CH", "name": "Switzerland", "id": "5291791748991835084"},
        "963": {"char": "🇸🇾", "iso": "SY", "name": "Syria", "id": "5294013428199869487"},
        "886": {"char": "🇹🇼", "iso": "TW", "name": "Taiwan", "id": "5294095745543069603"},
        "992": {"char": "🇹🇯", "iso": "TJ", "name": "Tajikistan", "id": "5294120269806328883"},
        "255": {"char": "🇹🇿", "iso": "TZ", "name": "Tanzania", "id": "5292146096678658977"},
        "66": {"char": "🇹🇭", "iso": "TH", "name": "Thailand", "id": "5293994384314882755"},
        "228": {"char": "🇹🇬", "iso": "TG", "name": "Togo", "id": "5294097669688415562"},
        "676": {"char": "🇹🇴", "iso": "TO", "name": "Tonga", "id": "5294283689016973348"},
        "1868": {"char": "🇹🇹", "iso": "TT", "name": "Trinidad & Tobago", "id": "5294362935458548705"},
        "216": {"char": "🇹🇳", "iso": "TN", "name": "Tunisia", "id": "5294484680601521871"},
        "90": {"char": "🇹🇷", "iso": "TR", "name": "Turkey", "id": "5293993400767367408"},
        "993": {"char": "🇹🇲", "iso": "TM", "name": "Turkmenistan", "id": "5294098958178603764"},
        "1649": {"char": "🇹🇨", "iso": "TC", "name": "Turks & Caicos", "id": "5294320866253884749"},
        "256": {"char": "🇺🇬", "iso": "UG", "name": "Uganda", "id": "5294192317882716626"},
        "971": {"char": "🇦🇪", "iso": "AE", "name": "UAE", "id": "5294314831824835370"},
        "380": {"char": "🇺🇦", "iso": "UA", "name": "Ukraine", "id": "5294263837678131580"},
        "678": {"char": "🇻🇺", "iso": "VU", "name": "Vanuatu", "id": "5294448585696368047"},
        "998": {"char": "🇺🇿", "iso": "UZ", "name": "Uzbekistan", "id": "5294217645304864345"},
        "598": {"char": "🇺🇾", "iso": "UY", "name": "Uruguay", "id": "5291928449210932974"},
        "58": {"char": "🇻🇪", "iso": "VE", "name": "Venezuela", "id": "5294476442854247878"},
        "84": {"char": "🇻🇳", "iso": "VN", "name": "Vietnam", "id": "5294235963340379688"},
        "1340": {"char": "🇻🇮", "iso": "VI", "name": "US Virgin Islands", "id": "5294228039125718124"},
        "967": {"char": "🇾🇪", "iso": "YE", "name": "Yemen", "id": "5294058972033076492"},
        "260": {"char": "🇿🇲", "iso": "ZM", "name": "Zambia", "id": "5294100109229838880"},
        "263": {"char": "🇿🇼", "iso": "ZW", "name": "Zimbabwe", "id": "5294422158762592930"},
        "62": {"char": "🇮🇩", "iso": "ID", "name": "Indonesia", "id": "5224405893960969756"}
    },
    "premium_apps": {
        "FACEBOOK": {"char": "📘", "id": "5323261730283863478", "name": "Facebook"},
        "INSTAGRAM": {"char": "📸", "id": "5319160079465857105", "name": "Instagram"},
        "MESSENGER": {"char": "💬", "id": "5323687726615119535", "name": "Messenger"},
        "META": {"char": "🌐", "id": "5321447183910716259", "name": "Meta"},
        "DISCORD": {"char": "🎮", "id": "5325612636467903082", "name": "Discord"},
        "SIGNAL": {"char": "🔒", "id": "5328050550099427291", "name": "Signal"},
        "TELEGRAM": {"char": "✈️", "id": "5330237710655306682", "name": "Telegram"},
        "THREADS": {"char": "🧵", "id": "5334592721594105691", "name": "Threads"},
        "REDNOTE": {"char": "📝", "id": "5334707727933390944", "name": "Rednote"},
        "VK": {"char": "🔵", "id": "5334853932915114338", "name": "VK"},
        "WECHAT": {"char": "💬", "id": "5332524123610430820", "name": "WeChat"},
        "TIKTOK": {"char": "🎵", "id": "5280662183057825163", "name": "TikTok"},
        "SNAPCHAT": {"char": "👻", "id": "5330248916224983855", "name": "Snapchat"},
        "REDDIT": {"char": "🤖", "id": "5330321861949539755", "name": "Reddit"},
        "APPLE": {"char": "🍎", "id": "5307884768111631358", "name": "Apple"},
        "TWITTER": {"char": "🐦", "id": "5330337435500951363", "name": "X/Twitter"},
        "X": {"char": "✖️", "id": "5330337435500951363", "name": "X/Twitter"},
        "NETFLIX": {"char": "🎬", "id": "5296258364655805333", "name": "Netflix"},
        "WHATSAPP": {"char": "📞", "id": "5334998226636390258", "name": "WhatsApp"},
        "BOLT": {"char": "🚗", "id": "5346188613602263703", "name": "Bolt"},
        "SPOTIFY": {"char": "🎶", "id": "5346074681004801565", "name": "Spotify"},
        "PAYPAL": {"char": "💰", "id": "5364111181415996352", "name": "PayPal"},
        "MASTERCARD": {"char": "💳", "id": "5364036341610858181", "name": "Mastercard"},
        "TETHER": {"char": "💵", "id": "5359437015752401733", "name": "Tether"},
        "CHATGPT": {"char": "🤖", "id": "5359726582447487916", "name": "ChatGPT"},
        "MICROSOFT": {"char": "🪟", "id": "5370857634440170316", "name": "Microsoft"},
        "STEAM": {"char": "🎮", "id": "5298975451161565553", "name": "Steam"},
        "BINANCE": {"char": "💹", "id": "5888561507557447441", "name": "Binance"},
        "TEAMS": {"char": "💼", "id": "5453866707888152017", "name": "Teams"},
        "GMAIL": {"char": "📧", "id": "5303416490295304868", "name": "Gmail"},
        "GOOGLEDRIVE": {"char": "📁", "id": "5303051181851943323", "name": "Google Drive"},
        "UBER": {"char": "🚖", "id": "5298715455316303708", "name": "Uber"},
        "GROKAI": {"char": "🤖", "id": "5454065032298009119", "name": "Grok AI"},
        "GITHUB": {"char": "💻", "id": "5303382121967001310", "name": "GitHub"},
        "CANVA": {"char": "🎨", "id": "5429229538527690282", "name": "Canva"},
    },
    "custom_messages": DEFAULT_CUSTOM_MESSAGES.copy()
}


number_batches = {}
used_numbers_list = []
voltx_assigned_numbers = {}
VOLTX_BASE_URL = "https://api.2oo9.cloud/MXS47FLFX0U/tnevs/@public/api"
total_uploaded_stats = 0
total_assigned_stats = 0
processed_otps = set() 
recent_traffic = []
user_banned_cache = {}

# Active HTTP sessions for Auto Captcha Panels
panel_sessions = {}


def fetch_cpt_panel_cdrs(p, session, check_url):
    res = session.get(check_url, timeout=15)
    html_text = res.text

    if "login" in html_text.lower() or "signin" in html_text.lower() or any(x in html_text for x in ["Sign in to your account", "Please sign in", "Welcome back!"]):
        raise Exception("Session expired")

    soup = BeautifulSoup(html_text, 'html.parser')
    s_ajax_source = ""
    for script in soup.find_all("script"):
        script_text = script.string or ""
        match = re.search(r'sAjaxSource":\s*"([^"]+)"', script_text)
        if match:
            s_ajax_source = match.group(1)
            break

    results = []

    n_col_name = p.get("num_col_name", "number").lower()
    m_col_name = p.get("msg_col_name", "message").lower()
    # Convert 1-based user config to 0-based; None/0 means "auto-detect"
    _nu = p.get("num_col_idx")
    _mu = p.get("msg_col_idx")
    n_idx_cfg = int(_nu) - 1 if _nu and str(_nu).isdigit() and int(_nu) > 0 else None
    m_idx_cfg = int(_mu) - 1 if _mu and str(_mu).isdigit() and int(_mu) > 0 else None

    _N_WORDS = ["number", "num", "phone", "msisdn", "mobile", "destination", "dest", "caller"]
    _M_WORDS = ["message", "msg", "sms", "text", "content", "body"]
    _C_WORDS = ["cli", "client", "service", "app", "provider", "application", "sender", "source"]

    def _auto_detect_cols(col_names):
        """Given a list of column name strings, return (n_idx, m_idx, c_idx)."""
        n_i = m_i = c_i = -1
        for i, name in enumerate(col_names):
            nl = str(name).lower().strip()
            if n_i == -1 and any(w in nl for w in _N_WORDS):
                n_i = i
            if m_i == -1 and any(w in nl for w in _M_WORDS):
                m_i = i
            if c_i == -1 and any(w in nl for w in _C_WORDS):
                c_i = i
        return n_i, m_i, c_i

    def _smart_detect_from_data(rows_sample):
        """Scan first few data rows to guess number and message column indices."""
        if not rows_sample:
            return -1, -1, -1
        n_i = m_i = c_i = -1
        num_counts = {}
        msg_len = {}
        for row_val in rows_sample[:10]:
            if not isinstance(row_val, list):
                continue
            for ci, cell in enumerate(row_val):
                s = str(cell).strip()
                digits = re.sub(r'\D', '', s)
                if 7 <= len(digits) <= 15 and len(digits) == len(s.replace('+', '').replace(' ', '')):
                    num_counts[ci] = num_counts.get(ci, 0) + 1
                if len(s) > 15:
                    msg_len[ci] = msg_len.get(ci, 0) + len(s)
        if num_counts:
            n_i = max(num_counts, key=num_counts.get)
        if msg_len:
            m_i = max(msg_len, key=msg_len.get)
        return n_i, m_i, c_i

    if s_ajax_source:
        baseUrl = p.get("login_url", "").split("/client")[0].split("/login")[0].strip()
        if not baseUrl.startswith("http"):
            baseUrl = "http://" + baseUrl

        full_ajax_url = ""
        if s_ajax_source.startswith("http"):
            full_ajax_url = s_ajax_source
        elif s_ajax_source.startswith("/"):
            full_ajax_url = f"{baseUrl}{s_ajax_source}"
        else:
            last_slash_idx = check_url.rfind("/")
            current_dir = check_url[:last_slash_idx]
            full_ajax_url = f"{current_dir}/{s_ajax_source}"

        if "iDisplayLength" not in full_ajax_url:
            query_params = "sEcho=1&iColumns=10&iDisplayStart=0&iDisplayLength=250&sSearch=&iSortingCols=1&iSortCol_0=0&sSortDir_0=desc"
            divider = "&" if "?" in full_ajax_url else "?"
            full_ajax_url += f"{divider}{query_params}"

        ajax_headers = {"Referer": check_url, "X-Requested-With": "XMLHttpRequest"}
        ajax_res = session.get(full_ajax_url, headers=ajax_headers, timeout=15)
        data_dict = ajax_res.json()
        rows = data_dict.get("aaData", [])

        # Detect columns from aoColumns or sColumns in AJAX response
        n_i = n_idx_cfg if n_idx_cfg is not None else -1
        m_i = m_idx_cfg if m_idx_cfg is not None else -1
        c_i = -1

        if n_i == -1 or m_i == -1:
            ao_cols = data_dict.get("aoColumns", data_dict.get("columns", []))
            if ao_cols:
                col_names = []
                for col in ao_cols:
                    if isinstance(col, dict):
                        col_names.append(col.get("sTitle", col.get("title", col.get("data", ""))))
                    else:
                        col_names.append(str(col))
                dn, dm, dc = _auto_detect_cols(col_names)
                if n_i == -1 and dn >= 0: n_i = dn
                if m_i == -1 and dm >= 0: m_i = dm
                if c_i == -1 and dc >= 0: c_i = dc

            # Still not found → smart scan data rows
            if n_i == -1 or m_i == -1:
                dn, dm, dc = _smart_detect_from_data(rows)
                if n_i == -1 and dn >= 0: n_i = dn
                if m_i == -1 and dm >= 0: m_i = dm
                if c_i == -1 and dc >= 0: c_i = dc

            # Final fallback defaults (Number=col0, SMS=col3 for typical CDR panels)
            if n_i == -1: n_i = 0
            if m_i == -1: m_i = 3

        for row_val in rows:
            if not isinstance(row_val, list) or len(row_val) <= max(n_i, m_i):
                continue

            num_val = str(row_val[n_i]) if 0 <= n_i < len(row_val) else ""
            msg_val = str(row_val[m_i]) if 0 <= m_i < len(row_val) else ""
            cli_val = ""
            if 0 <= c_i < len(row_val):
                raw_c = str(row_val[c_i]).strip()
                if raw_c and not re.match(r'^\+?[\d\s\-]+$', raw_c):
                    cli_val = raw_c

            clean_num = re.sub(r'\D', '', num_val)
            if clean_num and 5 <= len(clean_num) <= 18:
                otp = extract_otp_code(msg_val)
                if otp and len(msg_val) > 4:
                    if not cli_val:
                        cli_val = detect_service(msg_val) or ""
                    results.append({"number": clean_num, "message": msg_val, "otp": otp, "cli": cli_val})

    else:
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if not rows:
                continue

            final_n_idx = n_idx_cfg if n_idx_cfg is not None else 0
            final_m_idx = m_idx_cfg if m_idx_cfg is not None else 3
            final_c_idx = -1

            # Auto-detect from header row
            header_cells = rows[0].find_all(['th', 'td'])
            for i, cell in enumerate(header_cells):
                c_text = cell.get_text(strip=True).lower()
                if n_idx_cfg is None and any(w in c_text for w in [n_col_name] + _N_WORDS):
                    final_n_idx = i
                if m_idx_cfg is None and any(w in c_text for w in [m_col_name] + _M_WORDS):
                    final_m_idx = i
                if any(w in c_text for w in _C_WORDS):
                    final_c_idx = i

            for row in rows:
                cols = row.find_all(['td', 'th'])
                if all(c.name == 'th' for c in cols):
                    continue
                if len(cols) <= max(final_n_idx, final_m_idx):
                    continue

                num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                cli_val = ""
                if 0 <= final_c_idx < len(cols):
                    raw_c = cols[final_c_idx].get_text(strip=True)
                    if raw_c and not re.match(r'^\+?[\d\s\-]+$', raw_c):
                        cli_val = raw_c

                clean_num = re.sub(r'\D', '', num_text)
                if clean_num and 5 <= len(clean_num) <= 18:
                    otp = extract_otp_code(msg_text)
                    if otp and len(msg_text) > 4:
                        if not cli_val:
                            cli_val = detect_service(msg_text) or ""
                        results.append({"number": clean_num, "message": msg_text, "otp": otp, "cli": cli_val})

    return results, html_text

# Track active number sessions to expire them automatically
user_active_sessions = {}


def load_db():
    global bot_settings, total_uploaded_stats, total_assigned_stats, pending_withdrawals, number_batches
    import json as _json
    # ── Load all bot_settings from DB ──────────────────────────────────────
    with db_lock:
        conn = get_db_conn()
        rows = conn.execute("SELECT key, value FROM bot_settings_store").fetchall()
        conn.close()
    RESERVED = {"__stats__", "__number_batches__"}
    # Keys that must stay as their default types even if DB has a stale value
    PROTECTED_DEFAULTS = {"premium_flags", "premium_apps"}
    for key, val in rows:
        if key in RESERVED or key in PROTECTED_DEFAULTS:
            continue
        try:
            bot_settings[key] = _json.loads(val)
        except Exception:
            bot_settings[key] = val
    # ── Load number_batches (uploaded numbers survive restarts) ─────────────
    with db_lock:
        conn = get_db_conn()
        nb_row = conn.execute("SELECT value FROM bot_settings_store WHERE key='__number_batches__'").fetchone()
        conn.close()
    if nb_row:
        try:
            loaded_batches = _json.loads(nb_row[0])
            if isinstance(loaded_batches, dict):
                number_batches = loaded_batches
                print(f"✅ Loaded {len(number_batches)} number batch(es) from DB")
        except Exception:
            pass
    # ── Restore any stock backed up in numbers/*.txt (survives even a DB reset) ──
    load_numbers_from_folder()
    # Always ensure OWNER_ID is in admins list after loading
    if OWNER_ID not in bot_settings.get("admins", []):
        bot_settings.setdefault("admins", []).insert(0, OWNER_ID)
    # ── Load stats ─────────────────────────────────────────────────────────
    with db_lock:
        conn = get_db_conn()
        stats_row = conn.execute("SELECT value FROM bot_settings_store WHERE key='__stats__'").fetchone()
        # ── Reload pending withdrawals from DB ──────────────────────────────
        pending_rows = conn.execute(
            "SELECT id, user_id, amount, method, account FROM withdrawals WHERE status='pending'"
        ).fetchall()
        conn.close()
    if stats_row:
        try:
            parsed = _json.loads(stats_row[0])
            total_uploaded_stats = parsed.get("uploaded", 0)
            total_assigned_stats = parsed.get("assigned", 0)
        except Exception:
            pass
    for row in pending_rows:
        db_id, uid, amt, method, account = row
        req_id = f"DB_{db_id}"
        pending_withdrawals[req_id] = {
            "user_id": uid, "amount": amt,
            "method": method, "number": account,
            "full_name": "", "db_id": db_id
        }
    print("✅ SQLite DB Loaded!")

def save_local_db():
    import json as _json
    # Only skip large static defaults — everything else (fw_groups, admins,
    # custom_messages, w_methods, keys, etc.) must be persisted.
    SKIP = {"premium_flags", "premium_apps"}
    with db_lock:
        conn = get_db_conn()
        for k, v in bot_settings.items():
            if k in SKIP:
                continue
            try:
                serialised = _json.dumps(v)
                conn.execute(
                    "INSERT INTO bot_settings_store (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?",
                    (k, serialised, serialised)
                )
            except Exception:
                pass
        # Save number_batches so uploaded numbers survive bot restarts
        try:
            nb_json = _json.dumps(number_batches)
            conn.execute("INSERT INTO bot_settings_store (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?",
                         ("__number_batches__", nb_json, nb_json))
        except Exception:
            pass
        # Stats (uploaded/assigned counts)
        try:
            st_json = _json.dumps({"uploaded": total_uploaded_stats, "assigned": total_assigned_stats})
            conn.execute("INSERT INTO bot_settings_store (key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=?",
                         ("__stats__", st_json, st_json))
        except Exception:
            pass
        conn.commit()
        conn.close()
    # Write users.txt for backup/export
    try:
        with db_lock:
            conn2 = get_db_conn()
            user_rows = conn2.execute("SELECT user_id, username, first_name FROM users").fetchall()
            conn2.close()
        os.makedirs("data", exist_ok=True)
        with open("data/users.txt", "w", encoding="utf-8") as uf:
            uf.write("user_id|username|first_name\n")
            for row in user_rows:
                uid2, uname2, fname2 = row[0], row[1] or "", row[2] or ""
                uf.write(f"{uid2}|{uname2}|{fname2}\n")
    except Exception:
        pass

def save_db():
    threading.Thread(target=save_local_db, daemon=True).start()

def _fs_sanitize(s):
    """Turn a service/country label into a safe lowercase filename fragment."""
    s = re.sub(r'[^a-z0-9]+', '_', str(s or "unknown").strip().lower())
    return s.strip('_') or "unknown"

def _fs_batch_id(service, country):
    """Deterministic batch id so every upload for the same service+country
    merges into ONE local backup file instead of scattering across many."""
    return f"fs_{_fs_sanitize(country)}_{_fs_sanitize(service)}"

def _fs_file_path(service, country):
    return os.path.join(NUMBERS_DIR, f"{_fs_sanitize(country)}_{_fs_sanitize(service)}.txt")

def _fs_sync_batch(batch_id):
    """Rewrite (or remove) the local numbers/*.txt backup file so it always
    mirrors the current numbers actually left in that batch. Called after
    every add/remove so a bot restart can restore stock straight from disk."""
    b = number_batches.get(batch_id)
    try:
        if not b:
            return
        service, country = b.get("service", "UNKNOWN"), b.get("country", "UNKNOWN")
        path = _fs_file_path(service, country)
        nums = [str(n.get("num", "")) for n in b.get("numbers", []) if n.get("num")]
        if nums:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(nums) + "\n")
        elif os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

def _fs_remove_file_for(service, country):
    try:
        path = _fs_file_path(service, country)
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

def load_numbers_from_folder():
    """On startup, restore any stock found in numbers/*.txt that isn't
    already loaded from the DB (e.g. DB was wiped/reset). Files are named
    <country>_<service>.txt and use the same deterministic fs_ batch id, so
    re-running this is always safe/idempotent."""
    restored_files = 0
    try:
        for fname in os.listdir(NUMBERS_DIR):
            if not fname.endswith(".txt"):
                continue
            fpath = os.path.join(NUMBERS_DIR, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    file_nums = [line.strip() for line in f if line.strip()]
            except Exception:
                continue
            if not file_nums:
                continue
            # Find any existing batch (fs_-based or legacy) already covering
            # this exact file so we don't duplicate numbers already in DB.
            existing_nums_all = set()
            for b in number_batches.values():
                for n in b.get("numbers", []):
                    existing_nums_all.add(str(n.get("num", "")).replace("+", "").replace(" ", "").replace("-", "").strip())
            base = fname[:-4]
            # base is "<country>_<service>" (both sanitized) — recover a
            # best-effort display service/country by matching sanitized parts
            # against premium_apps/premium_flags, falling back to raw text.
            service_guess, country_guess = "UNKNOWN", "UNKNOWN"
            for app_key, app_data in bot_settings.get("premium_apps", {}).items():
                if _fs_sanitize(app_key) and base.endswith("_" + _fs_sanitize(app_key)):
                    service_guess = app_key
                    country_guess = base[: -(len(_fs_sanitize(app_key)) + 1)]
                    break
            if service_guess == "UNKNOWN":
                # Fall back: split on last underscore
                if "_" in base:
                    country_guess, service_guess = base.rsplit("_", 1)
                else:
                    service_guess = base
            new_nums = [n for n in file_nums if n.replace("+", "").replace(" ", "").replace("-", "").strip() not in existing_nums_all]
            if not new_nums:
                continue
            b_id = _fs_batch_id(service_guess, country_guess)
            if b_id in number_batches:
                number_batches[b_id]["numbers"].extend({"num": n, "shares": 0, "used_by": []} for n in new_nums)
            else:
                number_batches[b_id] = {
                    "filename": fname, "service": service_guess, "country": country_guess,
                    "numbers": [{"num": n, "shares": 0, "used_by": []} for n in new_nums]
                }
            restored_files += 1
        if restored_files:
            print(f"✅ Restored stock from {restored_files} local numbers/*.txt file(s)")
    except Exception as e:
        print(f"⚠️ load_numbers_from_folder error: {e}")

def remove_number_after_otp(raw_num):
    """
    Called only when an OTP has actually been received for a number.
    Removes the matching number from stock (number_batches) and records it in
    used_numbers_list (with service/country) so it can be restocked later.
    Numbers that were merely assigned/shared to a user but never received an
    OTP are left untouched in stock.
    """
    clean_target = str(raw_num).replace("+", "").replace(" ", "").replace("-", "").strip()
    if not clean_target:
        return False
    for b_id, b_data in list(number_batches.items()):
        numbers = b_data.get("numbers", [])
        for idx, n_obj in enumerate(numbers):
            n_clean = str(n_obj.get("num", "")).replace("+", "").replace(" ", "").replace("-", "").strip()
            if n_clean == clean_target or (len(n_clean) >= 8 and len(clean_target) >= 8 and (n_clean.endswith(clean_target[-8:]) or clean_target.endswith(n_clean[-8:]))):
                used_numbers_list.append({
                    "num": n_obj.get("num"),
                    "service": b_data.get("service"),
                    "country": b_data.get("country")
                })
                del numbers[idx]
                save_db()
                _fs_sync_batch(b_id)
                return True
    return False

user_states = {}
temp_data = {}
user_cooldowns = {}
pending_withdrawals = {}
daily_otps = {}  # {user_id: {"date": "YYYY-MM-DD", "count": N}}

load_db()

# ==========================================
# Telegram API & Helpers
# ==========================================
tg_session = requests.Session() # 🌟 Keep-Alive Connection (Makes bot 10x faster)

def api_call(method, payload=None):
    url = f"{BASE_URL}/{method}"
    try:
        # 🌟 Added timeout to prevent hanging!
        res = tg_session.post(url, json=payload, timeout=15)
        return res.json()
    except Exception as e:
        return {}

def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendMessage", payload)

def send_photo(chat_id, photo_url_or_file_id, caption="", reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "photo": photo_url_or_file_id, "caption": caption, "parse_mode": parse_mode}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("sendPhoto", payload)

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode="HTML"):
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    if reply_markup: payload["reply_markup"] = reply_markup
    return api_call("editMessageText", payload)

def delete_message(chat_id, message_id):
    return api_call("deleteMessage", {"chat_id": chat_id, "message_id": message_id})

def answer_callback(callback_id, text="", show_alert=False):
    api_call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text, "show_alert": show_alert})

def send_document(chat_id, filename, text_content):
    url = f"{BASE_URL}/sendDocument"
    files = {'document': (filename, text_content)}
    data = {'chat_id': chat_id}
    try: requests.post(url, data=data, files=files)
    except: pass

all_known_users = set()

def sync_users_list():
    global all_known_users
    with db_lock:
        conn = get_db_conn()
        rows = conn.execute("SELECT user_id FROM users").fetchall()
        conn.close()
    all_known_users = set(str(r[0]) for r in rows)

threading.Thread(target=sync_users_list, daemon=True).start()

def register_user_local(uid, username=None, first_name=None):
    uid_str = str(uid)
    all_known_users.add(uid_str)
    with db_lock:
        conn = get_db_conn()
        conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (uid,))
        if username or first_name:
            conn.execute(
                "UPDATE users SET username=COALESCE(?,username), first_name=COALESCE(?,first_name) WHERE user_id=?",
                (username or None, first_name or None, uid)
            )
        conn.commit()
        conn.close()

def broadcast_copymessage(from_chat_id, msg_id):
    success = 0
    failed = 0
    users = list(all_known_users)
    
    # 🌟 Dedicated Connection Pool for Broadcast (Fixes Port Exhaustion & Network Lag)
    b_session = requests.Session()
    url = f"{BASE_URL}/copyMessage"
    
    for user_id in users:
        payload = {"chat_id": user_id, "from_chat_id": from_chat_id, "message_id": msg_id}
        try:
            res = b_session.post(url, json=payload, timeout=5).json()
            if res.get("ok"): success += 1
            else: failed += 1
        except:
            failed += 1
        time.sleep(0.035) # Safe speed (28 msgs/sec) to prevent Telegram Ban
        
    send_message(from_chat_id, render_body_text(f"📢 <b>Broadcast Completed!</b>\n✅ Success: {success}\n❌ Failed: {failed}\n👥 Total Sent: {len(users)}"))

def render_body_text(text):
    if not text: return str(text)
    parts = re.split(r'(<tg-emoji.*?</tg-emoji>)', str(text))
    for i in range(len(parts)):
        if not parts[i].startswith('<tg-emoji'):
            for normal_emj, prem_id in GLOBAL_BODY_EMOJIS.items():
                if normal_emj in parts[i]:
                    parts[i] = parts[i].replace(normal_emj, f'<tg-emoji emoji-id="{prem_id}">{normal_emj}</tg-emoji>')
    return "".join(parts)

def extract_premium_html(msg):
    text = msg.get("text", msg.get("caption", ""))
    entities = msg.get("entities", msg.get("caption_entities", []))
    if not entities: return text
    try:
        b_text = text.encode('utf-16-le')
        c_entities = [e for e in entities if e.get("type") == "custom_emoji"]
        c_entities.sort(key=lambda x: x["offset"], reverse=True)
        for ent in c_entities:
            offset = ent["offset"] * 2
            length = ent["length"] * 2
            eid = ent["custom_emoji_id"]
            emoji_char = b_text[offset:offset+length].decode('utf-16-le')
            html_tag = f'<tg-emoji emoji-id="{eid}">{emoji_char}</tg-emoji>'
            replacement = html_tag.encode('utf-16-le')
            b_text = b_text[:offset] + replacement + b_text[offset+length:]
        return b_text.decode('utf-16-le')
    except Exception as e:
        return text 

def get_flag_info_from_num(num):
    clean = num.replace("+", "").replace(" ", "")
    sorted_codes = sorted(bot_settings.get("premium_flags", {}).keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            data = bot_settings["premium_flags"][code]
            return data["char"], data.get("iso", "XX"), data.get("id")
    return "🌍", "XX", None

def get_flag_and_code(num):
    char, iso, _ = get_flag_info_from_num(num)
    return char, iso

def _get_phone_prefix(num):
    """Return the phone-country-prefix code (e.g. '880') that matches num, or '' if unknown."""
    clean = str(num).replace("+", "").replace(" ", "").replace("-", "")
    flags_db = bot_settings.get("premium_flags", {})
    sorted_codes = sorted(flags_db.keys(), key=len, reverse=True)
    for code in sorted_codes:
        if clean.startswith(code):
            return code
    return ""

def get_flag_info_html(num_or_iso):
    if len(num_or_iso) == 2:
        for code, data in bot_settings.get("premium_flags", {}).items():
            if data.get("iso") == num_or_iso:
                eid = data.get("id")
                char = data.get("char")
                if eid: return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
                return char
        return "🌍"
        
    char, _, eid = get_flag_info_from_num(num_or_iso)
    if eid:
        return f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
    return char

def generate_emoji_txt(mode):
    if mode == "flags":
        flags_db = bot_settings.get("premium_flags", {})
        if not flags_db:
            return None
        lines = []
        for code, data in flags_db.items():
            char = data.get("char", "")
            iso = data.get("iso", "XX")
            name = data.get("name", "")
            eid = data.get("id", "")
            json_part = json.dumps({"emoji": char, "id": eid}, ensure_ascii=False)
            lines.append(f"{name} ({code}) ({iso}) {char} {json_part}")
        return "\n".join(lines)
    else:
        apps_db = bot_settings.get("premium_apps", {})
        if not apps_db:
            return None
        lines = []
        for key, data in apps_db.items():
            char = data.get("char", "")
            name = data.get("name", key)
            eid = data.get("id", "")
            json_part = json.dumps({"emoji": char, "id": eid}, ensure_ascii=False)
            lines.append(f"{name} {char} {json_part}")
        return "\n".join(lines)

def mask_number(num):
    clean = num.replace("+", "").replace(" ", "")
    if len(clean) > 7:
        return f"+{clean[:4]}••{clean[-3:]}"
    elif len(clean) > 4:
        return f"+{clean[:2]}••{clean[-2:]}"
    return f"+{clean}"

# ==========================================
# 🌟 ADVANCED SERVICE & LANGUAGE DETECTION
# ==========================================

SERVICE_SMS_KEYWORDS = {
    # 🟢 Social Media & Chat
    "whatsapp":      ["whatsapp", "wa.me", "whatsapp business", "wa code", "واتساب", "واتساپ", "واٹس ایپ", "व्हाट्सएप", "వాట్సాప్", "왓츠앱", "whatsapp验证码", "וואטסאפ"],
    "facebook":      ["facebook", "fb", "fbook", "fb code", "facebook code", "facebook verification", "facebook account", "فيسبوك", "فيس بوك", "فیسبوک"],
    "instagram":     ["instagram", "insta", "ig code", "instagram code", "instagram confirmation", "انستغرام", "انستقرام", "اینستاگرام"],
    "telegram":      ["telegram", "tg", "tele", "telegram code", "tg code", "t.me", "تيليجرام", "تليجرام", "تلگرام"],
    "tiktok":        ["tiktok", "tik tok", "tikvideo", "tiktok code", "تيك توك", "تیک توک"],
    "snapchat":      ["snapchat", "snap code", "سناب شات", "سناپ چت"],
    "twitter":       ["twitter", "x.com", "twitter code", "تويتر", "توییتر"],
    "discord":       ["discord", "discord code", "ديسكورد"],
    "viber":         ["viber", "viber code", "فايبر", "وایبر"],
    "line":          ["line app", "line code", "line verification", "لاين"],
    "wechat":        ["wechat", "we chat", "wechat code", "微信", "وي تشات"],
    "signal":        ["signal app", "signal code", "سيجنال"],
    "linkedin":      ["linkedin", "linked in", "linkedin code", "لينكد إن"],
    "imo":           ["imo", "imo code", "imo verification", "ايمو"],
    "kakaotalk":     ["kakao", "kakaotalk", "kakao code", "كاكاو"],
    "qq":            ["tencent qq", "qq验证码"],
    "vk":            ["vkontakte", "vk code", "vk verification"],
    "messenger":     ["messenger", "fb messenger", "facebook messenger"],
    "meta":          ["meta code", "meta verification", "meta account", "meta platforms"],
    "threads":       ["threads", "threads code", "threads app", "threads verification"],
    "rednote":       ["rednote", "xiaohongshu", "red note", "小红书"],
    "reddit":        ["reddit", "redd.it", "reddit code", "reddit verification"],
    "skype":         ["skype", "skype code", "skype verification", "سكايب"],
    "zoom":          ["zoom", "zoom code", "zoom meeting", "zoom verification"],
    "pinterest":     ["pinterest", "pinterest code", "pinterest verification"],
    "twitch":        ["twitch", "twitch code", "twitch verification"],
    "likee":         ["likee", "likee code", "likee verification"],
    "zalo":          ["zalo", "zalo code", "zalo verification"],
    "kik":           ["kik messenger", "kik code"],
    "tumblr":        ["tumblr", "tumblr code"],
    "clubhouse":     ["clubhouse", "clubhouse code"],
    "bigo":          ["bigo", "bigo live", "bigo code"],
    "kwai":          ["kwai", "kwai code"],
    "hike":          ["hike messenger", "hike code"],

    # 🔵 Tech & Mail
    "teams":         ["microsoft teams", "ms teams", "teams code", "teams verification"],
    "gmail":         ["gmail", "google mail", "gmail code", "gmail verification"],
    "googledrive":   ["google drive", "googledrive", "gdrive", "drive.google"],
    "grokai":        ["grok", "grok ai", "xai", "grok code"],
    "github":        ["github", "git hub", "github code", "gh code"],
    "canva":         ["canva", "canva code", "canva verification"],
    "chatgpt":       ["chatgpt", "chat gpt", "openai", "chatgpt code", "openai code"],
    "google":        ["google account", "google voice", "جوجل", "غوغل"],
    "microsoft":     ["microsoft", "outlook", "live.com", "hotmail", "msn"],
    "apple":         ["apple", "icloud", "itunes", "apple id", "apple account"],
    "yahoo":         ["yahoo", "yahoo code", "ymail", "yahoo mail"],
    "protonmail":    ["proton", "protonmail", "proton mail"],
    "dropbox":       ["dropbox", "dropbox code"],
    "slack":         ["slack", "slack code", "slack verification"],
    "notion":        ["notion", "notion code"],
    "adobe":         ["adobe", "adobe id", "adobe code"],
    "cloudflare":    ["cloudflare", "cloudflare code"],
    "shopify":       ["shopify", "shopify code"],
    "netflix":       ["netflix", "netflix code", "netflix verification"],
    "spotify":       ["spotify", "spotify code", "spotify verification"],
    "youtube":       ["youtube", "youtube code", "youtube premium"],
    "disneyplus":    ["disney", "disney+", "disneyplus", "disney plus"],
    "hbo":           ["hbo", "hbo max", "hbo code"],
    "hulu":          ["hulu", "hulu code"],
    "amazonprime":   ["prime video", "amazon prime", "primevideo"],
    "deezer":        ["deezer", "deezer code"],
    "soundcloud":    ["soundcloud", "sound cloud"],

    # 💰 Crypto & Trading
    "binance":       ["binance", "bnb", "binance code", "binance verification"],
    "coinbase":      ["coinbase", "coinbase code"],
    "okx":           ["okx", "okex", "okx code"],
    "kucoin":        ["kucoin", "kucoin code"],
    "bybit":         ["bybit", "bybit code"],
    "huobi":         ["huobi", "htx", "huobi code"],
    "mexc":          ["mexc", "mexc code"],
    "trustwallet":   ["trust wallet", "trustwallet"],
    "kraken":        ["kraken", "kraken code"],
    "gateio":        ["gate.io", "gateio", "gate code"],
    "bitfinex":      ["bitfinex", "bitfinex code"],
    "crypto":        ["crypto.com", "crypto code", "crypto verification"],
    "metamask":      ["metamask", "meta mask", "metamask code"],
    "bitget":        ["bitget", "bitget code"],
    "pionex":        ["pionex", "pionex code"],
    "phemex":        ["phemex", "phemex code"],
    "bitmex":        ["bitmex", "bitmex code"],
    "etoro":         ["etoro", "etoro code"],

    # 💳 Finance & Wallets
    "bkash":         ["bkash", "b-kash", "bkash code", "bkash verification"],
    "nagad":         ["nagad", "nagad code", "nagad verification"],
    "rocket":        ["dutch bangla", "dutch-bangla"],
    "upay":          ["upay", "upay code"],
    "paypal":        ["paypal", "pay pal", "paypal code", "paypal verification"],
    "paytm":         ["paytm", "paytm code"],
    "cashapp":       ["cash app", "cashapp", "cash app code"],
    "wise":          ["wise", "transferwise", "wise transfer"],
    "mastercard":    ["mastercard", "master card", "mastercard code"],
    "tether":        ["tether", "usdt", "tether code"],
    "bolt":          ["bolt food", "bolt ride", "bolt driver", "bolt verification"],
    "gpay":          ["google pay", "gpay", "g pay", "google payment"],
    "applepay":      ["apple pay", "applepay"],
    "stripe":        ["stripe", "stripe code"],
    "skrill":        ["skrill", "skrill code"],
    "neteller":      ["neteller", "neteller code"],
    "revolut":       ["revolut", "revolut code"],
    "monzo":         ["monzo", "monzo code"],
    "chime":         ["chime", "chime code"],
    "zelle":         ["zelle", "zelle code"],
    "venmo":         ["venmo", "venmo code"],
    "payoneer":      ["payoneer", "payoneer code"],
    "momo":          ["mtn momo", "momo code"],
    "mpesa":         ["m-pesa", "mpesa", "safaricom"],
    "dana":          ["dana", "dana code", "dana verification"],
    "ovo":           ["ovo", "ovo code", "ovo verification"],
    "gopay":         ["gopay", "go-pay", "gojek pay"],
    "grab":          ["grabpay", "grab code"],
    "truemoney":     ["truemoney", "true money", "truewallet"],
    "alipay":        ["alipay", "ali pay", "alipay code", "支付宝"],
    "jazzcash":      ["jazzcash", "jazz cash", "jazzcash code"],
    "easypaisa":     ["easypaisa", "easy paisa", "easypaisa code"],
    "sadapay":       ["sadapay", "sada pay"],
    "nayapay":       ["nayapay", "naya pay"],
    "interac":       ["interac", "interac code"],
    "pix":           ["pix code", "pix verification"],

    # 🛒 E-commerce & Delivery
    "amazon":        ["amazon", "amzn", "amazon code", "amazon verification"],
    "ebay":          ["ebay", "ebay code"],
    "aliexpress":    ["aliexpress", "ali express", "aliexpress code"],
    "alibaba":       ["alibaba", "alibaba code"],
    "daraz":         ["daraz", "daraz code", "daraz verification"],
    "foodpanda":     ["foodpanda", "food panda"],
    "uber":          ["uber", "uber code", "uber verification", "uber eats"],
    "pathao":        ["pathao", "pathao ride"],
    "shein":         ["shein", "shein code", "shein verification"],
    "lazada":        ["lazada", "lazada code"],
    "shopee":        ["shopee", "shopee code", "shopee verification"],
    "tokopedia":     ["tokopedia", "tokopedia code"],
    "flipkart":      ["flipkart", "flipkart code"],
    "meesho":        ["meesho", "meesho code"],
    "noon":          ["noon code", "noon verification"],
    "temu":          ["temu", "temu code", "temu verification"],
    "olx":           ["olx", "olx code", "olx verification"],
    "careem":        ["careem", "careem code", "careem verification"],
    "zomato":        ["zomato", "zomato code"],
    "swiggy":        ["swiggy", "swiggy code"],
    "doordash":      ["doordash", "door dash"],
    "lyft":          ["lyft", "lyft code"],
    "instacart":     ["instacart", "instacart code"],
    "gojek":         ["gojek", "go-jek"],
    "rappi":         ["rappi", "rappi code"],

    # 🎮 Gaming
    "steam":         ["steam", "steam guard", "steam code"],
    "epicgames":     ["epic games", "epicgames", "epic code"],
    "roblox":        ["roblox", "roblox code"],
    "riotgames":     ["riot games", "valorant", "league of legends"],
    "garena":        ["garena", "free fire", "freefire"],
    "playstation":   ["playstation", "psn", "ps4", "ps5", "playstation code"],
    "xbox":          ["xbox", "xbox live", "xbox code", "xbox verification"],
    "nintendo":      ["nintendo", "nintendo code", "nintendo switch"],
    "pubg":          ["pubg", "pubg mobile", "battlegrounds"],
    "mobilelegends": ["mobile legends", "mobilelegends", "mlbb"],
    "codm":          ["call of duty", "codm", "cod mobile"],
    "apex":          ["apex legends", "apex code"],

    # 🎲 Betting & Casino
    "1xbet":         ["1xbet", "1x bet", "1xbet code"],
    "melbet":        ["melbet", "melbet code"],
    "linebet":       ["linebet", "linebet code"],
    "bet365":        ["bet365", "bet 365"],
    "megapari":      ["megapari", "megapari code"],
    "betwinner":     ["betwinner", "bet winner"],
    "mostbet":       ["mostbet", "most bet"],
    "pinup":         ["pin-up bet", "pinup bet", "pin up casino"],
    "parimatch":     ["parimatch", "pari match"],
    "betway":        ["betway", "betway code"],
    "draftkings":    ["draftkings", "draft kings"],
    "fanduel":       ["fanduel", "fan duel"],

    # ❤️ Dating
    "tinder":        ["tinder", "tinder code"],
    "bumble":        ["bumble", "bumble code"],
    "badoo":         ["badoo", "badoo code"],
    "hinge":         ["hinge", "hinge code"],
    "okcupid":       ["okcupid", "ok cupid"],
    "grindr":        ["grindr", "grindr code"],

    # 🚗 Ride & Transport
    "indriver":      ["indriver", "indrive", "in driver"],
    "yandex":        ["yandex", "yandex go", "yandex taxi"],
    "ola":           ["ola cab", "ola code"],
}


def _country_code_matches(c, iso, name):
    """Match a stored country code/name (e.g. voltx country key) against a flag
    entry's iso/name. Short codes (like ISO 'SL' for Sierra Leone) must match
    exactly — substring matching on short codes is unsafe because e.g. 'SL' is
    literally contained inside 'ISLANDS' (Cook Islands, Solomon Islands, ...),
    which previously caused the wrong country to be shown."""
    c_up = str(c).upper().strip()
    if not c_up:
        return False
    if c_up == iso or c_up == name:
        return True
    if len(c_up) <= 3:
        return False
    return c_up in name or name in c_up

def _kw_matches(kw, text_lower):
    """Match keyword against lowercase text. Short keywords (≤3 chars) require word boundaries
    to prevent false positives like 'wa' matching 'was', 'want', 'swap' etc."""
    if len(kw) <= 3:
        return bool(re.search(r'(?<![a-z0-9])' + re.escape(kw) + r'(?![a-z0-9])', text_lower))
    return kw in text_lower

def detect_service(text):
    text_lower = str(text).lower()
    for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
        for kw in keywords:
            if _kw_matches(kw, text_lower):
                return service_key.upper()
    return None

def _e(name, char, eid):
    return (name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>')

def _eu(name, char):
    """Unknown/generic service emoji using the default unknown emoji ID."""
    return name, f'<tg-emoji emoji-id="5253742260054409879">{char}</tg-emoji>'

_DEFAULT_SERVICE_EMOJIS = {
    # Social & Chat
    "WHATSAPP":      _e("WhatsApp",        "💬", "5334998226636390258"),
    "FACEBOOK":      _e("Facebook",        "📘", "5323261730283863478"),
    "INSTAGRAM":     _e("Instagram",       "📸", "5319160079465857105"),
    "MESSENGER":     _e("Messenger",       "💬", "5323687726615119535"),
    "META":          _e("Meta",            "🔵", "5321447183910716259"),
    "TELEGRAM":      _e("Telegram",        "✈️", "5330237710655306682"),
    "TIKTOK":        _e("TikTok",          "🎵", "5327982530702359565"),
    "SNAPCHAT":      _e("Snapchat",        "👻", "5330248916224983855"),
    "TWITTER":       _e("Twitter/X",       "🐦", "5330337435500951363"),
    "DISCORD":       _e("Discord",         "🎮", "5325612636467903082"),
    "SIGNAL":        _e("Signal",          "🔵", "5328050550099427291"),
    "THREADS":       _e("Threads",         "🔗", "5334592721594105691"),
    "REDNOTE":       _e("RedNote",         "📕", "5334707727933390944"),
    "VK":            _e("VK",              "💙", "5334853932915114338"),
    "WECHAT":        _e("WeChat",          "🟢", "5332524123610430820"),
    "REDDIT":        _e("Reddit",          "🔴", "5330321861949539755"),
    "VIBER":         _eu("Viber",          "📳"),
    "LINE":          _eu("Line",           "💚"),
    "LINKEDIN":      _eu("LinkedIn",       "💼"),
    "IMO":           _eu("Imo",            "📞"),
    "KAKAOTALK":     _eu("KakaoTalk",      "💛"),
    "SKYPE":         _eu("Skype",          "🔵"),
    "ZOOM":          _eu("Zoom",           "🎦"),
    "PINTEREST":     _eu("Pinterest",      "📌"),
    "TWITCH":        _eu("Twitch",         "🟣"),
    "LIKEE":         _eu("Likee",          "🎬"),
    "ZALO":          _eu("Zalo",           "🔵"),
    "KIK":           _eu("Kik",            "🟢"),
    "TUMBLR":        _eu("Tumblr",         "🔵"),
    "CLUBHOUSE":     _eu("Clubhouse",      "🟢"),
    "BIGO":          _eu("Bigo Live",      "🎥"),
    "KWAI":          _eu("Kwai",           "🎵"),
    "QQ":            _eu("QQ",             "🐧"),
    # Tech & Mail
    "GMAIL":         _e("Gmail",           "📧", "5303416490295304868"),
    "GOOGLEDRIVE":   _e("Google Drive",    "📁", "5303051181851943323"),
    "GROKAI":        _e("Grok AI",         "🤖", "5454065032298009119"),
    "GITHUB":        _e("GitHub",          "🐙", "5303382121967001310"),
    "CANVA":         _e("Canva",           "🎨", "5429229538527690282"),
    "CHATGPT":       _e("ChatGPT",         "🤖", "5359726582447487916"),
    "MICROSOFT":     _e("Microsoft",       "🪟", "5370857634440170316"),
    "APPLE":         _e("Apple",           "🍎", "5334955749409834455"),
    "TEAMS":         _e("Teams",           "🟦", "5453866707888152017"),
    "GOOGLE":        _eu("Google",         "🔍"),
    "YAHOO":         _eu("Yahoo",          "🟣"),
    "PROTONMAIL":    _eu("ProtonMail",     "🟣"),
    "SLACK":         _eu("Slack",          "💬"),
    "NOTION":        _eu("Notion",         "📝"),
    "ADOBE":         _eu("Adobe",          "🔴"),
    "DROPBOX":       _eu("Dropbox",        "🔵"),
    # Entertainment
    "NETFLIX":       _e("Netflix",         "🎬", "5318911503938634641"),
    "SPOTIFY":       _e("Spotify",         "🎧", "5346074681004801565"),
    "YOUTUBE":       _eu("YouTube",        "▶️"),
    "DISNEYPLUS":    _eu("Disney+",        "🏰"),
    "HBO":           _eu("HBO Max",        "🎬"),
    "HULU":          _eu("Hulu",           "🟢"),
    "AMAZONPRIME":   _eu("Prime Video",    "📦"),
    "DEEZER":        _eu("Deezer",         "🎵"),
    "SOUNDCLOUD":    _eu("SoundCloud",     "🔶"),
    # Finance
    "PAYPAL":        _e("PayPal",          "💳", "5364111181415996352"),
    "MASTERCARD":    _e("Mastercard",      "💳", "5364036341610858181"),
    "TETHER":        _e("Tether",          "💵", "5359437015752401733"),
    "PAYTM":         _eu("Paytm",          "💰"),
    "CASHAPP":       _eu("Cash App",       "💵"),
    "WISE":          _eu("Wise",           "💸"),
    "BKASH":         _eu("bKash",          "🩷"),
    "NAGAD":         _eu("Nagad",          "🟠"),
    "ROCKET":        _eu("Rocket",         "🚀"),
    "UPAY":          _eu("Upay",           "💳"),
    "GPAY":          _eu("Google Pay",     "💳"),
    "APPLEPAY":      _eu("Apple Pay",      "💳"),
    "STRIPE":        _eu("Stripe",         "🔵"),
    "SKRILL":        _eu("Skrill",         "🟣"),
    "NETELLER":      _eu("Neteller",       "🔵"),
    "REVOLUT":       _eu("Revolut",        "🔵"),
    "MONZO":         _eu("Monzo",          "🔥"),
    "CHIME":         _eu("Chime",          "🟢"),
    "ZELLE":         _eu("Zelle",          "🔵"),
    "VENMO":         _eu("Venmo",          "🔵"),
    "PAYONEER":      _eu("Payoneer",       "🟠"),
    "MOMO":          _eu("MoMo",           "🟣"),
    "MPESA":         _eu("M-Pesa",         "🟢"),
    "DANA":          _eu("Dana",           "🔵"),
    "OVO":           _eu("OVO",            "🟣"),
    "GOPAY":         _eu("GoPay",          "🟢"),
    "GRAB":          _eu("GrabPay",        "🟢"),
    "TRUEMONEY":     _eu("TrueMoney",      "🔵"),
    "ALIPAY":        _eu("Alipay",         "💙"),
    "JAZZCASH":      _eu("JazzCash",       "🔴"),
    "EASYPAISA":     _eu("EasyPaisa",      "🟢"),
    "SADAPAY":       _eu("SadaPay",        "🟣"),
    "NAYAPAY":       _eu("NayaPay",        "🔵"),
    "INTERAC":       _eu("Interac",        "🔴"),
    "PIX":           _eu("Pix",            "🔵"),
    # Crypto
    "BINANCE":       _e("Binance",         "🪙", "5888561507557447441"),
    "COINBASE":      _eu("Coinbase",       "🔵"),
    "OKX":           _eu("OKX",            "⬛"),
    "BYBIT":         _eu("Bybit",          "🟠"),
    "KUCOIN":        _eu("KuCoin",         "🟢"),
    "HUOBI":         _eu("Huobi",          "🔵"),
    "MEXC":          _eu("MEXC",           "🔵"),
    "TRUSTWALLET":   _eu("Trust Wallet",   "🔵"),
    "KRAKEN":        _eu("Kraken",         "🟣"),
    "GATEIO":        _eu("Gate.io",        "🔵"),
    "BITFINEX":      _eu("Bitfinex",       "🟢"),
    "CRYPTO":        _eu("Crypto.com",     "🔵"),
    "METAMASK":      _eu("MetaMask",       "🦊"),
    "BITGET":        _eu("Bitget",         "🔵"),
    "ETORO":         _eu("eToro",          "🟢"),
    # E-commerce & Delivery
    "UBER":          _e("Uber",            "🚗", "5298715455316303708"),
    "BOLT":          _e("Bolt",            "⚡", "5346188613602263703"),
    "AMAZON":        _eu("Amazon",         "📦"),
    "EBAY":          _eu("eBay",           "🛒"),
    "ALIEXPRESS":    _eu("AliExpress",     "🛍️"),
    "ALIBABA":       _eu("Alibaba",        "🛒"),
    "DARAZ":         _eu("Daraz",          "🛍️"),
    "FOODPANDA":     _eu("foodpanda",      "🐼"),
    "PATHAO":        _eu("Pathao",         "🚗"),
    "SHEIN":         _eu("Shein",          "👗"),
    "LAZADA":        _eu("Lazada",         "🛒"),
    "SHOPEE":        _eu("Shopee",         "🛒"),
    "TOKOPEDIA":     _eu("Tokopedia",      "🟢"),
    "FLIPKART":      _eu("Flipkart",       "🛒"),
    "MEESHO":        _eu("Meesho",         "🛍️"),
    "NOON":          _eu("Noon",           "🛒"),
    "TEMU":          _eu("Temu",           "🛒"),
    "OLX":           _eu("OLX",            "🟢"),
    "CAREEM":        _eu("Careem",         "🚗"),
    "ZOMATO":        _eu("Zomato",         "🔴"),
    "SWIGGY":        _eu("Swiggy",         "🟠"),
    "DOORDASH":      _eu("DoorDash",       "🔴"),
    "LYFT":          _eu("Lyft",           "🩷"),
    "INSTACART":     _eu("Instacart",      "🟢"),
    "GOJEK":         _eu("GoJek",          "🟢"),
    "RAPPI":         _eu("Rappi",          "🟡"),
    # Gaming
    "STEAM":         _e("Steam",           "🎮", "5373144051690258848"),
    "ROBLOX":        _eu("Roblox",         "🎲"),
    "GARENA":        _eu("Garena",         "🔥"),
    "PLAYSTATION":   _eu("PlayStation",    "🎮"),
    "EPICGAMES":     _eu("Epic Games",     "🎮"),
    "RIOTGAMES":     _eu("Riot Games",     "⚔️"),
    "XBOX":          _eu("Xbox",           "🟢"),
    "NINTENDO":      _eu("Nintendo",       "🔴"),
    "PUBG":          _eu("PUBG",           "🎯"),
    "MOBILELEGENDS": _eu("Mobile Legends", "⚔️"),
    "CODM":          _eu("Call of Duty",   "🎮"),
    "APEX":          _eu("Apex Legends",   "🎯"),
    # Betting
    "1XBET":         _eu("1xBet",          "🎲"),
    "MELBET":        _eu("Melbet",         "🎲"),
    "LINEBET":       _eu("LineBet",        "🎲"),
    "BET365":        _eu("Bet365",         "🎲"),
    "MEGAPARI":      _eu("Megapari",       "🎲"),
    "BETWINNER":     _eu("BetWinner",      "🎲"),
    "MOSTBET":       _eu("Mostbet",        "🎲"),
    "PINUP":         _eu("Pin-Up",         "🎲"),
    "PARIMATCH":     _eu("Parimatch",      "🎲"),
    "BETWAY":        _eu("Betway",         "🎲"),
    "DRAFTKINGS":    _eu("DraftKings",     "🏈"),
    "FANDUEL":       _eu("FanDuel",        "🏈"),
    # Dating
    "TINDER":        _eu("Tinder",         "🔥"),
    "BUMBLE":        _eu("Bumble",         "🐝"),
    "BADOO":         _eu("Badoo",          "❤️"),
    "HINGE":         _eu("Hinge",          "❤️"),
    "OKCUPID":       _eu("OkCupid",        "❤️"),
    "GRINDR":        _eu("Grindr",         "🟡"),
    # Transport
    "INDRIVER":      _eu("inDriver",       "🚗"),
    "YANDEX":        _eu("Yandex Go",      "🚖"),
    "OLA":           _eu("Ola",            "🚖"),
}


def get_service_info_html(service_text, msg_text=""):
    s = str(service_text).upper().strip()
    m = str(msg_text).lower().strip()
    apps = bot_settings.get("premium_apps", {})

    # Is service_text purely numeric? (e.g. CLI="372828") → not a service name
    _is_numeric = bool(re.match(r'^\+?[\d\s\-]+$', s.strip())) if s else True

    detected_service = s

    if s and not _is_numeric:
        # Priority 1: CLI/service_text is a real name — try to match against known services
        cli_mapped = None
        s_lower = s.lower()
        for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
            for kw in keywords:
                if _kw_matches(kw, s_lower):
                    cli_mapped = service_key.upper()
                    break
            if cli_mapped:
                break
        if cli_mapped:
            detected_service = cli_mapped
        else:
            # CLI name not found in keywords (e.g. "Panel 1", unknown panel name)
            # → Priority 2: try message body
            if m:
                for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
                    for kw in keywords:
                        if _kw_matches(kw, m):
                            detected_service = service_key.upper()
                            break
                    if detected_service != s:
                        break
    else:
        # CLI is numeric or empty → Priority 2: detect from message body
        if m:
            for service_key, keywords in SERVICE_SMS_KEYWORDS.items():
                for kw in keywords:
                    if _kw_matches(kw, m):
                        detected_service = service_key.upper()
                        break
                if detected_service != s:
                    break

    clean_s = re.sub(r'[^\w\s]', '', detected_service).strip()

    # 1. Check admin-configured premium_apps first
    for app_name, data in apps.items():
        if app_name == detected_service or app_name == clean_s or app_name in detected_service or detected_service in app_name:
            full_name = data.get("name", app_name.title())
            char = data.get("char", "📱")
            eid = data.get("id")
            if eid: return full_name, f'<tg-emoji emoji-id="{eid}">{char}</tg-emoji>'
            return full_name, char

    # 2. Fall back to built-in emoji map for common services
    if clean_s in _DEFAULT_SERVICE_EMOJIS:
        return _DEFAULT_SERVICE_EMOJIS[clean_s]
    for key, val in _DEFAULT_SERVICE_EMOJIS.items():
        if key in clean_s or clean_s in key:
            return val

    if len(detected_service) > 20:
        return "Message", '<tg-emoji emoji-id="5253742260054409879">💬</tg-emoji>'

    return detected_service.title(), '<tg-emoji emoji-id="5253742260054409879">📱</tg-emoji>'

def detect_language(text):
    if not text: return "#EN"
    text_str = str(text)


    if any('\u0600' <= c <= '\u06ff' for c in text_str): return "#AR" # Arabic / Persian / Urdu
    if any('\u0980' <= c <= '\u09ff' for c in text_str): return "#BN" # Bengali
    if any('\u0900' <= c <= '\u097f' for c in text_str): return "#HI" # Hindi / Marathi / Nepali
    if any('\u0a00' <= c <= '\u0a7f' for c in text_str): return "#PA" # Punjabi (Gurmukhi)
    if any('\u0a80' <= c <= '\u0aff' for c in text_str): return "#GU" # Gujarati
    if any('\u0b00' <= c <= '\u0b7f' for c in text_str): return "#OR" # Odia
    if any('\u0b80' <= c <= '\u0bff' for c in text_str): return "#TA" # Tamil
    if any('\u0c00' <= c <= '\u0c7f' for c in text_str): return "#TE" # Telugu
    if any('\u0c80' <= c <= '\u0cff' for c in text_str): return "#KN" # Kannada
    if any('\u0d00' <= c <= '\u0d7f' for c in text_str): return "#ML" # Malayalam
    if any('\u0d80' <= c <= '\u0dff' for c in text_str): return "#SI" # Sinhala
    if any('\u0e00' <= c <= '\u0e7f' for c in text_str): return "#TH" # Thai
    if any('\u0e80' <= c <= '\u0eff' for c in text_str): return "#LO" # Lao
    if any('\u0f00' <= c <= '\u0fff' for c in text_str): return "#BO" # Tibetan
    if any('\u1000' <= c <= '\u109f' for c in text_str): return "#MY" # Burmese (Myanmar)
    if any('\u1200' <= c <= '\u137f' for c in text_str): return "#AM" # Amharic (Ethiopic)
    if any('\u1780' <= c <= '\u17ff' for c in text_str): return "#KM" # Khmer
    if any('\u10a0' <= c <= '\u10ff' for c in text_str): return "#KA" # Georgian
    if any('\u0530' <= c <= '\u058f' for c in text_str): return "#HY" # Armenian
    if any('\u0590' <= c <= '\u05ff' for c in text_str): return "#HE" # Hebrew
    if any('\u0370' <= c <= '\u03ff' for c in text_str): return "#EL" # Greek
    if any('\u0400' <= c <= '\u04ff' for c in text_str): return "#RU" # Russian / Ukrainian (Cyrillic)
    if any('\u4e00' <= c <= '\u9fff' for c in text_str): return "#ZH" # Chinese
    if any('\u3040' <= c <= '\u309f' or '\u30a0' <= c <= '\u30ff' for c in text_str): return "#JA" # Japanese
    if any('\uac00' <= c <= '\ud7af' for c in text_str): return "#KO" # Korean


    text_lower = text_str.lower()
    
    # Asian / Pacific
    if any(w in text_lower for w in ["kode verifikasi", "jangan bagikan", "rahasia"]): return "#ID" # Indonesian
    if any(w in text_lower for w in ["kod pengesahan", "jangan kongsi"]): return "#MS" # Malay
    if any(w in text_lower for w in ["mã của bạn", "không chia sẻ", "mã xác minh"]): return "#VN" # Vietnamese
    if any(w in text_lower for w in ["ang iyong code", "huwag ibahagi"]): return "#TL" # Tagalog / Filipino
    
    # European / Americas
    if any(w in text_lower for w in ["código", "tu código", "verificación", "no compartas"]): return "#ES" # Spanish
    if any(w in text_lower for w in ["seu código", "código de verificação", "não compartilhe"]): return "#PT" # Portuguese
    if any(w in text_lower for w in ["code secret", "ne partagez pas", "votre code"]): return "#FR" # French
    if any(w in text_lower for w in ["dein code", "bestätigungscode", "nicht teilen"]): return "#DE" # German
    if any(w in text_lower for w in ["il tuo codice", "codice di verifica", "non condividere"]): return "#IT" # Italian
    if any(w in text_lower for w in ["twój kod", "nie udostępniaj", "kod weryfikacyjny"]): return "#PL" # Polish
    if any(w in text_lower for w in ["doğrulama kodu", "paylaşmayın", "onay kodu"]): return "#TR" # Turkish
    if any(w in text_lower for w in ["jouw code", "verificatiecode", "niet delen"]): return "#NL" # Dutch
    if any(w in text_lower for w in ["din kod", "verifieringskod", "dela inte"]): return "#SV" # Swedish
    if any(w in text_lower for w in ["bekræftelseskode", "del ikke"]): return "#DA" # Danish
    if any(w in text_lower for w in ["bekreftelseskode", "ikke del"]): return "#NO" # Norwegian
    if any(w in text_lower for w in ["vahvistuskoodi", "älä jaa"]): return "#FI" # Finnish
    if any(w in text_lower for w in ["váš kód", "ověřovací kód", "nesdílejte"]): return "#CS" # Czech
    if any(w in text_lower for w in ["overovací kód", "nezdieľajte"]): return "#SK" # Slovak
    if any(w in text_lower for w in ["ellenőrző kód", "ne oszd meg"]): return "#HU" # Hungarian
    if any(w in text_lower for w in ["codul tău", "codul de verificare", "nu partaja"]): return "#RO" # Romanian
    if any(w in text_lower for w in ["kontrolni kod", "kod za potvrdu", "ne delite"]): return "#HR" # Croatian/Serbian
    if any(w in text_lower for w in ["код за потвърждение", "не споделяйте"]): return "#BG" # Bulgarian
    if any(w in text_lower for w in ["ваш код", "код підтвердження"]): return "#UK" # Ukrainian
    
    # African
    if any(w in text_lower for w in ["msimbo wako", "usishiriki"]): return "#SW" # Swahili
    if any(w in text_lower for w in ["verifikasiekode", "moenie deel nie"]): return "#AF" # Afrikaans
    

    return "#EN"

def parse_chat_id(text):
    text = text.strip()
    if text.startswith("-100") or (text.startswith("-") and text[1:].isdigit()):
        return text
    if "t.me/" in text:
        parts = text.split("/")
        username = parts[-1]
        if username: return "@" + username if not username.startswith("@") else username
    if text.startswith("@"):
        return text
    return "@" + text

def is_admin(user_id):
    return user_id in bot_settings["admins"] or user_id == OWNER_ID

def check_force_join(user_id):
    if not bot_settings["fj_on"] or not bot_settings["fj_channels"]: return True
    if is_admin(user_id): return True
    for ch in bot_settings["fj_channels"]:
        try:
            res = api_call("getChatMember", {"chat_id": ch, "user_id": user_id})
            if res.get("ok"):
                status = res["result"].get("status", "left")
                if status in ["left", "kicked"]:
                    return False
            else:
                err = str(res.get("description", "")).lower()
                if "user not found" in err or "participant" in err or "member" in err or "not a member" in err:
                    return False
        except:
            pass
    return True

def _get_fj_invite_link(ch):
    ch = str(ch)
    if ch.startswith("@"):
        return f"https://t.me/{ch.lstrip('@')}"
    inv = api_call("exportChatInviteLink", {"chat_id": ch})
    if inv.get("ok"):
        return inv["result"]
    chat_info = api_call("getChat", {"chat_id": ch})
    return chat_info.get("result", {}).get("invite_link", "")

def _get_chat_title(ch):
    """Fetch the title/name of a channel or group from Telegram.
    Prefers username (handle) over title — title can be arbitrary short text.
    For private channels/groups with no username, falls back to title."""
    try:
        ch_info = api_call("getChat", {"chat_id": ch})
        result = ch_info.get("result", {})
        username = result.get("username")   # e.g. "AmirXOtp"
        title = result.get("title")         # e.g. "ه"
        if username:
            return username  # prefer handle — always matches what admin added
        if title:
            return title     # private channel/group — no username, use title
    except:
        pass
    # Safe fallback: strip @ for usernames, keep numeric IDs as-is
    ch_str = str(ch)
    if ch_str.startswith("@"):
        return ch_str[1:]
    return ch_str

def send_force_join_msg(chat_id):
    kb = []
    for ch in bot_settings["fj_channels"]:
        url = _get_fj_invite_link(ch)
        if url and str(url).startswith("http"):
            ch_name = _get_chat_title(ch)
            btn_label = ch_name if ch_name else "Join Channel"
            kb.append([{"text": btn_label, "icon_custom_emoji_id": "5789428375261023681", "url": url, "style": "primary"}])
    kb.append([{"text": "I Joined — Check Now", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "check_fj", "style": "success"}])
    send_message(chat_id, render_body_text(f"{PEM['warn']} <b>Join our channel(s) first to use the bot!</b>\n\n{PEM['link']} Click the button below, join, then press <b>I Joined</b>."), reply_markup={"inline_keyboard": kb})

def is_user_banned(user_id):
    if is_admin(user_id): return False
    if user_id in user_banned_cache and time.time() - user_banned_cache[user_id]['time'] < 60:
        return user_banned_cache[user_id]['banned']
    with db_lock:
        conn = get_db_conn()
        row = conn.execute("SELECT banned FROM users WHERE user_id=?", (user_id,)).fetchone()
        conn.close()
    banned = bool(row[0]) if row else False
    user_banned_cache[user_id] = {'banned': banned, 'time': time.time()}
    return banned


# ==========================================
# Captcha Auto Login & Parsing Core
# ==========================================
def extract_otp_code(text):
    clean_text = re.sub(r'[\u200B-\u200D\uFEFF]', '', str(text))

    # 1. Multi-part OTPs (e.g. 123-456 or 809-761)
    multi_part = re.search(r'(\d{3}[-\s]+\d{3})|(\d{2}[-\s]+\d{2}[-\s]+\d{2})', clean_text)
    if multi_part:

        return multi_part.group(0).replace(" ", "")

    # 2. Keyword-based extraction
    otp_keywords = ['code', 'is', 'otp', 'pin', 'verification', 'auth', 'رمز', 'your code']
    keywords_pattern = '|'.join(otp_keywords)
    keyword_match = re.search(rf'(?:{keywords_pattern})\s*(?:is|:|-|=)?\s*([a-z0-9]{{4,10}})', clean_text, re.I)
    if keyword_match and keyword_match.group(1).isdigit():
        return keyword_match.group(1)
        
    keyword_match_rev = re.search(rf'([a-z0-9]{{4,10}})\s*(?:is your|is the|)', clean_text, re.I)
    if keyword_match_rev and keyword_match_rev.group(1).isdigit():
        return keyword_match_rev.group(1)

    # 3. Google OTP
    g_match = re.search(r'G-(\d{6})', clean_text, re.IGNORECASE)
    if g_match: return g_match.group(1)

    # 4. Digit sequences fallback
    digit_matches = re.findall(r'(?<!\d)\d{4,8}(?!\d)', clean_text)
    if digit_matches: return digit_matches[0]

    return None

def parse_panel_response(response_text, p_config=None):
    results = []
    p_type = p_config.get("type", "API Panel") if p_config else "API Panel"
    
    n_col_name = p_config.get("num_col_name", "number").lower() if p_config else "number"
    m_col_name = p_config.get("msg_col_name", "message").lower() if p_config else "message"
    n_idx = int(p_config.get("num_col_idx", 1)) - 1 if p_config and p_config.get("num_col_idx") else 1
    m_idx = int(p_config.get("msg_col_idx", 2)) - 1 if p_config and p_config.get("msg_col_idx") else 2

    _CLI_HDR_WORDS = ["cli", "client", "service", "app", "provider", "application", "sender", "source"]

    if p_type == "Auto Captcha Panel":
        try:
            soup = BeautifulSoup(response_text, 'html.parser')
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                if not rows: continue

                final_n_idx = n_idx
                final_m_idx = m_idx
                final_c_idx = -1  # CLI column index; -1 = not found

                header_cells = rows[0].find_all(['th', 'td'])
                for i, cell in enumerate(header_cells):
                    c_text = cell.get_text(strip=True).lower()
                    if n_col_name in c_text or "number" in c_text or "phone" in c_text or "msisdn" in c_text:
                        final_n_idx = i
                    if m_col_name in c_text or "message" in c_text or "sms" in c_text or "text" in c_text:
                        final_m_idx = i
                    if any(w in c_text for w in _CLI_HDR_WORDS):
                        final_c_idx = i

                for row in rows:
                    cols = row.find_all(['td', 'th'])

                    if all(c.name == 'th' for c in cols): continue
                    
                    if len(cols) > max(final_n_idx, final_m_idx):

                        num_text = cols[final_n_idx].get_text(separator=" ", strip=True)
                        msg_text = cols[final_m_idx].get_text(separator=" ", strip=True)
                        clean_num = re.sub(r'\D', '', num_text)

                        # Extract CLI from dedicated column if detected
                        cli_val = ""
                        if final_c_idx >= 0 and final_c_idx < len(cols):
                            raw_cli = cols[final_c_idx].get_text(strip=True)
                            if raw_cli and not re.match(r'^\+?[\d\s\-]+$', raw_cli):
                                cli_val = raw_cli

                        # If no CLI column, detect service from message body
                        if not cli_val:
                            cli_val = detect_service(msg_text) or ""

                        if clean_num and 5 <= len(clean_num) <= 18:
                            otp = extract_otp_code(msg_text)
                            if otp and len(msg_text) > 4:
                                results.append({"number": clean_num, "message": msg_text, "otp": otp, "cli": cli_val})
        except Exception as e:
            pass
    else:
        try:
            data = json.loads(response_text)
            temp_results = []
            
            def process_item(item):
                pot_nums_list = []
                pot_msg = None
                values = []
                
                if isinstance(item, dict):

                    lower_keys = {str(k).lower(): v for k, v in item.items()}
                    for k in ["number", "num", "phone", "msisdn", "sender"]:
                        if k in lower_keys:
                            clean_val = re.sub(r'\D', '', str(lower_keys[k]))
                            if 5 <= len(clean_val) <= 18:
                                if clean_val not in pot_nums_list: pot_nums_list.append(clean_val)
                    for k in ["message", "msg", "sms", "content", "text"]:
                        if k in lower_keys:
                            val = str(lower_keys[k])
                            if len(val) > 4:
                                pot_msg = val
                                break
                    cli_hint = None
                    for k in ["cli", "client", "service", "app", "provider", "application"]:
                        if k in lower_keys and str(lower_keys[k]).strip():
                            cli_hint = str(lower_keys[k]).strip()
                            break
                    values = list(item.values())
                elif isinstance(item, list):
                    values = item


                for v in values:
                    if isinstance(v, (dict, list)) or v is None: continue
                    v_str = str(v).strip()
                    

                    clean_v = re.sub(r'\D', '', v_str)
                    if 7 <= len(clean_v) <= 18 and not re.search(r'[a-zA-Z]', v_str):

                        if not re.search(r'\d{4}[-/]\d{2}[-/]\d{2}', v_str) and not re.search(r'\d{2}:\d{2}:\d{2}', v_str) and "." not in v_str:
                            if clean_v not in pot_nums_list:
                                pot_nums_list.append(clean_v)
                    

                    if len(v_str) > 4 and not v_str.isdigit():
                        if extract_otp_code(v_str):
                            if pot_msg is None or len(v_str) > len(pot_msg):
                                pot_msg = v_str
                                

                pot_num = None
                if pot_nums_list:
                    matched_user_num = None
                    for n in pot_nums_list:
                            matched_user_num = n
                            break
                    
                    if matched_user_num:
                        pot_num = matched_user_num
                    elif len(pot_nums_list) >= 2:
                        pot_num = pot_nums_list[1]
                    else:
                        pot_num = pot_nums_list[0]
                            
                if pot_num and pot_msg:
                    otp = extract_otp_code(pot_msg)
                    if otp:
                        # If no cli in JSON keys, detect from message body
                        final_cli = cli_hint if isinstance(item, dict) and cli_hint else None
                        if not final_cli:
                            final_cli = detect_service(pot_msg) or ""
                        temp_results.append({"number": pot_num, "message": pot_msg, "otp": otp, "cli": final_cli})
                        
            def traverse_json(node):
                if isinstance(node, list):
                    if len(node) > 0 and not isinstance(node[0], (dict, list)):
                        # It's a flat list representing one record
                        process_item(node)
                    for child in node:
                        if isinstance(child, (dict, list)):
                            traverse_json(child)
                elif isinstance(node, dict):
                    process_item(node)
                    for val in node.values():
                        if isinstance(val, (dict, list)):
                            traverse_json(val)

            traverse_json(data)
            
            # Remove duplicates
            seen = set()
            for r in temp_results:
                uid = f"{r['number']}_{r['otp']}"
                if uid not in seen:
                    seen.add(uid)
                    results.append(r)
        except: pass
        
    return results

# 🌟 Advanced Automated Background Captcha Solver 🌟
def attempt_auto_login(p, idx):
    login_url = p.get("login_url", "").strip()
    if not login_url.startswith("http"):
        login_url = "http://" + login_url
        
    if not login_url.lower().endswith('/login') and not login_url.lower().endswith('.php'):
        login_url = f"{login_url.rstrip('/')}/login"
        
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    try:
        res = session.get(login_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        all_text = res.text
        
        # 1. SOLVE CAPTCHA (Exact bot 3.py logic)
        captcha_match = re.search(r'(\d+\s*[\+\-\*]\s*\d+)\s*[=\?:]', all_text)
        if not captcha_match:
            captcha_match = re.search(r'what is\s*(\d+\s*[\+\-\*]\s*\d+)', all_text, re.I)
        if not captcha_match:
            elements = soup.find_all(["label", "div", "span", "p", "strong"])
            for el in elements:
                txt = el.get_text(separator=" ", strip=True)
                if any(op in txt for op in ["+", "-", "*"]):
                    m = re.search(r'(\d+\s*[\+\-\*]\s*\d+)', txt)
                    if m:
                        captcha_match = m
                        break
                        
        captcha_text = captcha_match.group(1) if captcha_match else "0 + 0"
        answer = "0"
        m2 = re.search(r'(\d+)\s*([\+\-\*])\s*(\d+)', captcha_text)
        if m2:
            a, op, b = int(m2.group(1)), m2.group(2), int(m2.group(3))
            if op == '+': answer = str(a + b)
            elif op == '-': answer = str(a - b)
            elif op == '*': answer = str(a * b)

        # 2. FIND FORM
        form = soup.find("form")
        if not form:
            p["login_status"] = "❌ No login form found"
            return False
            
        action = form.get("action")
        from urllib.parse import urljoin
        post_url = urljoin(login_url, action) if action else login_url

        form_data = {}
        for hidden in form.find_all("input", type="hidden"):
            name = hidden.get("name")
            if name: form_data[name] = hidden.get("value") or ""
        
        user_input = form.find("input", {"name": re.compile(r"user|email|id", re.I)}) or \
                     form.find("input", {"type": "text", "placeholder": re.compile(r"user|email", re.I)}) or \
                     form.find("input", {"type": "text"})
                     
        pass_input = form.find("input", {"name": re.compile(r"pass", re.I)}) or \
                     form.find("input", {"type": "password"})
                     
        captcha_input = form.find("input", {"placeholder": re.compile(r"answer|ans|code|verification|value|captcha", re.I)}) or \
                        form.find("input", {"name": re.compile(r"ans|captcha|ver|code", re.I)})
        
        user_field = user_input.get("name") if user_input else "username"
        pass_field = pass_input.get("name") if pass_input else "password"
        captcha_field = captcha_input.get("name") if captcha_input else "answer"

        form_data[user_field] = p.get("username", "")
        form_data[pass_field] = p.get("password", "")
        if captcha_field:
            form_data[captcha_field] = answer

        # 3. SUBMIT
        login_req = session.post(post_url, data=form_data, allow_redirects=True, timeout=15)
        
        # 4. VERIFY (Exact bot 3.py check logic)
        msg_link = p.get("msg_link", "").strip()
        if not msg_link.startswith("http") and msg_link != "":
            msg_link = "http://" + msg_link
            
        check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
        
        check_res = session.get(check_url, timeout=10)
        
        if 'logout' in login_req.text.lower() or 'logout' in check_res.text.lower() or 'sms reports' in check_res.text.lower() or 'dashboard' in check_res.text.lower() or 'cdrs' in check_res.text.lower():
            panel_sessions[idx] = session
            p["login_status"] = "✅ Active & Fetching"
            return True
        else:

            p["login_status"] = f"❌ Login Failed (Math: {captcha_text} = {answer})"
            return False
            
    except Exception as e:
        p["login_status"] = f"❌ Error: {str(e)[:20]}"
        
    return False

def panel_monitor_thread():
    global processed_otps, recent_traffic, panel_sessions
    while True:
        try:
            for idx, p in enumerate(bot_settings.get("panels", [])):
                if p.get("status") == "ON":
                    
                    if p.get("type") == "Auto Captcha Panel":
                        sess = panel_sessions.get(idx)
                        
                        if not sess:
                            now = time.time()
                            if now - p.get("last_login_attempt", 0) < 30: 
                                continue 
                            p["last_login_attempt"] = now
                            
                            success = attempt_auto_login(p, idx)
                            save_db() # Save login status text to show in settings
                            if not success:
                                continue 
                            sess = panel_sessions.get(idx)
                            
                        try:
                            # 🌟 auto sessions with sAjaxSource and Fallback HTML Parser
                            parsed_data, res_text = fetch_cpt_panel_cdrs(p, sess, p["msg_link"])
                            p["login_status"] = "✅ Active & Fetching"
                        except Exception as e:
                            p["login_status"] = "❌ Session Expired (Retrying...)"
                            del panel_sessions[idx]
                            save_db()
                            continue

                    elif p.get("api_url") or p.get("full_api_url"): 
                        full_url = p.get("full_api_url", "").strip()
                        url = p.get("api_url", "").strip()
                        token = p.get("token", "").strip()
                        if not full_url and not url: continue
                        
                        urls_to_try = []
                        if full_url:
                            urls_to_try.append(full_url)
                        else:
                            if "{token}" in url or "{key}" in url:
                                urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                            elif "token=" in url or "key=" in url:
                                urls_to_try.append(url)
                            else:
                                sep = '&' if '?' in url else '?'
                                urls_to_try.append(f"{url}{sep}token={token}")
                                urls_to_try.append(f"{url}{sep}key={token}&start=0")
                                urls_to_try.append(f"{url}{sep}key={token}")
                            
                        parsed_data = []
                        # 🌟 Browser Bypass (403 Forbidden Fix)
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                        for try_url in urls_to_try:
                            try:
                                res = requests.get(try_url, headers=headers, timeout=10)
                                parsed_data = parse_panel_response(res.text, p)
                                if parsed_data:
                                    if not full_url and try_url != url and token:
                                        p["api_url"] = try_url.replace(token, "{token}")
                                        save_db()
                                    break
                            except: continue
                        if not parsed_data: continue
                    else:
                        continue
                    
                    if p.get("type") != "Auto Captcha Panel":
                        limit = p.get("records", 0)
                        if limit > 0: parsed_data = parsed_data[:limit]
                        
                    for item in parsed_data:
                        num = item["number"]
                        otp = item["otp"]
                        msg_text = item["message"]
                        unique_id = f"{num}_{otp}"
                        
                        if unique_id not in processed_otps:
                            processed_otps.add(unique_id)
                            if len(processed_otps) > 5000: processed_otps.clear()
                                 
                            char, iso = get_flag_and_code(num)
                            _cli = item.get("cli") or ""
                            # API method: cli field from JSON is authoritative (e.g. "Paypal", "Facebook")
                            # If cli is numeric/empty, fall back to message body detection, then panel name
                            _cli_clean = _cli.strip()
                            _cli_numeric = bool(re.match(r'^\+?[\d\s\-]+$', _cli_clean)) if _cli_clean else True
                            if _cli_clean and not _cli_numeric:
                                _svc_hint = _cli_clean  # Direct: "Paypal" → PayPal
                            else:
                                _detected = detect_service(msg_text)
                                _svc_hint = _detected if _detected else p.get("name", "Panel")
                            app_full_name, prem_app_html = get_service_info_html(_svc_hint, msg_text)
                            current_time = time.time()
                            
                            recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                            recent_traffic.append({
                                "service": app_full_name,
                                "iso": iso,
                                "flag": char,
                                "number": num,
                                "time": current_time
                            })

                            save_local_db()
                                 
                            display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                            masked = mask_number(display_num)
                            lang = detect_language(msg_text)
                            
                            display_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} <b>{iso}</b> <b>{masked}</b> {lang}\n╚═══════════════╝")
                            
                            for fw in bot_settings["fw_groups"]:
                                kb = build_otp_fw_kb(otp, fw)
                                send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                            
                            owners = []
                            owner_assigned_service = {}
                            clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()

                            # OTP actually received for this number now — remove it from stock.
                            # (Numbers that are merely assigned/shared but never receive an OTP
                            # stay in stock, per the fixed behavior.)
                            remove_number_after_otp(clean_api_num)

                            for uid, session_data in user_active_sessions.items():
                                for act_num in session_data.get("nums", []):
                                    act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                    if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                        owners.append(uid)
                                        owner_assigned_service[uid] = session_data.get("service")
                                        break
                                        

                            owners = list(set(owners)) 
                            for owner_id in owners:
                                # Use the service the number was actually stocked/assigned under
                                # (set by admin) instead of re-detecting from the SMS text, so the
                                # owner's inbox always matches what they saw in "Get Number" and the
                                # admin's configured per-service rate.
                                assigned_service = owner_assigned_service.get(owner_id)
                                if assigned_service:
                                    owner_app_full_name, owner_prem_app_html = get_service_info_html(assigned_service)
                                else:
                                    owner_app_full_name, owner_prem_app_html = app_full_name, prem_app_html

                                inbox_msg = render_body_text(f"╔═══════════════╗\n║ {owner_prem_app_html} {get_flag_info_html(display_num)} <b>{iso}</b> {lang}\n╚═══════════════╝\n<b>{display_num}</b>")
                                inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                

                                reward = get_service_otp_reward(owner_app_full_name)
                                if reward > 0:
                                    update_balance(owner_id, reward)
                                    inbox_kb.append([{"text": f"Added {reward} USDT", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                
                                
                                send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                try:
                                    with db_lock:
                                        conn = get_db_conn()
                                        conn.execute("UPDATE users SET total_otps=total_otps+1 WHERE user_id=?", (owner_id,))
                                        conn.commit()
                                        conn.close()
                                    if owner_id in user_cache: user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps",0)+1
                                    _today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
                                    if daily_otps.get(owner_id, {}).get("date") != _today: daily_otps[owner_id] = {"date": _today, "count": 0}
                                    daily_otps[owner_id]["count"] = daily_otps[owner_id].get("count", 0) + 1
                                except: pass
        except Exception as e:
            pass
        time.sleep(5) 

# ==========================================
# User Data (SQLite)
# ==========================================
user_cache = {}

def get_user(user_id):
    if user_id in user_cache: return user_cache[user_id]
    with db_lock:
        conn = get_db_conn()
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if row:
            data = dict(row)
        else:
            conn.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
            conn.commit()
            data = {"user_id": user_id, "balance": 0.0, "total_refers": 0, "total_otps": 0,
                    "banned": 0, "verified": 0, "referred_by": None, "ref_paid": 0}
        conn.close()
    data["banned"] = bool(data.get("banned", 0))
    data["verified"] = bool(data.get("verified", 0))
    user_cache[user_id] = data
    return data

def get_service_otp_reward(app_full_name):
    prices = bot_settings.get("service_otp_prices", {})
    key = (app_full_name or "").upper()
    if key in prices:
        return float(prices[key])
    return float(bot_settings.get("otp_reward", 0.0))

def update_balance(user_id, amount):
    if user_id in user_cache:
        user_cache[user_id]["balance"] = user_cache[user_id].get("balance", 0.0) + float(amount)
    with db_lock:
        conn = get_db_conn()
        conn.execute(
            "INSERT INTO users (user_id, balance) VALUES (?,?) ON CONFLICT(user_id) DO UPDATE SET balance=balance+?",
            (user_id, float(amount), float(amount))
        )
        conn.commit()
        conn.close()

def add_referral(inviter_id, new_user_id):
    existing = get_user(new_user_id)
    if existing.get("ref_paid"): return
    reward = bot_settings.get("refer_reward", 0.2)
    update_balance(inviter_id, reward)
    with db_lock:
        conn = get_db_conn()
        conn.execute("UPDATE users SET total_refers=total_refers+1 WHERE user_id=?", (inviter_id,))
        conn.commit()
        conn.close()
    if inviter_id in user_cache:
        user_cache[inviter_id]["total_refers"] = user_cache[inviter_id].get("total_refers", 0) + 1
    ref_msg = (
        f"{PEM['gift']} <b>New Referral !</b>\n"
        f"------------------\n"
        f"🔥 <b>You Received {reward} USDT</b>\n"
        f"------------------\n"
        f"{PEM['user']} <b>From User ID:</b> <code>{new_user_id}</code>"
    )
    send_message(inviter_id, render_body_text(ref_msg))


# ==========================================
# UI Keyboards & Menu Builders
# ==========================================
def get_cancel_kb():
    return {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]]}

def main_menu(user_id):
    kb = [
        [
            {"text": "GET NUMBER", "icon_custom_emoji_id": "5895343514320899727", "style": "primary"},
            {"text": "TRAFFIC", "icon_custom_emoji_id": "5429278861932124623", "style": "success"}
        ],
        [
            {"text": "2FA ONLINE", "icon_custom_emoji_id": "5267421176841398765", "style": "primary"},
            {"text": "SUPPORT", "icon_custom_emoji_id": "5307746710682869587", "style": "primary"}
        ],
    ]
    if bot_settings.get("refer_on", True):
        kb.append([
            {"text": "Refer", "icon_custom_emoji_id": "5420396762189831222", "style": "success"},
            {"text": "PROFILE", "icon_custom_emoji_id": "5352861489541714456", "style": "primary"}
        ])
    else:
        kb.append([
            {"text": "PROFILE", "icon_custom_emoji_id": "5352861489541714456", "style": "primary"}
        ])
    if is_admin(user_id):
        kb.append([{"text": "Admin Panel", "icon_custom_emoji_id": "5420155432272438703", "style": "danger"}])
    return {"keyboard": kb, "resize_keyboard": True}

def get_admin_text():
    users_count = len(all_known_users) # 🌟 Zero Cost User Count!
    total_files = len(number_batches)
    # Live counts (not stale lifetime counters) so numbers/available drop to 0
    # once their batches are actually deleted from stock.
    numbers_in_stock = sum(len(b["numbers"]) for b in number_batches.values())
    available_nums = sum(
        1 for b in number_batches.values()
        for n in b.get("numbers", []) if not n.get("exhausted")
    )

    txt = f"""
{PEM['admin']} <b>ADMIN CONTROL PANEL</b> {PEM['admin']}
━━━━━━━━━━━━━━━━━━

{PEM['graph']} <b>DATABASE OVERVIEW</b>
— — — — — — — — — —
{PEM['user']} Users      » {users_count}
{PEM['file']} Files      » {total_files}
{PEM['num']} Numbers    » {numbers_in_stock}
{PEM['ok']} Assigned   » {total_assigned_stats}
{PEM['rocket']} Available  » {available_nums}

{PEM['graph']} <b>STOCK LEVEL</b>
— — — — — — — — — —
[██████░░░░░░░░░] {available_nums} free
"""
    return render_body_text(txt)

def admin_panel_keyboard():
    return {"inline_keyboard": [
        [{"text": "LEADER BOARD SYSTEM", "icon_custom_emoji_id": "5353032893096567467", "callback_data": "lb_main", "style": "success"}],
        [{"text": "Upload Number", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_num", "style": "primary"},
         {"text": "Delete files", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "delete_files", "style": "danger"}],
        [{"text": "Stock", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "view_stock", "style": "primary"},
         {"text": "Update Number", "icon_custom_emoji_id": "5395444784611480792", "callback_data": "update_num", "style": "success"}],
        [{"text": "Broadcast", "icon_custom_emoji_id": "5789428375261023681", "callback_data": "broadcast_msg", "style": "success"},
         {"text": "System", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "system_settings", "style": "primary"}],
        [{"text": "Used number", "icon_custom_emoji_id": "5352694861990501856", "callback_data": "show_used", "style": "success"},
         {"text": "Unused number", "icon_custom_emoji_id": "5352597830089347330", "callback_data": "show_unused", "style": "success"}],
        [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]
    ]}

def system_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Voltx Control", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_control", "style": "primary"},
         {"text": "Panel MANAGEMENT", "icon_custom_emoji_id": "5336879280578138635", "callback_data": "manage_panels", "style": "danger"}],
        [{"text": "Force Join System", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "manage_fj", "style": "primary"},
         {"text": "Admin Management", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "manage_admins", "style": "danger"}],
        [{"text": "OTP Group", "icon_custom_emoji_id": "5190447043545438788", "callback_data": "manage_otp_groups", "style": "danger"},
         {"text": "User Management", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "user_management", "style": "primary"}],
        [{"text": "Subscription", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "dummy_alert", "style": "success"},
         {"text": "DEV Control", "icon_custom_emoji_id": "5193100774988617665", "callback_data": "dxa_control", "style": "primary"}],
        [{"text": "Premium Emoji", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "manage_emojis", "style": "success"},
         {"text": "Database", "icon_custom_emoji_id": "5800835941543186089", "callback_data": "database_management", "style": "primary"}],
        [{"text": "Test", "icon_custom_emoji_id": "5190781475468915802", "callback_data": "test_message_flow", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275166", "callback_data": "back_to_admin", "style": "danger"}]
    ]}

def get_user_management_text():
    # 🌟 Fast & Free User Management Stats!
    total = len(all_known_users)
    
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    txt = f"""➖➖➖➖➖➖➖➖
《 👋 USER VIEW 》
➖➖➖➖➖➖➖➖
📊 LIVE STATISTICS:
➖➖➖➖➖➖➖➖
🫂 TOTAL USERS: {total}
✅ VERIFIED USERS: (Hidden to save DB Cost)
🚫 BANNED USERS: (Hidden to save DB Cost)
➖➖➖➖➖➖➖➖
⌛ UPDATED: {now_str}"""
    return render_body_text(txt)

def user_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Manage Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "um_manage_balance", "style": "primary"},
         {"text": "Ban/Unban User", "icon_custom_emoji_id": "5334807341109908955", "callback_data": "um_ban_unban", "style": "danger"}],
        [{"text": "User Profile", "icon_custom_emoji_id": "5352861489541714456", "callback_data": "um_user_profile", "style": "success"},
         {"text": "User List", "icon_custom_emoji_id": "5193063022226086560", "callback_data": "um_user_list_0", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def database_management_keyboard():
    return {"inline_keyboard": [
        [{"text": "Download Database", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_database", "style": "success"}],
        [{"text": "Upload Database", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "upload_database", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def emoji_settings_keyboard():
    return {"inline_keyboard": [
        [{"text": "Upload Flags (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_flags_txt", "style": "primary"},
         {"text": "Download Flags", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_flags_txt", "style": "success"}],
        [{"text": "Upload Services (TXT)", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "up_apps_txt", "style": "primary"},
         {"text": "Download Services", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_apps_txt", "style": "success"}],
        [{"text": "Delete All Flags", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "del_all_flags", "style": "danger"},
         {"text": "Add Single Emoji", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_single_emoji", "style": "success"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def fj_settings_keyboard():
    status_text = 'ON' if bot_settings['fj_on'] else 'OFF'
    status_icon = "5352694861990501856" if bot_settings['fj_on'] else "5318840353510408444"
    kb = [[{"text": f"STATUS: {status_text}", "icon_custom_emoji_id": status_icon, "callback_data": "toggle_fj", "style": "primary"}]]
    for idx, ch in enumerate(bot_settings["fj_channels"]):
        kb.append([{"text": f"Delete: {ch}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fj_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Channel", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fj", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def admin_settings_keyboard():
    kb = []
    for idx, adm in enumerate(bot_settings["admins"]):
        text_btn = f"Owner: {adm}" if adm == OWNER_ID else f"Delete: {adm}"
        icon_id = "5353032893096567467" if adm == OWNER_ID else "5420130255174145507"
        cb_data = "ignore" if adm == OWNER_ID else f"del_adm_{idx}"
        kb.append([{"text": text_btn, "icon_custom_emoji_id": icon_id, "callback_data": cb_data, "style": "danger" if adm != OWNER_ID else "primary"}])
    kb.append([{"text": "Add Admin", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_adm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}])
    return {"inline_keyboard": kb}

def otp_groups_list_keyboard():
    ch_set = "✅" if bot_settings.get("fw_channel_link") else "❌"
    kb = [
        [{"text": "Edit OTP Group Link", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "edit_otp_link", "style": "primary"}],
        [{"text": f"Edit Channel Link {ch_set}", "icon_custom_emoji_id": "5429405838345265327", "callback_data": "edit_fw_channel_link", "style": "primary"}],
    ]
    for idx, fg in enumerate(bot_settings["fw_groups"]):
        group_label = fg.get("name") or fg["chat_id"]
        kb.append([{"text": f"Group: {group_label}", "icon_custom_emoji_id": "5193063022226086560", "callback_data": f"manage_fw_{idx}", "style": "primary"}])
    kb.append([{"text": "Add Forward Group", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_fw", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}])
    return {"inline_keyboard": kb}

def build_otp_fw_kb(otp: str, fw: dict) -> list:
    """Build the inline keyboard for an OTP forward group message.
    Row 1: OTP copy button (green)
    Row N: any custom buttons configured for this group
    Last row: [Number BOT | Channel] side-by-side (auto from BOT_USERNAME + otp_link)
    """
    kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
    for btn in fw.get("buttons", []):
        b_obj = {"text": btn["text"], "url": btn["url"], "style": "primary"}
        if "icon_custom_emoji_id" in btn:
            b_obj["icon_custom_emoji_id"] = btn["icon_custom_emoji_id"]
        kb.append([b_obj])
    # Bottom row: Channel (left) + Get Number/BOT (right) — side by side
    bottom_row = []
    fw_channel = bot_settings.get("fw_channel_link", "")
    if fw_channel and fw_channel.strip():
        bottom_row.append({"text": "𝗖𝗵𝗮𝗻𝗻𝗲𝗹", "url": fw_channel.strip(), "style": "primary", "icon_custom_emoji_id": "5839406384243807787"})
    if BOT_USERNAME:
        bottom_row.append({"text": "𝗕𝗢𝗧", "url": f"https://t.me/{BOT_USERNAME}", "style": "primary", "icon_custom_emoji_id": "5352597830089347330"})
    if bottom_row:
        kb.append(bottom_row)
    return kb

def voltx_control_keyboard():
    return {"inline_keyboard": [
        [{"text": "Add Voltx Key", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_key", "style": "success"},
         {"text": "View/Del Keys", "icon_custom_emoji_id": "5422557736330106570", "callback_data": "view_voltx_keys", "style": "danger"}],
        [{"text": "Manage Voltx Services", "icon_custom_emoji_id": "5192739271886282680", "callback_data": "manage_voltx_srv", "style": "success"}],
        [{"text": "Search Country", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "voltx_search_country", "style": "primary"}],
        [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "primary"}]
    ]}

def specific_fw_group_keyboard(idx):
    group = bot_settings["fw_groups"][idx]
    kb = []
    for b_idx, btn in enumerate(group.get("buttons", [])):
        kb.append([{"text": f"Del: {btn['text']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_fwbtn_{idx}_{b_idx}", "style": "danger"}])
    
    kb.append([{"text": "Add Inline Button", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"add_fwbtn_{idx}", "style": "success"}])
    kb.append([{"text": "Delete Entire Group", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"del_fw_{idx}", "style": "danger"}])
    kb.append([{"text": "Back to Groups", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "primary"}])
    return {"inline_keyboard": kb}

def dxa_control_keyboard():
    w_status = "ON" if bot_settings["withdraw_on"] else "OFF"
    sup_status = "ON" if bot_settings.get("support_link") else "OFF"
    grp_status = "ON" if bot_settings.get("w_group") else "OFF"
    try:
        with db_lock:
            conn = get_db_conn()
            pending_count = conn.execute("SELECT COUNT(*) FROM withdrawals WHERE status='pending'").fetchone()[0]
            conn.close()
    except:
        pending_count = 0
    req_label = f"📋 W. REQUESTS ({pending_count})" if pending_count else "📋 W. REQUESTS"
    refer_status = "ON" if bot_settings.get("refer_on", True) else "OFF"
    return {"inline_keyboard": [
        [{"text": f"WITHDRAW: {w_status}", "icon_custom_emoji_id": "5888561507557447441", "callback_data": "dxa_toggle_w", "style": "primary"},
         {"text": f"REFER & EARN: {refer_status}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "dxa_toggle_refer", "style": "success" if bot_settings.get("refer_on", True) else "danger"}],
        [{"text": f"MIN WITHDRAW: {bot_settings['min_withdraw']}", "icon_custom_emoji_id": "5352877703043258544", "callback_data": "dxa_min_w", "style": "success"},
         {"text": f"OTP REWARD: {bot_settings['otp_reward']}", "icon_custom_emoji_id": "5190576863226933563", "callback_data": "dxa_otp_r", "style": "primary"}],
        [{"text": f"REFER REWARD: {bot_settings['refer_reward']}", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "dxa_ref_r", "style": "success"},
         {"text": f"COOLDOWN: {bot_settings['cooldown']}s", "icon_custom_emoji_id": "5337172996211648018", "callback_data": "dxa_cool", "style": "primary"}],
        [{"text": f"NUM/REQ: {bot_settings['num_req']}", "icon_custom_emoji_id": "5337132498965010628", "callback_data": "dxa_num_req", "style": "success"},
         {"text": f"NUM/SHARE: {bot_settings['num_share']}", "icon_custom_emoji_id": "5352862640592949843", "callback_data": "dxa_num_share", "style": "primary"}],
        [{"text": f"SUPPORT LINK: {sup_status}", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "dxa_sup_link", "style": "success"},
         {"text": "W. METHODS", "icon_custom_emoji_id": "5190899075968441286", "callback_data": "manage_w_methods", "style": "primary"}],
        [{"text": f"W. GROUP: {grp_status}", "icon_custom_emoji_id": "5420517437885943844", "callback_data": "dxa_w_group", "style": "success"},
         {"text": req_label, "icon_custom_emoji_id": "5472250091332993630", "callback_data": "view_w_requests", "style": "success"}],
        [{"text": "BACK", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
    ]}

def get_payment_emoji_id(method_name):
    key = method_name.upper().replace(" ", "").replace("/", "").replace("-", "")
    apps = bot_settings.get("premium_apps", {})
    for app_key, app_data in apps.items():
        clean_key = app_key.replace(" ", "").replace("/", "").replace("-", "")
        if clean_key in key or key in clean_key:
            return app_data.get("id", "5472250091332993630")
    return "5472250091332993630"

def withdrawal_requests_list_keyboard(requests):
    kb = []
    for row in requests:
        db_id, user_id, amount, method, account, status, ts = row
        label = f"#{db_id} | {method} | {amount} USDT | {account[:8]}..."
        kb.append([{"text": label, "icon_custom_emoji_id": "5472250091332993630", "callback_data": f"wreq_detail_{db_id}", "style": "primary"}])
    kb.append([{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": "view_w_requests", "style": "success"},
               {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "danger"}])
    return {"inline_keyboard": kb}

def w_methods_keyboard():
    kb = []
    for idx, m in enumerate(bot_settings["w_methods"]):
        emoji_id = get_payment_emoji_id(m)
        kb.append([{"text": f"{m}", "icon_custom_emoji_id": emoji_id, "callback_data": f"del_wm_{idx}", "style": "danger"}])
    kb.append([{"text": "Add Method", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_wm", "style": "success"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "primary"}])
    return {"inline_keyboard": kb}

def typed_panels_list_keyboard(p_type):
    kb = []
    for idx, p in enumerate(bot_settings["panels"]):
        if p.get("type", "API Panel") != p_type: continue
        action_text = f"Turn OFF {p['name']}" if p['status'] == 'ON' else f"Turn ON {p['name']}"
        action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
        icon_id = "5420155432272438703" 
        kb.append([
            {"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"},
            {"text": f"{p['name']}", "icon_custom_emoji_id": icon_id, "callback_data": f"conf_pnl_{idx}", "style": "primary"}
        ])
    add_cb = "add_api_panel" if p_type == "API Panel" else "add_cpt_panel"
    kb.append([{"text": "Add New Provider", "icon_custom_emoji_id": "5420323438508155202", "callback_data": add_cb, "style": "success"}])
    kb.append([{"text": "Delete Provider", "icon_custom_emoji_id": "5336944168944047463", "callback_data": f"list_del_{'api' if p_type=='API Panel' else 'cpt'}", "style": "danger"}])
    kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_panels", "style": "primary"}])
    return {"inline_keyboard": kb}

def panel_config_keyboard(idx):
    p = bot_settings["panels"][idx]
    
    kb = []
    action_text = "Turn OFF" if p['status'] == 'ON' else "Turn ON"
    action_icon = "5318840353510408444" if p['status'] == 'ON' else "5192812028632274956"
    kb.append([{"text": action_text, "icon_custom_emoji_id": action_icon, "callback_data": f"tog_pnl_{idx}", "style": "danger" if p['status'] == 'ON' else "success"}])
    
    if p["type"] != "Auto Captcha Panel":
        rec_count_text = "All (Unlimited)" if p.get('records', 0) == 0 else str(p.get('records'))
        kb.append([{"text": "Set API URL", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_api_{idx}", "style": "primary"}])
        kb.append([{"text": "Set Token", "icon_custom_emoji_id": "5353022963132174959", "callback_data": f"set_p_tok_{idx}", "style": "primary"}])
        kb.append([{"text": "Full API (URL+Token)", "icon_custom_emoji_id": "5420517437885943844", "callback_data": f"set_p_fapi_{idx}", "style": "primary"}])
        kb.append([{"text": f"Set Records Count: {rec_count_text}", "icon_custom_emoji_id": "5192739271886282680", "callback_data": f"set_p_rec_{idx}", "style": "primary"}])
        
    kb.append([{"text": "Test Connection", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"test_p_conn_{idx}", "style": "success"}])
        
    back_data = "manage_api_panels" if p.get("type", "API Panel") == "API Panel" else "manage_cpt_panels"
    kb.append([{"text": "Back to Providers", "icon_custom_emoji_id": "5267490665117275176", "callback_data": back_data, "style": "danger"}])
    return {"inline_keyboard": kb}

def build_traffic_ui():
    global recent_traffic
    current_time = time.time()
    recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]

    # Build aggregated stats: (service, iso) -> {count, flag, c_name}
    stats = {}
    for t in recent_traffic:
        srv = t.get("service", "Unknown")
        iso = t.get("iso", "XX")
        flag = t.get("flag", "🌍")
        key = (srv, iso)
        if key not in stats:
            # Resolve country name
            c_name = iso
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    break
            stats[key] = {"count": 0, "flag": flag, "c_name": c_name, "srv": srv, "iso": iso}
        stats[key]["count"] += 1

    txt = "🔴 <b>Live Traffic (Last 1 Hours)</b>\n\n"

    kb = []
    if not stats:
        txt += "<i>No recent traffic found in the last hour...</i>\n"
    else:
        total_all = sum(v["count"] for v in stats.values())

        # Sort by count descending so highest OTP sources appear first (highest % auto-first)
        sorted_entries = sorted(stats.values(), key=lambda x: x["count"], reverse=True)

        for entry in sorted_entries:
            srv = entry["srv"]
            iso = entry["iso"]
            c_name = entry["c_name"]
            count = entry["count"]
            pct = (count / total_all * 100) if total_all else 0.0

            app_full_name, prem_app_html = get_service_info_html(srv)
            prem_flag_html = get_flag_info_html(iso)

            txt += f"{prem_app_html} {app_full_name} | {prem_flag_html} {c_name} | <b>{pct:.1f}%</b>\n"

        txt += f"\n<i>Total OTPs: {total_all}</i>\n"

    txt = render_body_text(txt)
    kb.append([{"text": "Refresh", "icon_custom_emoji_id": "5465368548702446780", "callback_data": "refresh_traffic", "style": "primary"}])
    kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])

    return txt, {"inline_keyboard": kb}

# ==========================================
# Number Upload Finalizer (shared by wait_for_otp_price + skip_otp_price)
# ==========================================
def _finalize_number_upload(chat_id):
    global total_uploaded_stats
    try:
        td = temp_data.get(chat_id)
        if not td:
            send_message(chat_id, render_body_text("❌ Session expired. Please upload the file again."))
            return
        service = td.get("service", "UNKNOWN")
        raw_numbers = td.get("numbers", [])
        filename = td.get("filename", "")

        clean_nums = []
        for num in raw_numbers:
            num = str(num).strip()
            if num:
                if not num.startswith("+"): num = "+" + num
                clean_nums.append(num)

        if not clean_nums:
            send_message(chat_id, render_body_text("❌ No valid numbers found in the file. Please upload again."))
            if chat_id in user_states: del user_states[chat_id]
            if chat_id in temp_data: del temp_data[chat_id]
            return

        auto_country_key = "UNKNOWN"
        auto_country_name = "Unknown"
        prem_flag_html = f"{PEM['world']} "
        first_num = clean_nums[0].replace("+", "").replace(" ", "")
        flags_db_up = bot_settings.get("premium_flags", {})
        sorted_codes = sorted(flags_db_up.keys(), key=len, reverse=True)
        for code in sorted_codes:
            if first_num.startswith(code):
                fd = flags_db_up[code]
                auto_country_key = code
                auto_country_name = fd.get("name", code)
                flag_char_up = fd.get("char", "🏳️")
                flag_eid_up = fd.get("id")
                prem_flag_html = f'<tg-emoji emoji-id="{flag_eid_up}">{flag_char_up}</tg-emoji>' if flag_eid_up else flag_char_up
                break

        batch_id = _fs_batch_id(service, auto_country_key)
        if batch_id in number_batches:
            number_batches[batch_id]["numbers"].extend({"num": n, "shares": 0, "used_by": []} for n in clean_nums)
            number_batches[batch_id]["filename"] = filename
        else:
            number_batches[batch_id] = {
                "filename": filename, "service": service, "country": auto_country_key,
                "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]
            }
        total_uploaded_stats += len(clean_nums)
        save_db()
        _fs_sync_batch(batch_id)

        app_full_name, prem_app_html = get_service_info_html(service)
        otp_price = bot_settings.get("service_otp_prices", {}).get(service, bot_settings.get("otp_reward", 0.1))

        new_tag_html  = '<tg-emoji emoji-id="6271473763439612077">🆕</tg-emoji>'
        up_arrow_html = '<tg-emoji emoji-id="5118734498590098251">⬆️</tg-emoji>'
        total_html    = '<tg-emoji emoji-id="5190806721286657692">🎯</tg-emoji>'
        price_line = f"\n💰 OTP Rate: <b>{otp_price} USDT</b>" if float(otp_price) > 0 else "\n💰 OTP Rate: <b>No reward</b>"
        broadcast_txt = render_body_text(
            f"{new_tag_html} <b>New Stock Added</b> {up_arrow_html}\n\n"
            f"{prem_flag_html} | {prem_app_html} <b>{service.upper()}</b>\n"
            f"{total_html} TOTALL : <b>{len(clean_nums)}</b> Numbers{price_line}"
        )
        broadcast_kb = {"inline_keyboard": [[{
            "text": "  Get Number", "icon_custom_emoji_id": "5460907099884104609",
            "callback_data": f"ntf_get_{service}||{auto_country_key}", "style": "success"
        }]]}

        send_message(chat_id, render_body_text(
            f"{PEM['ok']} <b>{len(clean_nums)} numbers added!</b>\n"
            f"📍 Country: <b>{auto_country_name}</b>\n"
            f"📦 Service: <b>{service}</b>\n"
            f"💰 OTP Price: <b>{otp_price} USDT</b>\n\n"
            f"📢 Broadcasting to all users..."
        ))

        def simple_broadcast(txt, kb):
            b_session = requests.Session()
            url = f"{BASE_URL}/sendMessage"
            for u_id in list(all_known_users):
                try:
                    b_session.post(url, json={"chat_id": u_id, "text": txt, "parse_mode": "HTML",
                                               "disable_web_page_preview": True, "reply_markup": kb}, timeout=5)
                except: pass
                time.sleep(0.035)
        threading.Thread(target=simple_broadcast, args=(broadcast_txt, broadcast_kb)).start()

    except Exception as e:
        try:
            send_message(chat_id, render_body_text(f"❌ <b>Upload Error:</b> <code>{e}</code>\nPlease try again."))
        except: pass
    finally:
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]

# ==========================================
# Update Number Flow Helpers (admin: service -> country -> upload -> price)
# ==========================================
def _all_stocked_numbers_set():
    """Set of all normalized (digits-only) numbers currently in stock across every batch."""
    existing = set()
    for b in number_batches.values():
        for n in b.get("numbers", []):
            existing.add(str(n.get("num", "")).replace("+", "").replace(" ", "").replace("-", "").strip())
    return existing

def _flag_display(code):
    """Return (display_name, flag_html) for a country/phone-code key."""
    flags_db = bot_settings.get("premium_flags", {})
    for fc, fd in flags_db.items():
        iso = fd.get("iso", "").upper()
        name = fd.get("name", "").upper()
        if fc == code or _country_code_matches(code, iso, name):
            fchar = fd.get("char", "🏳️")
            feid = fd.get("id")
            fhtml = f'<tg-emoji emoji-id="{feid}">{fchar}</tg-emoji>' if feid else fchar
            return fd.get("name", code), fhtml
    return code, "🏳️"

def _finalize_update_number_upload(chat_id):
    global total_uploaded_stats
    try:
        td = temp_data.get(chat_id)
        if not td:
            send_message(chat_id, render_body_text("❌ Session expired. Please start again."))
            return
        service = td.get("upd_service", "UNKNOWN")
        country = td.get("upd_country", "UNKNOWN")
        raw_numbers = td.get("numbers", [])
        filename = td.get("filename", "")

        existing = _all_stocked_numbers_set()
        clean_nums = []
        seen_in_file = set()
        duplicate_count = 0
        for num in raw_numbers:
            num = str(num).strip()
            if not num:
                continue
            digits = num.replace("+", "").replace(" ", "").replace("-", "").strip()
            if not digits:
                continue
            if digits in existing or digits in seen_in_file:
                duplicate_count += 1
                continue
            seen_in_file.add(digits)
            if not num.startswith("+"):
                num = "+" + digits
            clean_nums.append(num)

        country_name, flag_html = _flag_display(country)

        if not clean_nums:
            send_message(chat_id, render_body_text(
                f"{PEM['no']} <b>No new numbers added.</b>\n"
                f"All {duplicate_count} number(s) in this file were duplicates or already in stock."
            ))
            if chat_id in user_states: del user_states[chat_id]
            if chat_id in temp_data: del temp_data[chat_id]
            return

        batch_id = _fs_batch_id(service, country)
        if batch_id in number_batches:
            number_batches[batch_id]["numbers"].extend({"num": n, "shares": 0, "used_by": []} for n in clean_nums)
            number_batches[batch_id]["filename"] = filename
        else:
            number_batches[batch_id] = {
                "filename": filename, "service": service, "country": country,
                "numbers": [{"num": n, "shares": 0, "used_by": []} for n in clean_nums]
            }
        total_uploaded_stats += len(clean_nums)
        save_db()
        _fs_sync_batch(batch_id)

        otp_price = bot_settings.get("service_otp_prices", {}).get(service, bot_settings.get("otp_reward", 0.1))
        dup_line = f"\n{PEM['warn']} Duplicates skipped: <b>{duplicate_count}</b>" if duplicate_count else ""

        send_message(chat_id, render_body_text(
            f"{PEM['ok']} <b>Numbers Updated!</b>\n"
            f"📦 Service: <b>{service}</b>\n"
            f"{flag_html} Country: <b>{country_name}</b>\n"
            f"➕ New numbers added: <b>{len(clean_nums)}</b>{dup_line}\n"
            f"💰 OTP Price: <b>{otp_price} USDT</b>"
        ), reply_markup={"inline_keyboard": [[{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})
    except Exception as e:
        try:
            send_message(chat_id, render_body_text(f"❌ <b>Update Error:</b> <code>{e}</code>\nPlease try again."))
        except: pass
    finally:
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]

# ==========================================
# Message Handler
# ==========================================
def handle_message(msg):
    global total_uploaded_stats
    chat_id = msg["chat"]["id"]
    chat_type = msg["chat"].get("type", "private")
    
    if chat_type != "private":
        return
        
    text = msg.get("text", "")
    _from = msg.get("from", {})
    register_user_local(chat_id, username=_from.get("username"), first_name=_from.get("first_name"))

    if is_user_banned(chat_id):
        send_message(chat_id, render_body_text("🚫 <b>You are banned from using this bot!</b>\nIf you think this is a mistake, please contact support."))
        return
    
    # --- REFERRAL FIX: Save inviter BEFORE Force Join ---
    if text.startswith("/start"):
        parts = text.split()
        if len(parts) > 1 and parts[1].isdigit():
            inviter = int(parts[1])
            if inviter != chat_id:
                u = get_user(chat_id)
                if not u.get("referred_by"):
                    with db_lock:
                        conn = get_db_conn()
                        conn.execute("UPDATE users SET referred_by=?, ref_paid=0 WHERE user_id=?", (inviter, chat_id))
                        conn.commit()
                        conn.close()
                    if chat_id in user_cache: user_cache[chat_id]["referred_by"] = inviter
                        
    if not check_force_join(chat_id):
        send_force_join_msg(chat_id)
        return
        
    MAIN_MENU_CMDS = ["GET NUMBER", "TRAFFIC", "Refer", "WITHDRAWAL", "SUPPORT", "Admin Panel", "2FA ONLINE"]
    
    is_main_cmd = False
    if text in MAIN_MENU_CMDS or text.startswith("/start"):
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        is_main_cmd = True
    
    if chat_id in user_states and not is_main_cmd:
        state = user_states[chat_id]
        
        # 🌟 Auto Captcha Panel Setup Flow 
        if state == "wait_for_cpanel_url" and text:
            temp_data[chat_id]["p_data"]["login_url"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_user"
            send_message(chat_id, render_body_text("2️⃣ <b>Username</b>\n➡️ Enter panel username:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_user" and text:
            temp_data[chat_id]["p_data"]["username"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_pass"
            send_message(chat_id, render_body_text("3️⃣ <b>Password</b>\n➡️ Enter panel password:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_pass" and text:
            temp_data[chat_id]["p_data"]["password"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_link"
            send_message(chat_id, render_body_text("4️⃣ <b>Message Link</b>\n➡️ Enter the SMS/OTP data link (JSON):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_link" and text:
            temp_data[chat_id]["p_data"]["msg_link"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_name"
            send_message(chat_id, render_body_text("5️⃣ <b>Number Column Name</b>\n➡️ Number column name in data? (e.g.: number, phone):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_name" and text:
            temp_data[chat_id]["p_data"]["num_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_num_col_idx"
            send_message(chat_id, render_body_text("6️⃣ <b>Number Column Serial</b>\n➡️ Number column serial? (e.g.: 3, 5):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_num_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["num_col_idx"] = int(text)
                user_states[chat_id] = "wait_for_cpanel_msg_col_name"
                send_message(chat_id, render_body_text("7️⃣ <b>Message Column Name</b>\n➡️ Message/OTP column name? (e.g.: message, sms):"), reply_markup=get_cancel_kb())
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_name" and text:
            temp_data[chat_id]["p_data"]["msg_col_name"] = text.strip()
            user_states[chat_id] = "wait_for_cpanel_msg_col_idx"
            send_message(chat_id, render_body_text("8️⃣ <b>Message Column Serial</b>\n➡️ Message column serial? (e.g.: 5, 7):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_cpanel_msg_col_idx" and text:
            if text.isdigit():
                temp_data[chat_id]["p_data"]["msg_col_idx"] = int(text)
                temp_data[chat_id]["p_data"]["login_status"] = "⏳ Pending Auto-Login..."
                
                # Save the panel configuration
                bot_settings["panels"].append(temp_data[chat_id]["p_data"])
                save_db()
                
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Auto Captcha Panel Added Successfully!</b>\n          ।"), reply_markup=main_menu(chat_id))
                
                msg_id = temp_data[chat_id]["msg_id"]
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_cpt_panels", "id": "internal"})
                
                del user_states[chat_id]
                del temp_data[chat_id]
            else:
                 send_message(chat_id, render_body_text("❌ Please enter a valid number serial!"), reply_markup=get_cancel_kb())
            return

        # --- User Management Flows ---
        elif state == "wait_for_um_bal_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID! Please send a numeric User ID."), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            doc_data = get_user(target_uid)
            if not doc_data:
                send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                return
            current_bal = doc_data.get('balance', 0.0)
            temp_data[chat_id]["target_uid"] = target_uid
            user_states[chat_id] = "wait_for_um_bal_amt"
            send_message(chat_id, render_body_text(f"✅ User found!\n💰 Current Balance: {current_bal} \n\n📝 Send the amount to ADD (e.g. 50) or REMOVE (e.g. -50):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_bal_amt" and text:
            try:
                amt = float(text.strip())
                target_uid = temp_data[chat_id]["target_uid"]
                update_balance(target_uid, amt)
                send_message(chat_id, render_body_text(f"{PEM['ok']} Balance updated successfully for {target_uid}!"), reply_markup=main_menu(chat_id))
                send_message(target_uid, render_body_text(f"🔔 Your balance has been adjusted by <b>{amt} </b> by an Admin."))
                del user_states[chat_id]
                del temp_data[chat_id]
            except ValueError:
                send_message(chat_id, render_body_text("❌ Invalid amount! Please send a number."), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_um_ban_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            u_data = get_user(target_uid)
            current_status = u_data.get("banned", False)
            new_status = not current_status
            with db_lock:
                conn = get_db_conn()
                conn.execute("UPDATE users SET banned=? WHERE user_id=?", (1 if new_status else 0, target_uid))
                conn.commit()
                conn.close()
            if target_uid in user_cache: user_cache[target_uid]["banned"] = new_status
            user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
            status_text = "BANNED 🚫" if new_status else "UNBANNED ✅"
            send_message(chat_id, render_body_text(f"✅ User {target_uid} has been {status_text}!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_um_edit_bal" and text:
            t_uid = temp_data[chat_id].get("target_uid")
            raw = text.strip()
            try:
                if raw.startswith("+") or raw.startswith("-"):
                    delta = float(raw)
                    update_balance(t_uid, delta)
                else:
                    new_bal = float(raw)
                    with db_lock:
                        conn = get_db_conn()
                        conn.execute("UPDATE users SET balance=? WHERE user_id=?", (new_bal, t_uid))
                        conn.commit()
                        conn.close()
                    if t_uid in user_cache: user_cache[t_uid]["balance"] = new_bal
                if t_uid in user_cache: user_cache.pop(t_uid, None)
                u_new = get_user(t_uid)
                del user_states[chat_id]
                del temp_data[chat_id]
                send_message(chat_id, render_body_text(
                    f"✅ <b>Balance Updated!</b>\n\n"
                    f"🆔 User: <code>{t_uid}</code>\n"
                    f"💰 New Balance: <b>{u_new.get('balance', 0.0):.2f} USDT</b>"
                ), reply_markup={"inline_keyboard": [[{"text": "◀ Back to User", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"um_view_user_{t_uid}", "style": "success"}]]})
            except:
                send_message(chat_id, render_body_text(
                    "❌ Invalid amount!\n\nSend a number like <code>10.5</code>, <code>+5</code>, or <code>-3</code>:"
                ), reply_markup={"inline_keyboard": [[{"text": "❌ Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"um_view_user_{t_uid}", "style": "danger"}]]})
            return

        elif state == "wait_for_um_prof_uid" and text:
            target_uid_str = text.strip()
            if not target_uid_str.isdigit():
                send_message(chat_id, render_body_text("❌ Invalid ID!"), reply_markup=get_cancel_kb())
                return
            target_uid = int(target_uid_str)
            data = get_user(target_uid)
            if not data:
                send_message(chat_id, render_body_text("❌ User not found in database!"), reply_markup=get_cancel_kb())
                return
            is_verified = True if data.get('total_otps', 0) > 0 else data.get('verified', False)
            prof_text = f"""➖➖➖➖➖➖➖➖
👤 <b>USER PROFILE</b>
➖➖➖➖➖➖➖➖
🆔 ID: <code>{target_uid}</code>
💰 Balance: {data.get('balance', 0.0)} 
🤝 Total Refers: {data.get('total_refers', 0)}
🔐 Total OTPs: {data.get('total_otps', 0)}
✅ Verified: {is_verified}
🚫 Banned: {data.get('banned', False)}
➖➖➖➖➖➖➖➖"""
            kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "primary"}]]}
            send_message(chat_id, render_body_text(prof_text), reply_markup=kb)
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        # --- Database Upload Flow ---
        elif state == "wait_for_db_upload" and "document" in msg:
            if not is_admin(chat_id):
                send_message(chat_id, render_body_text(f"{PEM['no']} This action is restricted to admins only."))
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return
            doc = msg["document"]
            fname_doc = doc.get("file_name", "")
            if not fname_doc.endswith(".db"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a valid <b>.db</b> file."), reply_markup=get_cancel_kb())
                return
            file_id = doc["file_id"]
            fi_resp = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            if not fi_resp.get("ok") or "result" not in fi_resp:
                send_message(chat_id, render_body_text(f"{PEM['no']} Failed to fetch the file from Telegram."), reply_markup=database_management_keyboard())
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return
            file_path_tg = fi_resp["result"]["file_path"]
            db_bytes = requests.get(f"{FILE_URL}{file_path_tg}").content
            import shutil as _shutil
            backup_path = DB_PATH + ".backup"
            try:
                _shutil.copy2(DB_PATH, backup_path)
                os.makedirs("data", exist_ok=True)
                with open(DB_PATH, "wb") as dbf:
                    dbf.write(db_bytes)
                load_db()
                threading.Thread(target=sync_users_list, daemon=True).start()
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                send_message(chat_id, render_body_text(f"{PEM['ok']} <b>Database Replaced Successfully!</b>\n\nThe old database has been saved as a backup."), reply_markup=database_management_keyboard())
            except Exception as e:
                try: _shutil.copy2(backup_path, DB_PATH)
                except: pass
                send_message(chat_id, render_body_text(f"{PEM['no']} Failed to replace database: {e}"), reply_markup=database_management_keyboard())
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            return

        elif state == "wait_for_test_service" and text:
            temp_data[chat_id]["service"] = text.strip()
            user_states[chat_id] = "wait_for_test_number"
            send_message(chat_id, render_body_text("📝 Send the Number (e.g. +8801712345678):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_number" and text:
            temp_data[chat_id]["number"] = text.strip()
            user_states[chat_id] = "wait_for_test_otp"
            send_message(chat_id, render_body_text("📝 Send the OTP (e.g. 556677):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_otp" and text:
            temp_data[chat_id]["otp"] = text.strip()
            user_states[chat_id] = "wait_for_test_lang"
            send_message(chat_id, render_body_text("📝 Send the Language (e.g. EN, AR):"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_test_lang" and text:
            lang = text.strip().upper()
            if not lang.startswith("#"):
                lang = "#" + lang
                
            srv = temp_data[chat_id]["service"]
            num = temp_data[chat_id]["number"]
            otp = temp_data[chat_id]["otp"]
            
            masked = mask_number(num)
            prem_flag_html = get_flag_info_html(num)
            char, iso = get_flag_and_code(num)
            app_full_name, prem_app_html = get_service_info_html(srv)
            
            msg_text = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {prem_flag_html} <b>{masked}</b> {lang}\n╚═══════════════╝")
            
            for fw in bot_settings["fw_groups"]:
                kb = build_otp_fw_kb(otp, fw)
                send_message(fw["chat_id"], msg_text, reply_markup={"inline_keyboard": kb})
                
            send_message(chat_id, render_body_text(f"{PEM['ok']} Test message formatted and sent to all Forward Groups!"), reply_markup=main_menu(chat_id))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_emoji_extract":
            entities = msg.get("entities", [])
            custom_emoji_id = None
            emoji_text = ""
            for ent in entities:
                if ent.get("type") == "custom_emoji":
                    custom_emoji_id = ent.get("custom_emoji_id")
                    offset = ent.get("offset", 0)
                    length = ent.get("length", 0)
                    b_text = msg.get("text", "").encode('utf-16-le')
                    emoji_text = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                    break
            
            if custom_emoji_id:
                temp_data[chat_id] = {"id": custom_emoji_id, "char": emoji_text}
                user_states[chat_id] = "wait_for_emoji_details"
                send_message(chat_id, render_body_text(f"{PEM['ok']} Emoji ID  : <code>{custom_emoji_id}</code>\n\n📌         ।\n\n<b>:</b>\n`FLAG | 880 | BD | Bangladesh`\n\n`APP | WhatsApp`"), reply_markup=get_cancel_kb())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']}  Premium Emoji  !   Custom Emoji  ।"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_emoji_details" and text:
            parts = [p.strip() for p in text.split("|")]
            mode = parts[0].upper()
            eid = temp_data[chat_id]["id"]
            char = temp_data[chat_id]["char"]
            
            if mode == "FLAG" and len(parts) == 4:
                code, iso, name = parts[1], parts[2], parts[3]
                bot_settings["premium_flags"][code] = {"char": char, "iso": iso.upper(), "name": name, "id": eid}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} Flag Emoji  !\nCode: {code} | Name: {name}"), reply_markup=emoji_settings_keyboard())
            elif mode == "APP" and len(parts) == 2:
                name = parts[1]
                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name.title()}
                save_db()
                send_message(chat_id, render_body_text(f"{PEM['ok']} App Emoji  !\nName: {name}"), reply_markup=emoji_settings_keyboard())
            else:
                send_message(chat_id, render_body_text(f"{PEM['no']}  !\n\n :\n`FLAG | 880 | BD | Bangladesh`\n`APP | WhatsApp`"))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state in ["wait_for_flag_txt", "wait_for_app_txt"] and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            content = requests.get(f"{FILE_URL}{file_path}").text
            
            mode = "flags" if state == "wait_for_flag_txt" else "apps"
            count = 0
            
            if mode == "flags":
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            prefix_str = line[:json_match.start()].strip()
                            code_match = re.search(r'\((\d+)\)', prefix_str)
                            iso_match = re.search(r'\(([A-Za-z]+)\)', prefix_str)
                            
                            if code_match and iso_match and char and eid:
                                code = code_match.group(1)
                                iso = iso_match.group(1).upper()
                                name = prefix_str.replace(f"({code})", "").replace(f"({iso_match.group(1)})", "").replace(char, "").strip()
                                bot_settings["premium_flags"][code] = {"char": char, "iso": iso, "name": name, "id": eid}
                                count += 1
                        except: pass
            else:
                for line in content.splitlines():
                    json_match = re.search(r'(\{.*\})', line)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            char = data.get("emoji")
                            eid = data.get("id")
                            
                            name_part = line[:json_match.start()].strip()
                            name = name_part.replace(char, '').strip() if char else name_part
                            
                            if char and eid and name:
                                bot_settings["premium_apps"][name.upper()] = {"char": char, "id": eid, "name": name}
                                count += 1
                        except: pass
            
            save_db()
            send_message(chat_id, render_body_text(f"{PEM['ok']} Successfully loaded {count} Emojis!"), reply_markup=emoji_settings_keyboard())
            del user_states[chat_id]
            return

        elif state == "wait_for_broadcast":
            msg_id = msg["message_id"]
            send_message(chat_id, render_body_text(f"{PEM['ok']} Broadcast started..."))
            threading.Thread(target=broadcast_copymessage, args=(chat_id, msg_id)).start()
            del user_states[chat_id]
            return

        elif state == "wait_for_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text
            
            temp_data[chat_id] = {"numbers": file_content.splitlines(), "filename": doc["file_name"]}
            user_states[chat_id] = "wait_for_service"
            send_message(chat_id, render_body_text(f"{PEM['ok']} File received.\n\n📌 Enter the service name (e.g., WHATSAPP):"), reply_markup=get_cancel_kb())
            return

        elif state == "wait_for_service" and text:
            service = text.upper()
            temp_data[chat_id]["service"] = service
            user_states[chat_id] = "wait_for_otp_price"
            default_rate = bot_settings.get("otp_reward", 0.1)
            price_kb = {"inline_keyboard": [
                [{"text": f"⏭ Skip (Default: {default_rate} USDT)", "callback_data": "skip_otp_price", "style": "success"}],
                [{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]
            ]}
            send_message(chat_id, render_body_text(
                f"💰 <b>OTP Price for {service}</b>\n\n"
                f"Enter OTP reward per code for this service (e.g. <code>0.5</code>)\n"
                f"Enter <code>0</code> for no reward\n"
                f"Or tap <b>Skip</b> to use default rate (<b>{default_rate} USDT</b>)"
            ), reply_markup=price_kb)
            return

        elif state == "wait_for_otp_price":
            if not text: return
            try:
                otp_price = float(text.strip())
                if otp_price < 0: raise ValueError
            except (ValueError, AttributeError):
                send_message(chat_id, render_body_text("❌ Enter a valid number (e.g. <code>0.5</code> or <code>0</code>)"), reply_markup=get_cancel_kb())
                return
            service = temp_data[chat_id].get("service", "")
            bot_settings.setdefault("service_otp_prices", {})[service] = otp_price
            _finalize_number_upload(chat_id)
            return

        elif state == "wait_for_upd_txt" and "document" in msg:
            doc = msg["document"]
            if not doc["file_name"].endswith(".txt"):
                send_message(chat_id, render_body_text(f"{PEM['no']} Please upload a .txt file only."))
                return
            file_id = doc["file_id"]
            file_info = requests.get(f"{BASE_URL}/getFile?file_id={file_id}").json()
            file_path = file_info["result"]["file_path"]
            file_content = requests.get(f"{FILE_URL}{file_path}").text

            td = temp_data.get(chat_id, {})
            td["numbers"] = file_content.splitlines()
            td["filename"] = doc["file_name"]
            temp_data[chat_id] = td
            user_states[chat_id] = "wait_for_upd_price"
            service = td.get("upd_service", "")
            default_rate = bot_settings.get("service_otp_prices", {}).get(service, bot_settings.get("otp_reward", 0.1))
            price_kb = {"inline_keyboard": [
                [{"text": f"⏭ Skip (Default: {default_rate} USDT)", "callback_data": "skip_upd_price", "style": "success"}],
                [{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_state", "style": "danger"}]
            ]}
            send_message(chat_id, render_body_text(
                f"{PEM['ok']} File received.\n\n💰 <b>OTP Price for {service}</b>\n\n"
                f"Enter OTP reward per code for this batch (e.g. <code>0.5</code>)\n"
                f"Enter <code>0</code> for no reward\n"
                f"Or tap <b>Skip</b> to use current rate (<b>{default_rate} USDT</b>)"
            ), reply_markup=price_kb)
            return

        elif state == "wait_for_upd_price":
            if not text: return
            try:
                otp_price = float(text.strip())
                if otp_price < 0: raise ValueError
            except (ValueError, AttributeError):
                send_message(chat_id, render_body_text("❌ Enter a valid number (e.g. <code>0.5</code> or <code>0</code>)"), reply_markup=get_cancel_kb())
                return
            service = temp_data[chat_id].get("upd_service", "")
            bot_settings.setdefault("service_otp_prices", {})[service] = otp_price
            _finalize_update_number_upload(chat_id)
            return

        elif state == "wait_for_add_voltx_key" and text:
            bot_settings["voltx_keys"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"✅ Voltx API Key Added! Total Keys: {len(bot_settings.get('voltx_keys', []))}"), reply_markup=voltx_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return


        elif state == "wait_for_add_vsc" and text:
            code = text.strip().replace("+", "")
            if "voltx_search_countries" not in bot_settings: bot_settings["voltx_search_countries"] = []
            bot_settings["voltx_search_countries"].append(code)
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "voltx_search_country", "id": "internal"})
            del user_states[chat_id]
            del temp_data[chat_id]
            return




        elif state == "wait_vx_srv_name" and text:
            srv = text.strip().upper()
            if "voltx_services" not in bot_settings: bot_settings["voltx_services"] = {}
            if srv not in bot_settings["voltx_services"]: bot_settings["voltx_services"][srv] = {}
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": "manage_voltx_srv", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_cnt_name" and text:
            cnt = text.strip()
            srv = temp_data[chat_id]["srv"]
            if cnt not in bot_settings["voltx_services"][srv]: bot_settings["voltx_services"][srv][cnt] = []
            save_db()
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_srv_{srv}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_vx_addr" and text:
            srv, cnt = temp_data[chat_id]["srv"], temp_data[chat_id]["cnt"]
            new_range = text.strip().replace("+", "")
            
            if new_range not in bot_settings["voltx_services"][srv][cnt]:
                bot_settings["voltx_services"][srv][cnt].append(new_range)
                
                if "voltx_search_countries" not in bot_settings:
                    bot_settings["voltx_search_countries"] = []
                if new_range not in bot_settings["voltx_search_countries"]:
                    bot_settings["voltx_search_countries"].append(new_range)
                    
                save_db()
                
            delete_message(chat_id, msg["message_id"])
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": temp_data[chat_id]["msg_id"]}, "data": f"vx_cnt_{srv}_{cnt}", "id": "internal"})
            del user_states[chat_id]
            return

        elif state == "wait_for_add_wm" and text:
            bot_settings["w_methods"].append(text.strip())
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fj" and text:
            bot_settings["fj_channels"].append(parse_chat_id(text))
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🔗 <b>FORCE JOIN SYSTEM</b>\nManage channels below:\n<i>(Note: For private links, use numeric IDs like -100...)</i>"), reply_markup=fj_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_adm" and text:
            if text.isdigit():
                bot_settings["admins"].append(int(text))
                save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("👥 <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_add_fw_id" and text:
            parsed_cid = parse_chat_id(text.strip())
            group_name = _get_chat_title(parsed_cid)
            bot_settings["fw_groups"].append({"chat_id": parsed_cid, "name": group_name, "buttons": []})
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_add_fw_btn" and text:
            fw_idx = temp_data[chat_id]["fw_idx"]
            if "-" in text:
                parts = text.split("-", 1)
                btn_text = parts[0].strip()
                btn_url = parts[1].strip()
                
                emoji_id = None
                emoji_char = ""
                for ent in msg.get("entities", []):
                    if ent.get("type") == "custom_emoji":
                        emoji_id = ent.get("custom_emoji_id")
                        offset = ent.get("offset", 0)
                        length = ent.get("length", 0)
                        b_text = text.encode('utf-16-le')
                        emoji_char = b_text[offset*2:(offset+length)*2].decode('utf-16-le')
                        break
                
                if emoji_char:
                    btn_text = btn_text.replace(emoji_char, "").strip()
                    
                btn_data = {"text": btn_text, "url": btn_url}
                if emoji_id:
                    btn_data["icon_custom_emoji_id"] = emoji_id
                    
                bot_settings["fw_groups"][fw_idx]["buttons"].append(btn_data)
                save_db()
            delete_message(chat_id, msg["message_id"])
            fw_grp = bot_settings['fw_groups'][fw_idx]
            fw_grp_lbl = fw_grp.get("name") or fw_grp['chat_id']
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(f"🛡 <b>Manage Group:</b> {fw_grp_lbl}"), reply_markup=specific_fw_group_keyboard(fw_idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return
            
        elif state == "wait_for_otp_link" and text:
            bot_settings["otp_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_fw_channel_link" and text:
            bot_settings["fw_channel_link"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_panel_name" and text:
            p_name = text.strip()
            t_key = temp_data[chat_id].get("add_type", "api")
            msg_id = temp_data[chat_id]["msg_id"]
            delete_message(chat_id, msg["message_id"])
            
            if t_key == "logc":
                user_states[chat_id] = "wait_for_cpanel_url"
                temp_data[chat_id] = {"msg_id": msg_id, "p_data": {
                    "name": p_name, "type": "Auto Captcha Panel", "status": "ON", "records": 0, "login_status": "⏳ Pending First Login"
                }}
                edit_message(chat_id, msg_id, render_body_text("1️⃣ <b>Login URL</b>\n➡️ Panel  Login Link :"), reply_markup=get_cancel_kb())
                return
            else:
                bot_settings["panels"].append({
                    "name": p_name, "type": "API Panel", "status": "OFF", "api_url": "", "token": "", "records": 0
                })
                save_db()
                handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_api_panels", "id": "internal"})
                if chat_id in user_states: del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
                return

        elif state == "wait_for_p_api" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_tok" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["token"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_fapi" and text:
            idx = temp_data[chat_id]["p_idx"]
            bot_settings["panels"][idx]["full_api_url"] = text.strip()
            save_db()
            delete_message(chat_id, msg["message_id"])
            p = bot_settings["panels"][idx]
            ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_p_rec" and text:
            if text.isdigit():
                idx = temp_data[chat_id]["p_idx"]
                bot_settings["panels"][idx]["records"] = int(text)
                save_db()
                delete_message(chat_id, msg["message_id"])
                p = bot_settings["panels"][idx]
                
                ui_text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
                edit_message(chat_id, temp_data[chat_id]["msg_id"], render_body_text(ui_text), reply_markup=panel_config_keyboard(idx))
            else:
                send_message(chat_id, render_body_text("❌ Please enter a valid number! Try again."), reply_markup=get_cancel_kb())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "set_dxa":
            msg_id = temp_data[chat_id]["msg_id"]
            key = temp_data[chat_id]["key"]
            try:
                if key in ["min_withdraw", "otp_reward", "refer_reward"]: bot_settings[key] = float(text)
                elif key in ["cooldown", "num_req", "num_share"]: bot_settings[key] = int(text)
                else: bot_settings[key] = text
                save_db()
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>DEV CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
            except:
                delete_message(chat_id, msg["message_id"])
                edit_message(chat_id, msg_id, render_body_text("🕹 <b>DEV CONTROL PANEL</b>\n\n❌ Invalid value!"), reply_markup=dxa_control_keyboard())
            del user_states[chat_id]
            del temp_data[chat_id]
            return

        elif state == "wait_for_withdraw_amount" and text:
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            try:
                amount = float(text.strip())
                bal = temp_data[chat_id]["balance"]
                min_w = bot_settings['min_withdraw']
                
                if amount < min_w:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ Minimum withdrawal is {min_w} USDT!\n💰 Balance: {bal} \n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                if amount > bal:
                    if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text(f"❌ You don't have enough balance!\n💰 Balance: {bal} \n\n📝 Enter again:"), reply_markup=get_cancel_kb())
                    return
                    
                temp_data[chat_id]["amount"] = amount
                user_states[chat_id] = "wait_for_withdraw_number"
                if msg_id_to_edit:
                    edit_message(chat_id, msg_id_to_edit, render_body_text(f"✅ Amount: {amount} \n\n📱 Now send your <b>{temp_data[chat_id]['method']}</b> account number:"), reply_markup=get_cancel_kb())
            except ValueError:
                if msg_id_to_edit: edit_message(chat_id, msg_id_to_edit, render_body_text("❌ Invalid amount!\n\n📝 Please send a valid number:"), reply_markup=get_cancel_kb())
            return
            
        elif state == "wait_for_2fa_key" and text:
            msg_id_to_edit = temp_data.get(chat_id, {}).get("msg_id")
            delete_message(chat_id, msg.get("message_id"))

            if not msg_id_to_edit:
                send_message(chat_id, render_body_text("❌ Error: Message not found. Try again."))
                del user_states[chat_id]
                return

            try:
                secret = text.strip().replace(" ", "")
                totp = pyotp.TOTP(secret)
                code = totp.now()
                remaining_time = 30 - (int(time.time()) % 30)
                
                success_txt = (
                    f"━━━━━━━━━━━━━━━\n"
                    f"《 🔐 <b>2FA CODE</b> 》\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                    f"━━━━━━━━━━━━━━━\n"
                    f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                    f"━━━━━━━━━━━━━━━"
                )
                kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                      [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                       {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                      [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
                
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
                del user_states[chat_id]
                if chat_id in temp_data: del temp_data[chat_id]
            except Exception:
                error_txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━\n❌ <b>Invalid Secret Key! Try again.</b>\n━━━━━━━━━━━━━━━"
                cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
                edit_message(chat_id, msg_id_to_edit, render_body_text(error_txt), reply_markup=cancel_kb)
            return

        elif state == "wait_for_withdraw_number":
            msg_id_to_edit = temp_data[chat_id].get("msg_id")
            
            method = temp_data[chat_id]["method"]
            amount = temp_data[chat_id]["amount"]
            number = text
            req_id = f"W_{str(uuid.uuid4())[:6].upper()}"
            
            first_name = msg.get("from", {}).get("first_name", "User")
            last_name = msg.get("from", {}).get("last_name", "")
            full_name = f"{first_name} {last_name}".strip()
            
            update_balance(chat_id, -amount)
            pending_withdrawals[req_id] = {"user_id": chat_id, "amount": amount, "method": method, "number": number, "full_name": full_name}
            
            try:
                with db_lock:
                    conn = get_db_conn()
                    conn.execute(
                        "INSERT INTO withdrawals (user_id,amount,method,account,status,timestamp) VALUES (?,?,?,?,?,?)",
                        (chat_id, amount, method, number, "pending", __import__('time').time())
                    )
                    conn.commit()
                    conn.close()
            except: pass
                
            if bot_settings["w_group"]:
                admin_msg = f"🎙 <b>NEW WITHDRAWAL REQUEST</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={chat_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amount} USDT\n🍏 <b>NUMBER:</b> <code>{number}</code>\n🏦 <b>METHOD:</b> {method}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
                kb = {"inline_keyboard": [[{"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wapp_{req_id}", "style": "success"}, {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrej_{req_id}", "style": "danger"}]]}
                send_message(bot_settings["w_group"], render_body_text(admin_msg), reply_markup=kb)
            
            kb = {"inline_keyboard": [[{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]}
            method_eid = get_payment_emoji_id(method)
            method_emoji_html = f'<tg-emoji emoji-id="{method_eid}">💳</tg-emoji>'
            success_text = f"{PEM['ok']} Your withdrawal request has been submitted!\n\n🧾 <b>Req ID:</b> {req_id}\n💰 <b>Amount:</b> {amount} USDT\n{method_emoji_html} <b>Method:</b> {method}\n📱 <b>Number:</b> <code>{number}</code>"
            
            if msg_id_to_edit:
                edit_message(chat_id, msg_id_to_edit, render_body_text(success_text), reply_markup=kb)
            else:
                send_message(chat_id, render_body_text(success_text), reply_markup=kb)
                
            del user_states[chat_id]
            del temp_data[chat_id]
            return

    # --- Regular Commands ---
    if text.startswith("/start"):
        get_user(chat_id)

        # --- PROCESS PENDING REFERRAL ---
        u_data = get_user(chat_id)
        if u_data.get("referred_by") and not u_data.get("ref_paid"):
            inviter = u_data["referred_by"]
            add_referral(inviter, chat_id)
            with db_lock:
                conn = get_db_conn()
                conn.execute("UPDATE users SET ref_paid=1 WHERE user_id=?", (chat_id,))
                conn.commit()
                conn.close()
            if chat_id in user_cache: user_cache[chat_id]["ref_paid"] = 1

        c_msg = bot_settings["custom_messages"].get("start", {})
        raw_txt = c_msg.get("text", f"{PEM['hi']} Welcome!")
        _first_name = _from.get("first_name") or _from.get("username") or "User"
        raw_txt = raw_txt.replace("{name}", _first_name).replace("{bot_name}", BOT_NAME).replace("{bot_username}", BOT_USERNAME)
        txt = render_body_text(raw_txt)
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        if kb:
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})
            send_message(chat_id, render_body_text(f"{PEM['gear']} Navigation Menu:"), reply_markup=main_menu(chat_id))
        else:
            send_message(chat_id, txt, reply_markup=main_menu(chat_id))
            
    elif text == "TRAFFIC":
        txt, markup = build_traffic_ui()
        send_message(chat_id, txt, reply_markup=markup)
        
    elif text == "Refer":
        u_data = get_user(chat_id)
        ref_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
        c_msg = bot_settings["custom_messages"].get("refer", {})
        
        raw_txt = c_msg.get("text", f"{PEM['gift']} Refer").replace("{ref_link}", ref_link).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{ref_reward}", str(bot_settings['refer_reward']))
        txt = render_body_text(raw_txt)
        
        kb = [[{"text": "COPY LINK", "icon_custom_emoji_id": "5192739271886282680", "copy_text": {"text": ref_link}, "style": "success"}]]
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "CLOSE", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "WITHDRAWAL":
        if not bot_settings["withdraw_on"]:
            send_message(chat_id, render_body_text(f"{PEM['no']} Withdrawals are currently disabled."))
            return
        
        u_data = get_user(chat_id)
        bal = u_data.get('balance', 0.0)
        
        c_msg = bot_settings["custom_messages"].get("withdrawal", {})
        raw_txt = c_msg.get("text", "Withdrawal").replace("{bal}", str(bal)).replace("{total_otp}", str(u_data.get('total_otps', 0))).replace("{total_ref}", str(u_data.get('total_refers', 0))).replace("{min_w}", str(bot_settings['min_withdraw']))
        txt = render_body_text(raw_txt)
        
        kb = []
        for m in bot_settings["w_methods"]:
            emoji_id = get_payment_emoji_id(m.strip())
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": emoji_id, "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})

    elif text == "PROFILE":
        u_data = get_user(chat_id)
        bal = round(u_data.get('balance', 0.0), 4)
        total_refers = u_data.get('total_refers', 0)
        total_otps = u_data.get('total_otps', 0)
        today_str = datetime.now().strftime("%Y-%m-%d")
        d_entry = daily_otps.get(chat_id, {})
        today_otp_count = d_entry.get("count", 0) if d_entry.get("date") == today_str else 0
        first_name = msg.get("from", {}).get("first_name", "User")
        last_name = msg.get("from", {}).get("last_name", "")
        full_name = f"{first_name} {last_name}".strip()
        profile_txt = (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"《 {PEM['user']} MY PROFILE 》\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['user']} <b>Name:</b> {full_name}\n"
            f"{PEM['num']} <b>User ID:</b> <code>{chat_id}</code>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['money']} <b>Balance:</b> {bal} USDT\n"
            f"{PEM['gift']} <b>Total Refers:</b> {total_refers}\n"
            f"{PEM['msg']} <b>Total OTPs:</b> {total_otps}\n"
            f"{PEM['graph']} <b>Today OTPs:</b> {today_otp_count}\n"
            f"━━━━━━━━━━━━━━━━━━"
        )
        kb_rows = []
        if bot_settings.get("withdraw_on", True):
            kb_rows.append([{"text": "WITHDRAW", "icon_custom_emoji_id": "5472250091332993630", "callback_data": "profile_withdraw", "style": "success"}])
        kb_rows.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        kb = {"inline_keyboard": kb_rows}
        send_message(chat_id, render_body_text(profile_txt), reply_markup=kb)

    elif text == "Admin Panel" and is_admin(chat_id):
        send_message(chat_id, get_admin_text(), reply_markup=admin_panel_keyboard())

    elif text == "GET NUMBER":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        all_services = local_srvs.union(voltx_srvs)
        
        if not all_services:
            send_message(chat_id, render_body_text(f"{PEM['no']} No numbers or services available!"))
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            
            apps_db = bot_settings.get("premium_apps", {})
            kb = []
            for s in all_services:
                emoji_id = "5352694861990501856" # Default icon
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data:
                            emoji_id = app_data["id"]
                            break
                kb.append([{"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"}])
            
            for b in c_msg.get("buttons", []): 
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                kb.append([b_copy])
            kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            
            send_message(chat_id, txt, reply_markup={"inline_keyboard": kb})


    elif text == "2FA ONLINE" or text == "🔐 2FA ONLINE":
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        send_message(chat_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif text == "SUPPORT":
        c_msg = bot_settings["custom_messages"].get("support", {})
        txt = render_body_text(c_msg.get("text", f"{PEM['msg']} Support"))
        if not txt.strip(): txt = render_body_text(f"{PEM['msg']} Support")
        kb = []
        for b in c_msg.get("buttons", []):
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        sup_link = bot_settings.get("support_link", "")
        if sup_link:
            kb.insert(0, [{"text": "Contact Support", "icon_custom_emoji_id": "5337302974806922068", "url": sup_link, "style": "success"}])
            
        kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        send_message(chat_id, txt, reply_markup={"inline_keyboard": kb} if kb else None)

def expire_previous_number(chat_id, current_msg_id=None):
    if chat_id in user_active_sessions:
        prev_data = user_active_sessions[chat_id]
        prev_msg_id = prev_data["msg_id"]
        nums = prev_data["nums"]

        save_db()

        # Only show "Number Expired" on a DIFFERENT old message.
        # If same message (e.g. Change Number), we're about to overwrite it — skip.
        if current_msg_id is None or prev_msg_id != current_msg_id:
            kb = [[{"text": "Number Expired", "icon_custom_emoji_id": "5336997731481193790", "callback_data": "ignore", "style": "danger"}]]
            try:
                edit_message(chat_id, prev_msg_id, "ㅤ\n", reply_markup={"inline_keyboard": kb})
            except:
                pass
        del user_active_sessions[chat_id]

# ==========================================
# Callback Query Handler
# ==========================================
def handle_callback(call):
    global total_assigned_stats, voltx_assigned_numbers
    chat_id = call["message"]["chat"]["id"]
    chat_type = call["message"]["chat"].get("type", "private")
    data = call.get("data", "")
    _from = call.get("from", {})
    if _from:
        register_user_local(chat_id, username=_from.get("username"), first_name=_from.get("first_name"))


    if not data.startswith("test_p_conn_") and not data.startswith("c_n_") and not data.startswith("g_c_"):
        try: threading.Thread(target=answer_callback, args=(call["id"],)).start()
        except: pass

    if chat_type != "private" and not (data.startswith("wapp_") or data.startswith("wrej_")):
        return

    msg_id = call["message"]["message_id"]

    if chat_type == "private":
        if is_user_banned(chat_id):
            answer_callback(call["id"], "🚫 You are banned from using this bot!", show_alert=True)
            return

        if not check_force_join(chat_id) and data != "check_fj":
            send_force_join_msg(chat_id)
            return

    if data == "check_fj":
        if check_force_join(chat_id):
            delete_message(chat_id, msg_id)
            send_message(chat_id, render_body_text(f"{PEM['ok']} Thanks for joining! You can now use the bot."), reply_markup=main_menu(chat_id))
            
            # --- PROCESS PENDING REFERRAL ---
            u_data = get_user(chat_id)
            if u_data.get("referred_by") and not u_data.get("ref_paid"):
                inviter = u_data["referred_by"]
                add_referral(inviter, chat_id)
                with db_lock:
                    conn = get_db_conn()
                    conn.execute("UPDATE users SET ref_paid=1 WHERE user_id=?", (chat_id,))
                    conn.commit()
                    conn.close()
                if chat_id in user_cache: user_cache[chat_id]["ref_paid"] = 1
        else:
            answer_callback(call["id"], "❌ You haven't joined all channels yet!", show_alert=True)
        return

    if data == "close_msg":
        delete_message(chat_id, msg_id)
        
    elif data == "cancel_state":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        delete_message(chat_id, msg_id)

    elif data == "skip_otp_price":
        if chat_id not in temp_data or "service" not in temp_data.get(chat_id, {}):
            answer_callback(call["id"], "⚠️ Session expired. Please upload again.", show_alert=True)
            return
        answer_callback(call["id"])
        _finalize_number_upload(chat_id)

    elif data == "skip_upd_price":
        if chat_id not in temp_data or "upd_service" not in temp_data.get(chat_id, {}):
            answer_callback(call["id"], "⚠️ Session expired. Please upload again.", show_alert=True)
            return
        answer_callback(call["id"])
        _finalize_update_number_upload(chat_id)

    elif data == "cancel_2fa":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        txt = "━━━━━━━━━━━━━━━\n《 🔐 <b>2FA ONLINE</b> 》\n━━━━━━━━━━━━━━━\n<i>Generate your 2FA security code instantly using your secret key.</i>\n━━━━━━━━━━━━━━━"
        kb = [[{"text": "Generate 2fa code", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "gen_2fa", "style": "success"}],
              [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data == "gen_2fa":
        user_states[chat_id] = "wait_for_2fa_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        txt = "━━━━━━━━━━━━━━━\n《 🔑 <b>ENTER 2FA KEY</b> 》\n━━━━━━━━━━━━━━━\n📝 <b>SEND YOUR 2FA SECRET KEY</b>\n━━━━━━━━━━━━━━━"
        kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_2fa", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data.startswith("ref_2fa_"):
        secret = data.replace("ref_2fa_", "")
        try:
            totp = pyotp.TOTP(secret)
            code = totp.now()
            remaining_time = 30 - (int(time.time()) % 30)
            
            success_txt = (
                f"━━━━━━━━━━━━━━━\n"
                f"《 🔐 <b>2FA CODE</b> 》\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔐 <b>CODE:</b> <code>{code}</code>\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🕓 <b>EXPIRES IN:</b> {remaining_time}s\n"
                f"━━━━━━━━━━━━━━━"
            )
            kb = [[{"text": f"Click to copy {code}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": code}, "style": "success"}],
                  [{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": f"ref_2fa_{secret}", "style": "primary"},
                   {"text": "New Code", "icon_custom_emoji_id": "5352552689983067014", "callback_data": "gen_2fa", "style": "danger"}],
                  [{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]
            
            edit_message(chat_id, msg_id, render_body_text(success_txt), reply_markup={"inline_keyboard": kb})
        except:
            answer_callback(call["id"], "❌ Error refreshing code!", show_alert=True)

    elif data == "cancel_dxa_edit":
        if chat_id in user_states: del user_states[chat_id]
        if chat_id in temp_data: del temp_data[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DEV CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())
        
    elif data == "dummy_alert":
        answer_callback(call["id"], "This feature will be added later!", show_alert=True)
        
    elif data == "refresh_traffic":
        txt, markup = build_traffic_ui()
        edit_message(chat_id, msg_id, txt, reply_markup=markup)
        answer_callback(call["id"], "✅ Traffic Refreshed!", show_alert=False)

    elif data.startswith("exp_rng_"):
        srv_query = data.replace("exp_rng_", "")
        
        country_stats = {}
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query):
                    iso = t.get("iso", "XX")
                    flag = t.get("flag", "🌍")
                    if iso not in country_stats:
                        country_stats[iso] = {"count": 0, "flag": flag}
                    country_stats[iso]["count"] += 1
        
        if not country_stats:
            answer_callback(call["id"], "❌ No recent traffic found for this service!", show_alert=True)
            return
            
        kb = []
        for iso, c_data in sorted(country_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            count = c_data["count"]
            c_name = iso
            emoji_id = "5780471598922337683"
            for code, fdata in bot_settings.get("premium_flags", {}).items():
                if fdata.get("iso") == iso:
                    c_name = fdata.get("name", iso)
                    if "id" in fdata: emoji_id = fdata["id"]
                    break
            
            btn_text = f"{c_name} ({iso}) - {count} OTP"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": emoji_id, "callback_data": f"exp_c_{srv_query}_{iso}", "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "refresh_traffic", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Explore Service: {prem_app_html} {app_full_name}</b>\n\nSelect a country to view available ranges:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("exp_c_"):
        parts = data.split("_")
        srv_query = parts[2]
        iso_query = parts[3]
        
        nums = []
        current_time = time.time()
        for t in recent_traffic:
            if current_time - t.get("time", 0) <= 3600:
                if t.get("service", "").startswith(srv_query) and t.get("iso") == iso_query:
                    num = t.get("number", "").replace("+", "").strip()
                    if num: nums.append(num)
        
        if not nums:
            answer_callback(call["id"], "❌ No recent numbers found for this country!", show_alert=True)
            return
            

        known_ranges = set()
        for s_name, c_dict in bot_settings.get("voltx_services", {}).items():
            for c_name, r_list in c_dict.items():
                for r in r_list:
                    known_ranges.add(r)
                    
        sorted_known = sorted(list(known_ranges), key=len, reverse=True)
        
        r_counts = Counter()
        for num in nums:
            matched = False
            for r in sorted_known:
                if num.startswith(r):
                    r_counts[r] += 1
                    matched = True
                    break
            if not matched:
                if len(num) >= 7:
                    r_counts[num[:7]] += 1
                else:
                    r_counts[num] += 1
                    
        r_list = r_counts.most_common(12)
        
        kb = []
        for r, count in r_list:

            kb.append([{"text": f"{r} ({count})", "icon_custom_emoji_id": "5352862640592949843", "copy_text": {"text": r}, "style": "primary"}])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"exp_rng_{srv_query}", "style": "danger"}])
        
        app_full_name, prem_app_html = get_service_info_html(srv_query)
        prem_flag_html = get_flag_info_html(iso_query)
        
        edit_message(chat_id, msg_id, render_body_text(f"📊 <b>Ranges for {prem_app_html} {app_full_name} - {prem_flag_html} {iso_query}</b>\n\nClick on any range to copy it."), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    # --- User Management Flows Integration ---
    elif data == "user_management":
        edit_message(chat_id, msg_id, get_user_management_text(), reply_markup=user_management_keyboard())

    elif data == "um_manage_balance":
        user_states[chat_id] = "wait_for_um_bal_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Manage Balance:"), reply_markup=get_cancel_kb())
        
    elif data == "um_ban_unban":
        user_states[chat_id] = "wait_for_um_ban_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to Ban or Unban:"), reply_markup=get_cancel_kb())

    elif data == "um_user_profile":
        user_states[chat_id] = "wait_for_um_prof_uid"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID to View Profile:"), reply_markup=get_cancel_kb())

    elif data.startswith("um_user_list_"):
        page = int(data.split("_")[-1])
        per_page = 5
        with db_lock:
            conn = get_db_conn()
            total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            rows = conn.execute(
                "SELECT user_id, username, first_name, balance, banned FROM users ORDER BY user_id DESC LIMIT ? OFFSET ?",
                (per_page, page * per_page)
            ).fetchall()
        total_pages = max(1, (total_users + per_page - 1) // per_page)
        kb = []
        for row in rows:
            uid, uname, fname, bal, banned = row
            label_name = f"@{uname}" if uname else (fname or str(uid))
            ban_mark = " 🚫" if banned else ""
            kb.append([{"text": f"{label_name}{ban_mark}  |  💰{bal:.2f}", "callback_data": f"um_view_user_{uid}", "style": "primary"}])
        nav = []
        if page > 0:
            nav.append({"text": "◀ Prev", "callback_data": f"um_user_list_{page-1}", "style": "primary"})
        if (page + 1) < total_pages:
            nav.append({"text": "Next ▶", "callback_data": f"um_user_list_{page+1}", "style": "primary"})
        if nav: kb.append(nav)
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "user_management", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(
            f"👥 <b>User List</b>  —  Page {page+1}/{total_pages}\n"
            f"📊 Total: <b>{total_users}</b> users\n\n"
            f"<i>Tap a user to view full profile</i>"
        ), reply_markup={"inline_keyboard": kb})

    elif data.startswith("um_view_user_"):
        target_uid = int(data.split("_")[-1])
        u_data = get_user(target_uid)
        if not u_data:
            answer_callback(call["id"], "❌ User not found!", show_alert=True)
        else:
            is_verified = True if u_data.get('total_otps', 0) > 0 else u_data.get('verified', False)
            uname = u_data.get('username')
            fname = u_data.get('first_name', '')
            uname_str = f"@{uname}" if uname else "—"
            prof_text = (
                f"➖➖➖➖➖➖➖➖\n"
                f"👤 <b>USER PROFILE</b>\n"
                f"➖➖➖➖➖➖➖➖\n"
                f"🆔 ID: <code>{target_uid}</code>\n"
                f"📝 Name: {fname or '—'}\n"
                f"🔗 Username: {uname_str}\n"
                f"💰 Balance: <b>{u_data.get('balance', 0.0):.2f}</b>\n"
                f"🤝 Total Refers: {u_data.get('total_refers', 0)}\n"
                f"🔐 Total OTPs: {u_data.get('total_otps', 0)}\n"
                f"✅ Verified: {is_verified}\n"
                f"🚫 Banned: {bool(u_data.get('banned', False))}\n"
                f"➖➖➖➖➖➖➖➖"
            )
            is_banned = bool(u_data.get('banned', False))
            if is_banned:
                ban_btn_text = "✅ Unban User"
                ban_btn_style = "success"
                ban_btn_icon = "5352694861990501856"
            else:
                ban_btn_text = "🚫 Ban User"
                ban_btn_style = "danger"
                ban_btn_icon = "5334807341109908955"
            kb = {"inline_keyboard": [
                [{"text": ban_btn_text, "icon_custom_emoji_id": ban_btn_icon, "callback_data": f"um_ban_{target_uid}", "style": ban_btn_style},
                 {"text": "💰 Edit Balance", "icon_custom_emoji_id": "5190576863226933563", "callback_data": f"um_editbal_{target_uid}", "style": "primary"}],
                [{"text": "◀ Back to List", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "um_user_list_0", "style": "primary"}]
            ]}
            edit_message(chat_id, msg_id, render_body_text(prof_text), reply_markup=kb)

    elif data.startswith("um_ban_"):
        target_uid = int(data.split("_")[-1])
        u_data = get_user(target_uid)
        current_status = u_data.get("banned", False)
        new_status = not current_status
        with db_lock:
            conn = get_db_conn()
            conn.execute("UPDATE users SET banned=? WHERE user_id=?", (1 if new_status else 0, target_uid))
            conn.commit()
            conn.close()
        if target_uid in user_cache: user_cache[target_uid]["banned"] = new_status
        user_banned_cache[target_uid] = {'banned': new_status, 'time': time.time()}
        answer_callback(call["id"], "🚫 User Banned!" if new_status else "✅ User Unbanned!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"um_view_user_{target_uid}", "id": "internal"})

    elif data.startswith("um_editbal_"):
        target_uid = int(data.split("_")[-1])
        u_data = get_user(target_uid)
        user_states[chat_id] = "wait_for_um_edit_bal"
        temp_data[chat_id] = {"msg_id": msg_id, "target_uid": target_uid}
        edit_message(chat_id, msg_id, render_body_text(
            f"💰 <b>Edit Balance</b>\n\n"
            f"🆔 User: <code>{target_uid}</code>\n"
            f"💳 Current Balance: <b>{u_data.get('balance', 0.0):.2f} USDT</b>\n\n"
            f"📝 Send new balance (e.g. <code>10.5</code>)\n"
            f"Or add/deduct (e.g. <code>+5</code> or <code>-3</code>):"
        ), reply_markup={"inline_keyboard": [[{"text": "❌ Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"um_view_user_{target_uid}", "style": "danger"}]]})

    # --- Database Management ---
    elif data == "database_management":
        if not is_admin(chat_id):
            answer_callback(call["id"], "🚫 Admins only!", show_alert=True)
            return
        with db_lock:
            _conn_tmp = get_db_conn()
            _ucnt = _conn_tmp.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            _conn_tmp.close()
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['file']} <b>DATABASE MANAGEMENT</b>\n"
            f"— — — — — — — — — —\n"
            f"{PEM['user']} Total Users: <b>{_ucnt}</b>\n"
            f"{PEM['ok']} DB Path: <code>{DB_PATH}</code>\n"
            f"— — — — — — — — — —\n"
            f"<i>Download: Get the real database file.\n"
            f"Upload: Replace the current database with a new one.</i>"
        ), reply_markup=database_management_keyboard())

    elif data == "dl_database":
        if not is_admin(chat_id):
            answer_callback(call["id"], "🚫 Admins only!", show_alert=True)
            return
        try:
            save_local_db()
            with open(DB_PATH, "rb") as _dbf:
                _db_bytes = _dbf.read()
            requests.post(f"{BASE_URL}/sendDocument",
                data={"chat_id": chat_id, "caption": "✅ Bot Database — Real file", "parse_mode": "HTML"},
                files={'document': ('bot_database.db', _db_bytes)})
            answer_callback(call["id"], "✅ Downloading database...")
        except Exception as e:
            answer_callback(call["id"], f"❌ Error: {e}", show_alert=True)

    elif data == "upload_database":
        if not is_admin(chat_id):
            answer_callback(call["id"], "🚫 Admins only!", show_alert=True)
            return
        user_states[chat_id] = "wait_for_db_upload"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['upload']} <b>Upload Database</b>\n\n"
            f"📂 Send your <b>.db</b> file.\n"
            f"⚠️ <b>Warning:</b> This will replace the current database!"
        ), reply_markup={"inline_keyboard": [[{"text": "❌ Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "database_management", "style": "danger"}]]})

    elif data == "profile_withdraw":
        if not bot_settings["withdraw_on"]:
            answer_callback(call["id"], "❌ Withdrawals are currently disabled.", show_alert=True)
            return
        u_data = get_user(chat_id)
        bal = round(u_data.get('balance', 0.0), 4)
        min_w = bot_settings['min_withdraw']
        if not bot_settings["w_methods"]:
            answer_callback(call["id"], "❌ No withdrawal methods configured yet.", show_alert=True)
            return
        w_txt = (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"《 {PEM['money']} WITHDRAWAL 》\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['money']} <b>Balance:</b> {bal} USDT\n"
            f"{PEM['lock']} <b>Minimum:</b> {min_w} USDT\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['pin']} <b>Select Withdrawal Method:</b>"
        )
        kb = []
        for m in bot_settings["w_methods"]:
            emoji_id = get_payment_emoji_id(m.strip())
            kb.append([{"text": m.strip(), "icon_custom_emoji_id": emoji_id, "callback_data": f"sel_wm_{m.strip()}", "style": "primary"}])
        kb.append([{"text": "Cancel", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(w_txt), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("sel_wm_"):
        method = data.replace("sel_wm_", "")
        bal = get_user(chat_id).get('balance', 0.0)
        min_w = bot_settings['min_withdraw']
        
        if bal < min_w:
            answer_callback(call["id"], f"❌ Minimum withdrawal: {min_w} USDT\n💰 Balance: {bal} USDT", show_alert=True)
            return
            
        temp_data[chat_id] = {"method": method, "balance": bal, "msg_id": msg_id}
        user_states[chat_id] = "wait_for_withdraw_amount"
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} Method: {method}\n💰 Available Balance: {bal} USDT\n\n📝 Enter the amount you want to withdraw (Min: {min_w} USDT):"), reply_markup=get_cancel_kb())
        answer_callback(call["id"])

    elif data == "test_message_flow":
        user_states[chat_id] = "wait_for_test_service"
        temp_data[chat_id] = {}
        edit_message(chat_id, msg_id, render_body_text("🧪 <b>Test Mode</b>\n\n📝 Send the Service Name (e.g., IG):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]]})

    elif data == "manage_emojis":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['star']} <b>Premium Emoji Management</b>\n\nUpload your TXT files or manually add them below:"), reply_markup=emoji_settings_keyboard())

    elif data == "up_flags_txt":
        user_states[chat_id] = "wait_for_flag_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Flag Emojis</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "up_apps_txt":
        user_states[chat_id] = "wait_for_app_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the <b>Service Apps</b> <code>.txt</code> file."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "add_single_emoji":
        user_states[chat_id] = "wait_for_emoji_extract"
        edit_message(chat_id, msg_id, render_body_text("📝   Premium Emoji   (: 🇧🇩  🚫):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_emojis", "style": "danger"}]]})

    elif data == "dl_flags_txt":
        content = generate_emoji_txt("flags")
        if content:
            send_document(chat_id, "Flag_Emojis.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No Flag Emojis found!", show_alert=True)

    elif data == "dl_apps_txt":
        content = generate_emoji_txt("apps")
        if content:
            send_document(chat_id, "Service_Apps.txt", content)
            answer_callback(call["id"], "✅ Downloaded!")
        else:
            answer_callback(call["id"], "❌ No App Emojis found!", show_alert=True)

    elif data == "del_all_flags":
        bot_settings["premium_flags"] = {}
        save_db()
        answer_callback(call["id"], "✅ All Premium Flags Deleted Successfully!", show_alert=True)

    elif data == "broadcast_msg":
        user_states[chat_id] = "wait_for_broadcast"
        edit_message(chat_id, msg_id, render_body_text("📢 <b>Broadcast Mode</b>\n\nSend the message you want to broadcast (Text, Photo, Video, File etc)."), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "upload_num":
        user_states[chat_id] = "wait_for_txt"
        edit_message(chat_id, msg_id, render_body_text("📂 Please upload the numbers in a <b>.txt</b> file."), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]})

    elif data == "delete_files":
        kb = []
        apps_db = bot_settings.get("premium_apps", {})
        flags_db = bot_settings.get("premium_flags", {})
        for b_id, b_data in number_batches.items():
            service = b_data.get("service", "UNKNOWN")
            country = b_data.get("country", "UNKNOWN")
            count = len(b_data.get("numbers", []))

            service_char = "📱"
            service_id = "5352694861990501856"
            for app_key, app_data in apps_db.items():
                if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                    service_char = app_data.get("char", "📱")
                    if "id" in app_data:
                        service_id = app_data["id"]
                    break

            flag_char = "🏳️"
            country_name = country
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if country == flag_code or _country_code_matches(country, iso, name):
                    flag_char = flag_data.get("char", "🏳️")
                    country_name = flag_data.get("name", country)
                    break

            btn_text = f"({country_name}) — {count}"
            kb.append([{"text": btn_text, "icon_custom_emoji_id": service_id, "callback_data": f"del_b_{b_id}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "primary"}])
        txt = "🗑 Select a stock to delete:" if len(kb) > 1 else f"{PEM['no']} No files found."
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_b_"):
        b_id = data.split("del_b_")[1]
        if b_id in number_batches:
            b_removed = number_batches[b_id]
            _fs_remove_file_for(b_removed.get("service", "UNKNOWN"), b_removed.get("country", "UNKNOWN"))
            del number_batches[b_id]
            save_db()
            answer_callback(call["id"], "✅ File deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "delete_files", "id": call["id"]})

    elif data == "show_used":
        kb = {"inline_keyboard": [
            [{"text": "Download Used Numbers", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dl_used", "style": "primary"}],
            [{"text": "Add Used Numbers", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "restock_used", "style": "success"}],
            [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>Total Used Numbers:</b> {len(used_numbers_list)}"), reply_markup=kb)

    elif data == "dl_used":
        if not used_numbers_list:
            answer_callback(call["id"], "❌ No used numbers to download!", show_alert=True)
            return
        groups = {}
        for entry in used_numbers_list:
            if isinstance(entry, dict):
                num = entry.get("num")
                service = entry.get("service") or "UNKNOWN"
                country = entry.get("country") or "UNKNOWN"
            else:
                num, service, country = entry, "UNKNOWN", "UNKNOWN"
            if not num:
                continue
            groups.setdefault((service, country), []).append(str(num))
        sent = 0
        for (service, country), nums in groups.items():
            fname = f"{_fs_sanitize(country)}_{_fs_sanitize(service)}_used.txt"
            content = "\n".join(nums).encode('utf-8')
            send_document(chat_id, fname, content)
            sent += 1
        answer_callback(call["id"], f"✅ Sent {sent} file(s), separated by service &amp; country.", show_alert=True)

    elif data == "restock_used":
        if not used_numbers_list:
            answer_callback(call["id"], "❌ No used numbers to restock!", show_alert=True)
            return
        restocked = 0
        for entry in list(used_numbers_list):
            if isinstance(entry, dict):
                num, service, country = entry.get("num"), entry.get("service", "UNKNOWN"), entry.get("country", "UNKNOWN")
            else:
                # Legacy plain-string entries (no service/country info) — restock as UNKNOWN.
                num, service, country = entry, "UNKNOWN", "UNKNOWN"
            if not num:
                continue
            target_b_id = None
            for b_id, b_data in number_batches.items():
                if b_data.get("service") == service and b_data.get("country") == country:
                    target_b_id = b_id
                    break
            if not target_b_id:
                target_b_id = _fs_batch_id(service, country)
                if target_b_id not in number_batches:
                    number_batches[target_b_id] = {"filename": "restocked_used_numbers.txt", "service": service, "country": country, "numbers": []}
            number_batches[target_b_id]["numbers"].append({"num": num, "shares": 0, "used_by": []})
            restocked += 1
            _fs_sync_batch(target_b_id)
        used_numbers_list.clear()
        save_db()
        kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['ok']} <b>{restocked}</b> used number(s) added back to stock!"), reply_markup=kb)
        answer_callback(call["id"])

    elif data == "show_unused":
        unused_count = sum(len(b["numbers"]) for b in number_batches.values())
        kb = {"inline_keyboard": [[{"text": "Download TXT", "icon_custom_emoji_id": "5257969839313526622", "callback_data": "dlu_svc", "style": "primary"}], [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['rocket']} <b>Total Unused Numbers:</b> {unused_count}"), reply_markup=kb)

    elif data == "dlu_svc":
        services = sorted(set(b["service"] for b in number_batches.values() if b.get("numbers")))
        if not services:
            answer_callback(call["id"], "❌ No unused numbers available!", show_alert=True)
            return
        apps_db = bot_settings.get("premium_apps", {})
        kb = []
        for s in services:
            emoji_id = "5352694861990501856"
            for app_key, app_data in apps_db.items():
                if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            svc_count = sum(len(b["numbers"]) for b in number_batches.values() if b.get("service") == s)
            kb.append([{"text": f"{s} ({svc_count})", "icon_custom_emoji_id": emoji_id, "callback_data": f"dlu_cty_{s}", "style": "primary"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "show_unused", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['pin']} <b>Download Unused Numbers</b>\n\nSelect the service:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("dlu_cty_"):
        service = data[len("dlu_cty_"):]
        countries = sorted(set(b["country"] for b in number_batches.values() if b["service"] == service and b.get("numbers")))
        if not countries:
            answer_callback(call["id"], "❌ No unused numbers found for this service.", show_alert=True)
            return
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in countries:
            emoji_id = "5780471598922337683"
            display_name = c
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c == flag_code or _country_code_matches(c, iso, name):
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        display_name = flag_data.get("name", c)
                        break
            c_count = sum(len(b["numbers"]) for b in number_batches.values() if b.get("service") == service and b.get("country") == c)
            kb.append([{"text": f"{display_name} ({c_count})", "icon_custom_emoji_id": emoji_id, "callback_data": f"dlu_go_{service}||{c}", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dlu_svc", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['pin']} <b>{service}</b>\n\nSelect the country:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("dlu_go_"):
        payload = data[len("dlu_go_"):]
        service, country = payload.split("||", 1) if "||" in payload else (payload, "UNKNOWN")
        nums = [n["num"] for b in number_batches.values() if b.get("service") == service and b.get("country") == country for n in b.get("numbers", [])]
        if not nums:
            answer_callback(call["id"], "❌ No unused numbers found for this selection.", show_alert=True)
            return
        fname = f"{_fs_sanitize(country)}_{_fs_sanitize(service)}_unused.txt"
        content = "\n".join(nums).encode('utf-8')
        send_document(chat_id, fname, content)
        answer_callback(call["id"], f"✅ Sent {len(nums)} number(s).", show_alert=True)

    elif data == "view_stock":
        services = {}
        for b_data in number_batches.values():
            svc = b_data.get("service", "UNKNOWN")
            services[svc] = services.get(svc, 0) + len(b_data.get("numbers", []))
        if not services:
            txt = f"{PEM['no']} No stock available. Upload numbers first."
        else:
            lines = [f"━━━━━━━━━━━━━━━━━━", f"《 {PEM['graph']} <b>STOCK OVERVIEW</b> 》", "━━━━━━━━━━━━━━━━━━"]
            apps_db = bot_settings.get("premium_apps", {})
            for svc, count in sorted(services.items(), key=lambda x: -x[1]):
                app_full_name, srv_html = get_service_info_html(svc)
                lines.append(f"{srv_html} <b>{svc}</b> — <code>{count}</code> pending")
            lines.append("━━━━━━━━━━━━━━━━━━")
            lines.append(f"{PEM['num']} <b>Total:</b> <code>{sum(services.values())}</code> number(s)")
            txt = "\n".join(lines)
        kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]]}
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data == "update_num":
        services = sorted(set(b["service"] for b in number_batches.values()))
        if not services:
            answer_callback(call["id"], "❌ No existing services found. Use 'Upload Number' first to create one.", show_alert=True)
            return
        apps_db = bot_settings.get("premium_apps", {})
        kb = []
        for s in services:
            emoji_id = "5352694861990501856"
            for app_key, app_data in apps_db.items():
                if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": s, "icon_custom_emoji_id": emoji_id, "callback_data": f"upd_svc_{s}", "style": "primary"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['pin']} <b>Update Number</b>\n\nSelect the service to add numbers to:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("upd_svc_"):
        service = data[len("upd_svc_"):]
        countries = sorted(set(b["country"] for b in number_batches.values() if b["service"] == service))
        if not countries:
            answer_callback(call["id"], "❌ No countries found for this service.", show_alert=True)
            return
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in countries:
            emoji_id = "5780471598922337683"
            display_name = c
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c == flag_code or _country_code_matches(c, iso, name):
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        display_name = flag_data.get("name", c)
                        break
            kb.append([{"text": display_name, "icon_custom_emoji_id": emoji_id, "callback_data": f"upd_cty_{service}||{c}", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "update_num", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['pin']} <b>{service}</b>\n\nSelect the country to add numbers to:"), reply_markup={"inline_keyboard": kb})
        answer_callback(call["id"])

    elif data.startswith("upd_cty_"):
        payload = data[len("upd_cty_"):]
        service, country = payload.split("||", 1) if "||" in payload else (payload, "UNKNOWN")
        temp_data[chat_id] = {"upd_service": service, "upd_country": country}
        user_states[chat_id] = "wait_for_upd_txt"
        country_name, flag_html = _flag_display(country)
        edit_message(chat_id, msg_id, render_body_text(
            f"{PEM['pin']} <b>{service}</b> / {flag_html} <b>{country_name}</b>\n\n"
            f"📂 Please upload the numbers in a <b>.txt</b> file.\n"
            f"Duplicate numbers already in stock will be skipped automatically."
        ), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "update_num", "style": "danger"}]]})
        answer_callback(call["id"])

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                with db_lock:
                    conn = get_db_conn()
                    rows = conn.execute(f"SELECT user_id, {field} FROM users WHERE {field}>0 ORDER BY {field} DESC LIMIT {limit}").fetchall()
                    conn.close()
                res_txt = ""
                count = 1
                for row in rows:
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={row[0]}'>{row[0]}</a> ➔ <b>{row[1]}</b>\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                with db_lock:
                    conn = get_db_conn()
                    rows = conn.execute(f"SELECT user_id, {field} FROM users WHERE {field}>0 ORDER BY {field} DESC LIMIT {limit}").fetchall()
                    conn.close()
                res_txt = ""
                count = 1
                for row in rows:
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={row[0]}'>{row[0]}</a> ➔ <b>{row[1]}</b>\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                with db_lock:
                    conn = get_db_conn()
                    ws = conn.execute("SELECT user_id, amount, status FROM withdrawals ORDER BY timestamp DESC LIMIT 10").fetchall()
                    conn.close()
                res_txt = ""
                count = 1
                for w in ws:
                    s = str(w[2]).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={w[0]}'>{w[0]}</a> ➔ <b>{w[1]}</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "lb_main":
        txt = f"━━━━━━━━━━━━━━━\n《 {PEM['admin']} <b>LEADER BOARD MENU</b> 》\n━━━━━━━━━━━━━━━\n<i>Select a category to view the top performers or history.</i>\n━━━━━━━━━━━━━━━"
        kb = [
            [{"text": "Top Referrers", "icon_custom_emoji_id": "5420145051336485498", "callback_data": "lb_top_refs", "style": "primary"}],
            [{"text": "Top OTP Receivers", "icon_custom_emoji_id": "5353001161878182134", "callback_data": "lb_top_otps", "style": "primary"}],
            [{"text": "Withdrawal History", "icon_custom_emoji_id": "5348469219761626211", "callback_data": "lb_w_history", "style": "success"}],
            [{"text": "Back to Admin", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "back_to_admin", "style": "danger"}]
        ]
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("lb_"):
        sub = data.replace("lb_", "")
        edit_message(chat_id, msg_id, render_body_text("⌛ <i>Fetching Data...</i>"))
        
        num_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣", "6": "6️⃣", "7": "7️⃣", "8": "8️⃣", "9": "9️⃣", "0": "0️⃣"}
        def get_p_num(n): return "".join([num_map.get(c, c) for c in str(n)])
        
        try:
            if sub == "top_refs":
                title, field, limit, icon = "TOP 5 REFERRERS", "total_refers", 5, PEM.get('user', '👥')
                with db_lock:
                    conn = get_db_conn()
                    rows = conn.execute(f"SELECT user_id, {field} FROM users WHERE {field}>0 ORDER BY {field} DESC LIMIT {limit}").fetchall()
                    conn.close()
                res_txt = ""
                count = 1
                for row in rows:
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={row[0]}'>{row[0]}</a> ➔ <b>{row[1]}</b>\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "top_otps":
                title, field, limit, icon = "TOP 5 OTP RECEIVERS", "total_otps", 5, PEM.get('msg', '📩')
                with db_lock:
                    conn = get_db_conn()
                    rows = conn.execute(f"SELECT user_id, {field} FROM users WHERE {field}>0 ORDER BY {field} DESC LIMIT {limit}").fetchall()
                    conn.close()
                res_txt = ""
                count = 1
                for row in rows:
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={row[0]}'>{row[0]}</a> ➔ <b>{row[1]}</b>\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No data found.</i>\n"

            elif sub == "w_history":
                title, limit, icon = "LAST 10 WITHDRAWALS", 10, PEM.get('money', '💸')
                with db_lock:
                    conn = get_db_conn()
                    ws = conn.execute("SELECT user_id, amount, status FROM withdrawals ORDER BY timestamp DESC LIMIT 10").fetchall()
                    conn.close()
                res_txt = ""
                count = 1
                for w in ws:
                    s = str(w[2]).lower()
                    stat_icon = PEM.get('ok','✅') if s in ["approved","success"] else PEM.get('no','❌') if s=="rejected" else "⏳"
                    p = "└" if count == limit else "├"
                    res_txt += f"{p} {get_p_num(count)} <a href='tg://user?id={w[0]}'>{w[0]}</a> ➔ <b>{w[1]}</b> {stat_icon}\n"
                    count += 1
                if not res_txt: res_txt = "└ <i>No history found.</i>\n"

            final_msg = f"━━━━━━━━━━━━━━━\n{icon} <b>{title}</b>\n━━━━━━━━━━━━━━━\n{res_txt}━━━━━━━━━━━━━━━"
            kb = [[{"text": "Refresh", "icon_custom_emoji_id": "5420155432272438703", "callback_data": data, "style": "success"}, {"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]
            edit_message(chat_id, msg_id, render_body_text(final_msg), reply_markup={"inline_keyboard": kb})

        except Exception as e:
            edit_message(chat_id, msg_id, render_body_text(f"❌ Error: {e}"), reply_markup={"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "lb_main", "style": "danger"}]]})

    elif data == "back_to_admin":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, get_admin_text(), reply_markup=admin_panel_keyboard())
        
    elif data == "system_settings":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['gear']} <b>System Settings</b>\nManage advanced bot configurations below:"), reply_markup=system_settings_keyboard())


    elif data == "voltx_control":
        edit_message(chat_id, msg_id, render_body_text(f"⚡ <b>Voltx Control Panel</b>\n\nTotal API Keys: {len(bot_settings.get('voltx_keys', []))}\nManage your Voltx API Keys below:"), reply_markup=voltx_control_keyboard())

    elif data == "add_voltx_key":
        user_states[chat_id] = "wait_for_add_voltx_key"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new Voltx API Key:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}]]})

    elif data == "view_voltx_keys":
        kb = []
        for idx, key in enumerate(bot_settings.get("voltx_keys", [])):
            safe_name = key[:10] + "..." if len(key)>10 else key
            kb.append([{"text": f"Delete {safe_name}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vtx_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🗑 <b>Select Voltx Key to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("del_vtx_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_keys", [])):
            del bot_settings["voltx_keys"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Key Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "view_voltx_keys", "id": call["id"]})

    elif data == "voltx_search_country":
        kb = []
        for idx, c in enumerate(bot_settings.get("voltx_search_countries", [])):
            kb.append([{"text": f"Delete {c}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"del_vsc_{idx}", "style": "danger"}])
        kb.append([{"text": "Add Country Code", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "add_voltx_search_country", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text("🌍 <b>Voltx Allowed Ranges:</b>\nOnly these ranges/codes will be allowed in Voltx Number Lookup."), reply_markup={"inline_keyboard": kb})

    elif data == "add_voltx_search_country":
        user_states[chat_id] = "wait_for_add_vsc"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Voltx Range Code (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_search_country", "style": "danger"}]]})

    elif data.startswith("del_vsc_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings.get("voltx_search_countries", [])):
            del bot_settings["voltx_search_countries"][idx]
            save_db()
            answer_callback(call["id"], "✅ Voltx Range Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "voltx_search_country", "id": call["id"]})

    elif data == "manage_voltx_srv":
        kb = []
        srvs = bot_settings.get("voltx_services", {})
        apps_db = bot_settings.get("premium_apps", {})
        for srv in srvs:
            emoji_id = "5257969839313526622"
            for app_key, app_data in apps_db.items():
                if srv.upper() == app_key or srv.upper() in app_key or app_key in srv.upper():
                    if "id" in app_data: emoji_id = app_data["id"]; break
            kb.append([{"text": f"{srv}", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        kb.append([{"text": "Add New Service", "icon_custom_emoji_id": "5420323438508155202", "callback_data": "vx_add_srv", "style": "success"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "voltx_control", "style": "danger"}])
        edit_message(chat_id, msg_id, render_body_text("⚡ <b>Voltx Services Manager</b>\nManage your API-based dynamic services below:"), reply_markup={"inline_keyboard": kb})

    elif data == "vx_add_srv":
        user_states[chat_id] = "wait_vx_srv_name"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Enter Service Name (e.g. TELEGRAM):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_srv_"):
        srv = data.replace("vx_srv_", "")
        kb = []
        countries = bot_settings["voltx_services"].get(srv, {})
        flags_db = bot_settings.get("premium_flags", {})
        for c in countries:
            emoji_id = "5780471598922337683"
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if _country_code_matches(c, iso, name):
                    if "id" in flag_data: emoji_id = flag_data["id"]; break
            kb.append([{"text": f"{c} ({len(countries[c])} Ranges)", "icon_custom_emoji_id": emoji_id, "callback_data": f"vx_cnt_{srv}_{c}", "style": "primary"}])
        kb.append([{"text": "Add Country", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_add_cnt_{srv}", "style": "success"}])
        kb.append([{"text": "Delete Service", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_srv_{srv}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_voltx_srv", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"📂 <b>Service: {srv}</b>\nManage countries for this service:"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_add_cnt_"):
        srv = data.replace("vx_add_cnt_", "")
        user_states[chat_id] = "wait_vx_cnt_name"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv}
        edit_message(chat_id, msg_id, render_body_text(f"🌍 Enter Country Name for <b>{srv}</b> (e.g. BD, INDIA):"), reply_markup=get_cancel_kb())

    elif data.startswith("vx_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        ranges = bot_settings["voltx_services"][srv].get(cnt, [])
        kb = []
        row = []
        for r in ranges:
            row.append({"text": f"Delete {r}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"vx_dr_{srv}_{cnt}_{r}", "style": "danger"})
            if len(row) == 2:
                kb.append(row)
                row = []
        if row: kb.append(row)
        kb.append([{"text": "Add Range", "icon_custom_emoji_id": "5420323438508155202", "callback_data": f"vx_addr_{srv}_{cnt}", "style": "success"}])
        kb.append([{"text": "Delete Entire Country", "icon_custom_emoji_id": "5422557736330106570", "callback_data": f"vx_del_cnt_{srv}_{cnt}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_srv_{srv}", "style": "primary"}])
        txt = f"📍 <b>Service: {srv} | Country: {cnt}</b>\n\n<b>Total Ranges:</b> {len(ranges)}\n<i>Click on a range below to delete it, or add a new one.</i>"
        edit_message(chat_id, msg_id, render_body_text(txt), reply_markup={"inline_keyboard": kb})

    elif data.startswith("vx_addr_"):
        parts = data.split("_")
        srv, cnt = parts[2], parts[3]
        user_states[chat_id] = "wait_vx_addr"
        temp_data[chat_id] = {"msg_id": msg_id, "srv": srv, "cnt": cnt}
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the new Range for <b>{cnt}</b> (e.g. 26134):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"vx_cnt_{srv}_{cnt}", "style": "danger"}]]})

    elif data.startswith("vx_dr_"):
        parts = data.split("_")
        srv, cnt, rng = parts[2], parts[3], parts[4]
        if rng in bot_settings["voltx_services"].get(srv, {}).get(cnt, []):
            bot_settings["voltx_services"][srv][cnt].remove(rng)
            save_db()
            answer_callback(call["id"], f"✅ Range {rng} deleted!", show_alert=True)
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_cnt_{srv}_{cnt}", "id": call["id"]})

    elif data.startswith("vx_del_srv_"):
        srv = data.replace("vx_del_srv_", "")
        if srv in bot_settings["voltx_services"]: del bot_settings["voltx_services"][srv]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": "manage_voltx_srv", "id": call["id"]})

    elif data.startswith("vx_del_cnt_"):
        parts = data.split("_")
        srv, cnt = parts[3], parts[4]
        if cnt in bot_settings["voltx_services"].get(srv, {}): del bot_settings["voltx_services"][srv][cnt]
        save_db()
        handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"vx_srv_{srv}", "id": call["id"]})

    elif data == "manage_fj":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "toggle_fj":
        bot_settings["fj_on"] = not bot_settings["fj_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "add_fj":
        user_states[chat_id] = "wait_for_add_fj"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Channel Username or Invite Link:\n<i>(Note: For private channels, use the numeric ID like -100...)</i>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_fj", "style": "danger"}]]})

    elif data.startswith("del_fj_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fj_channels"]):
            del bot_settings["fj_channels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Channel deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['link']} <b>FORCE JOIN SYSTEM</b>\nManage channels below:"), reply_markup=fj_settings_keyboard())

    elif data == "manage_admins":
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "add_adm":
        user_states[chat_id] = "wait_for_add_adm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the User ID of the new Admin:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_admins", "style": "danger"}]]})

    elif data.startswith("del_adm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["admins"]):
            del bot_settings["admins"][idx]
            save_db()
            answer_callback(call["id"], "✅ Admin deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text(f"{PEM['user']} <b>ADMIN MANAGEMENT</b>\nManage your bot admins below:"), reply_markup=admin_settings_keyboard())

    elif data == "manage_otp_groups":
        edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "add_fw":
        user_states[chat_id] = "wait_for_add_fw_id"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Group ID/Username to forward messages to:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data.startswith("manage_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            grp = bot_settings["fw_groups"][idx]
            grp_label = grp.get("name") or grp["chat_id"]
            edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_label}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("add_fwbtn_"):
        idx = int(data.split("_")[2])
        user_states[chat_id] = "wait_for_add_fw_btn"
        temp_data[chat_id] = {"msg_id": msg_id, "fw_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send Custom Inline Button format:\n<code>Button Text - https://link.com</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_fw_{idx}", "style": "danger"}]]})

    elif data.startswith("del_fwbtn_"):
        parts = data.split("_")
        idx, b_idx = int(parts[2]), int(parts[3])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            if 0 <= b_idx < len(bot_settings["fw_groups"][idx]["buttons"]):
                del bot_settings["fw_groups"][idx]["buttons"][b_idx]
                save_db()
                answer_callback(call["id"], "✅ Button deleted!", show_alert=True)
                grp_lbl = bot_settings['fw_groups'][idx].get("name") or bot_settings['fw_groups'][idx]['chat_id']
                edit_message(chat_id, msg_id, render_body_text(f"🛡 <b>Manage Group:</b> {grp_lbl}"), reply_markup=specific_fw_group_keyboard(idx))

    elif data.startswith("del_fw_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["fw_groups"]):
            del bot_settings["fw_groups"][idx]
            save_db()
            answer_callback(call["id"], "✅ Group deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("🛡 <b>OTP GROUP MANAGEMENT</b>\nManage settings below:"), reply_markup=otp_groups_list_keyboard())

    elif data == "edit_otp_link":
        user_states[chat_id] = "wait_for_otp_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the new OTP Group Link:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "edit_fw_channel_link":
        user_states[chat_id] = "wait_for_fw_channel_link"
        temp_data[chat_id] = {"msg_id": msg_id}
        cur = bot_settings.get("fw_channel_link", "") or "Not set"
        edit_message(chat_id, msg_id, render_body_text(f"📝 Send the Channel link for OTP forward message:\n\nCurrent: <code>{cur}</code>"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275166", "callback_data": "manage_otp_groups", "style": "danger"}]]})

    elif data == "manage_panels":
        api_count = len([p for p in bot_settings["panels"] if p.get("type") == "API Panel"])
        cpt_count = len([p for p in bot_settings["panels"] if p.get("type", "API Panel") == "Auto Captcha Panel"])
        text = f"{PEM['gear']} <b>Panel Management</b>\n\nSelect which type of panel system you want to manage:"
        kb = {"inline_keyboard": [
            [{"text": f"Manage API Panels ({api_count})", "icon_custom_emoji_id": "5336972142066047577", "callback_data": "manage_api_panels", "style": "primary"}],
            [{"text": f"Manage Auto Captcha Panels ({cpt_count})", "icon_custom_emoji_id": "5353022963132174959", "callback_data": "manage_cpt_panels", "style": "success"}],
            [{"text": "Back to System", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "system_settings", "style": "danger"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=kb)

    elif data in ["manage_api_panels", "manage_cpt_panels"]:
        p_type = "API Panel" if data == "manage_api_panels" else "Auto Captcha Panel"
        p_list = [p for p in bot_settings["panels"] if p.get("type", "API Panel") == p_type]
        icon = f"{PEM['world']} API" if p_type == 'API Panel' else f"{PEM['lock']} Auto Captcha"
        
        text = f"{icon} <b>{p_type}s Management</b>\n\n👀 <b>Active Monitors:</b> {len(p_list)}\n\n🟢 <b>Available Providers:</b>\n"
        for p in p_list:
            status = "Monitoring" if p['status'] == 'ON' else "Stopped"
            login_state = p.get('login_status', '')
            if p['type'] == 'Auto Captcha Panel':
                conf = f" {login_state}" if login_state else f"{PEM['ok']} Configured"
            else:
                conf = f"{PEM['ok']} Configured" if p.get('api_url') else f"{PEM['no']} Not Configured"
            text += f"• {p['name']}: {PEM['ok'] if p['status']=='ON' else PEM['no']} {status} | {conf}\n"
        edit_message(chat_id, msg_id, render_body_text(text), reply_markup=typed_panels_list_keyboard(p_type))

    elif data in ["add_api_panel", "add_cpt_panel"]:
        user_states[chat_id] = "wait_for_panel_name"
        p_type = "api" if data == "add_api_panel" else "logc"
        temp_data[chat_id] = {"msg_id": msg_id, "add_type": p_type}
        edit_message(chat_id, msg_id, render_body_text("📝 Please send the name of the New Provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='api' else 'cpt'}_panels", "style": "danger"}]]})

    elif data.startswith("add_ptype_"):
        pass

    elif data in ["list_del_api", "list_del_cpt"]:
        p_type = "API Panel" if data == "list_del_api" else "Auto Captcha Panel"
        kb = []
        for idx, p in enumerate(bot_settings["panels"]):
            if p.get("type", "API Panel") == p_type:
                kb.append([{"text": f"Delete {p['name']}", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"do_del_pnl_{idx}", "style": "danger"}])
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "style": "primary"}])
        edit_message(chat_id, msg_id, render_body_text(f"{PEM['trash']} <b>Select a Provider to Delete:</b>"), reply_markup={"inline_keyboard": kb})

    elif data.startswith("do_del_pnl_"):
        idx = int(data.split("_")[3])
        if 0 <= idx < len(bot_settings["panels"]):
            p_type = bot_settings["panels"][idx].get("type", "API Panel")
            del bot_settings["panels"][idx]
            save_db()
            answer_callback(call["id"], "✅ Provider Deleted!", show_alert=True)
            handle_callback({"message": {"chat": {"id": chat_id}, "message_id": msg_id}, "data": f"manage_{'api' if p_type=='API Panel' else 'cpt'}_panels", "id": "internal"})

    elif data.startswith("tog_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            
            p["status"] = "ON" if p["status"] == "OFF" else "OFF"
            save_db()
            
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("conf_pnl_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["panels"]):
            p = bot_settings["panels"][idx]
            if p["type"] == "Auto Captcha Panel":
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>Login Status:</b> {p.get('login_status', 'Unknown')}\n<b>Login URL:</b> <code>{p.get('login_url', 'None')}</code>\n<b>User:</b> <code>{p.get('username', 'None')}</code>\n<b>Num Col:</b> {p.get('num_col_name')} (Idx: {p.get('num_col_idx')})\n<b>Msg Col:</b> {p.get('msg_col_name')} (Idx: {p.get('msg_col_idx')})"
            else:
                text = f"⚙️ <b>Configure {p['name']}</b>\n\n<b>Type:</b> {p['type']}\n<b>Status:</b> {'🟢 Monitoring' if p['status'] == 'ON' else '🔴 Stopped'}\n<b>API URL:</b> <code>{p.get('api_url', 'None')}</code>\n<b>Token:</b> <code>{p.get('token', 'None')}</code>\n<b>Full API URL:</b> <code>{p.get('full_api_url', 'None')}</code>"
            edit_message(chat_id, msg_id, render_body_text(text), reply_markup=panel_config_keyboard(idx))

    elif data.startswith("set_p_api_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_api"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the API URL for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_tok_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_tok"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the Token for this provider:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_fapi_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_fapi"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the FULL API URL (Example: http://api.com/get?key=YOUR_TOKEN&start=0):"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("set_p_rec_"):
        idx = int(data.split("_")[3])
        user_states[chat_id] = "wait_for_p_rec"
        temp_data[chat_id] = {"msg_id": msg_id, "p_idx": idx}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the number of records to fetch (e.g. 10).\nType <code>0</code> for Unlimited:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": f"conf_pnl_{idx}", "style": "danger"}]]})

    elif data.startswith("test_p_conn_"):
        idx = int(data.split("_")[3])
        p = bot_settings["panels"][idx]
        wait_msg = send_message(chat_id, render_body_text("⏳ Testing connection. Please wait..."))
        wait_msg_id = wait_msg.get("result", {}).get("message_id") if wait_msg else None
        answer_callback(call["id"])
        
        try:
            parsed = []
            raw_text = ""
            
            if p["type"] == "Auto Captcha Panel":
                sess = panel_sessions.get(idx)
                if not sess:
                    success = attempt_auto_login(p, idx)
                    if not success:
                        if wait_msg_id: delete_message(chat_id, wait_msg_id)
                        send_message(chat_id, render_body_text(f"❌ <b>Auto Login Failed!</b>\nReason: {html.escape(str(p.get('login_status', 'Unknown')))}"))
                        return
                    sess = panel_sessions.get(idx)
                    
                login_url = p.get("login_url", "").strip()
                if not login_url.startswith("http"): login_url = "http://" + login_url
                msg_link = p.get("msg_link", "").strip()
                if not msg_link.startswith("http") and msg_link != "": msg_link = "http://" + msg_link
                check_url = msg_link if msg_link else f"{login_url.split('/login')[0]}/client/SMSCDRStats"
                
                # 🌟 test connection supports sAjaxSource & HTML table parser
                parsed, raw_text = fetch_cpt_panel_cdrs(p, sess, check_url)
                
            else:
                full_url = p.get("full_api_url", "").strip()
                url = p.get("api_url", "").strip()
                token = p.get("token", "").strip()
                if not full_url and not url:
                    if wait_msg_id: delete_message(chat_id, wait_msg_id)
                    send_message(chat_id, render_body_text("❌ Please Set API URL or Full API URL first!"))
                    return
                
                urls_to_try = []
                if full_url:
                    urls_to_try.append(full_url)
                else:
                    if "{token}" in url or "{key}" in url:
                        urls_to_try.append(url.replace("{token}", token).replace("{key}", token))
                    elif "token=" in url or "key=" in url:
                        urls_to_try.append(url)
                    else:
                        sep = '&' if '?' in url else '?'
                        urls_to_try.append(f"{url}{sep}token={token}")
                        urls_to_try.append(f"{url}{sep}key={token}&start=0")
                        urls_to_try.append(f"{url}{sep}key={token}")
                    
                parsed = []
                raw_text = ""
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                for try_url in urls_to_try:
                    try:
                        res = requests.get(try_url, headers=headers, timeout=10)
                        raw_text = res.text
                        parsed = parse_panel_response(raw_text, p)
                        if parsed:
                            if not full_url and try_url != url and token:
                                p["api_url"] = try_url.replace(token, "{token}")
                                save_db()
                            break
                    except: pass
                 
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
                 
            if parsed:
                txt = f"✅ <b>Connection Successful!</b>\n\n🎯 <b>Parsed Data Sample (Max 3):</b>\n\n"
                
                for i, sample in enumerate(parsed[:3]):
                    num = sample['number']
                    msg = sample['message']
                    otp = sample['otp']
                    
                    detected_app = detect_service(msg)
                    app_name = detected_app if detected_app else p.get("name", "Unknown")
                    app_full_name, prem_app_html = get_service_info_html(app_name, msg)
                    
                    txt += f"<b>{i+1}.</b> {prem_app_html} <b>{app_full_name}</b>\n"
                    txt += f"📱 Number: <code>{num}</code>\n"
                    txt += f"📝 Full Msg: <code>{html.escape(msg)}</code>\n"
                    txt += f"🔐 OTP: <code>{otp}</code>\n"
                    txt += "➖" * 12 + "\n"
                    
                send_message(chat_id, render_body_text(txt))
            else:
                if p["type"] == "Auto Captcha Panel":
                    try:
                        soup = BeautifulSoup(raw_text, 'html.parser')
                        tables = soup.find_all('table')
                        if tables:
                            full_table_data = "🔍 FULL TABLE DATA (A-Z)\n" + "="*50 + "\n\n"
                            for t_idx, table in enumerate(tables):
                                full_table_data += f"--- Table {t_idx+1} ---\n"
                                rows = table.find_all('tr')
                                for r_idx, row in enumerate(rows):
                                    cols = row.find_all(['th', 'td'])
                                    col_texts = [f"[{c_idx+1}] {c.get_text(separator=' ', strip=True)}" for c_idx, c in enumerate(cols)]
                                    full_table_data += f"Row {r_idx+1}: {' | '.join(col_texts)}\n"
                                full_table_data += "\n" + "="*50 + "\n"
                            
                            send_document(chat_id, f"Full_Panel_Data_{idx}.txt", full_table_data.encode('utf-8'))
                            fail_txt = f"⚠️ <b>Connected, but couldn't parse OTP data!</b>\n\n<i>    (A-Z)   Text File  ।     Column Number (: [1], [3])      ।</i>"
                            send_message(chat_id, render_body_text(fail_txt))
                        else:
                            send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but no HTML Table found!</b>\nMake sure the message link is correct."))
                    except Exception as e:
                        send_message(chat_id, render_body_text(f"❌ <b>Error parsing HTML:</b> {html.escape(str(e))}"))
                else:
                    safe_html = html.escape(str(raw_text)[:300])
                    send_message(chat_id, render_body_text(f"⚠️ <b>Connected, but couldn't find/parse OTP data.</b>\n\n<i>Make sure your API config is correct.</i>\n\nRaw HTML/Data (excerpt):\n<code>{safe_html}...</code>"))
        except Exception as e:
            if wait_msg_id: delete_message(chat_id, wait_msg_id)
            send_message(chat_id, render_body_text(f"❌ <b>Connection Failed!</b>\nError: {html.escape(str(e))}"))

    elif data == "dxa_control":
        if chat_id in user_states: del user_states[chat_id]
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DEV CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "view_w_requests":
        try:
            with db_lock:
                conn = get_db_conn()
                rows = conn.execute(
                    "SELECT id, user_id, amount, method, account, status, timestamp FROM withdrawals WHERE status='pending' ORDER BY timestamp DESC LIMIT 20"
                ).fetchall()
                conn.close()
            w_requests = [tuple(r) for r in rows]
        except:
            w_requests = []
        if not w_requests:
            hdr = (
                f"━━━━━━━━━━━━━━━━━━\n"
                f"《 {PEM['money']} WITHDRAWAL REQUESTS 》\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{PEM['no']} No pending withdrawal requests.\n"
                f"━━━━━━━━━━━━━━━━━━"
            )
            kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "dxa_control", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(hdr), reply_markup=kb)
        else:
            hdr = (
                f"━━━━━━━━━━━━━━━━━━\n"
                f"《 {PEM['money']} WITHDRAWAL REQUESTS 》\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{PEM['ok']} Pending: <b>{len(w_requests)}</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"Click any request for details:"
            )
            edit_message(chat_id, msg_id, render_body_text(hdr), reply_markup=withdrawal_requests_list_keyboard(w_requests))

    elif data.startswith("wreq_detail_"):
        db_id = data.replace("wreq_detail_", "")
        try:
            with db_lock:
                conn = get_db_conn()
                row = conn.execute(
                    "SELECT id, user_id, amount, method, account, status, timestamp FROM withdrawals WHERE id=?", (db_id,)
                ).fetchone()
                conn.close()
        except:
            row = None
        if not row:
            answer_callback(call["id"], "❌ Request not found!", show_alert=True)
            return
        r_id, r_uid, r_amt, r_method, r_acc, r_status, r_ts = tuple(row)
        ts_str = datetime.fromtimestamp(r_ts).strftime("%Y-%m-%d %H:%M") if r_ts else "N/A"
        r_method_eid = get_payment_emoji_id(r_method)
        r_method_html = f'<tg-emoji emoji-id="{r_method_eid}">💳</tg-emoji>'
        detail_txt = (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"《 {PEM['money']} REQUEST #{r_id} 》\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['user']} <b>User ID:</b> <a href='tg://user?id={r_uid}'>{r_uid}</a>\n"
            f'{PEM["money"]} <b>Amount:</b> {r_amt} USDT\n'
            f'{PEM["phone"]} <b>Account:</b> <code>{r_acc}</code>\n'
            f'{r_method_html} <b>Method:</b> {r_method}\n'
            f'{PEM["ok"]} <b>Status:</b> {r_status.upper()}\n'
            f'{PEM["star"]} <b>Time:</b> {ts_str}\n'
            f"━━━━━━━━━━━━━━━━━━"
        )
        if r_status == "pending":
            kb = {"inline_keyboard": [
                [{"text": "APPROVE", "icon_custom_emoji_id": "5352694861990501856", "callback_data": f"wappr_{r_id}", "style": "success"},
                 {"text": "REJECT", "icon_custom_emoji_id": "5420130255174145507", "callback_data": f"wrejr_{r_id}", "style": "danger"}],
                [{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "view_w_requests", "style": "primary"}]
            ]}
        else:
            kb = {"inline_keyboard": [[{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "view_w_requests", "style": "primary"}]]}
        edit_message(chat_id, msg_id, render_body_text(detail_txt), reply_markup=kb)

    elif data.startswith("wappr_") or data.startswith("wrejr_"):
        if not is_admin(chat_id):
            answer_callback(call["id"], "🚫 Admins only!", show_alert=True)
            return
        action = "APPROVE" if data.startswith("wappr_") else "REJECT"
        db_id = data.replace("wappr_", "").replace("wrejr_", "")
        try:
            with db_lock:
                conn = get_db_conn()
                row = conn.execute(
                    "SELECT id, user_id, amount, method, account, status FROM withdrawals WHERE id=?", (db_id,)
                ).fetchone()
                conn.close()
        except:
            row = None
        if not row:
            answer_callback(call["id"], "❌ Request not found!", show_alert=True)
            return
        r_id, r_uid, r_amt, r_method, r_acc, r_status = tuple(row)
        if r_status != "pending":
            answer_callback(call["id"], "❌ Already processed!", show_alert=True)
            return
        new_status = "approved" if action == "APPROVE" else "rejected"
        try:
            with db_lock:
                conn = get_db_conn()
                conn.execute("UPDATE withdrawals SET status=? WHERE id=?", (new_status, db_id))
                conn.commit()
                conn.close()
        except: pass
        if action == "REJECT":
            update_balance(r_uid, r_amt)
            send_message(r_uid, render_body_text(f"{PEM['no']} Your {r_amt} USDT withdrawal request was rejected. Balance refunded."))
        else:
            send_message(r_uid, render_body_text(f"{PEM['ok']} Your {r_amt} USDT withdrawal request has been paid!"))
        status_icon = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
        r_method_eid2 = get_payment_emoji_id(r_method)
        r_method_html2 = f'<tg-emoji emoji-id="{r_method_eid2}">💳</tg-emoji>'
        done_txt = (
            f"━━━━━━━━━━━━━━━━━━\n"
            f"《 {PEM['money']} REQUEST #{r_id} — {new_status.upper()} 》\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['user']} <b>User:</b> <a href='tg://user?id={r_uid}'>{r_uid}</a>\n"
            f"{PEM['money']} <b>Amount:</b> {r_amt} USDT\n"
            f"{PEM['phone']} <b>Account:</b> <code>{r_acc}</code>\n"
            f"{r_method_html2} <b>Method:</b> {r_method}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"{PEM['ok'] if action == 'APPROVE' else PEM['no']} <b>Processed by admin</b>"
        )
        kb = {"inline_keyboard": [
            [{"text": new_status.upper(), "icon_custom_emoji_id": status_icon, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}],
            [{"text": "Back to Requests", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "view_w_requests", "style": "primary"}]
        ]}
        edit_message(chat_id, msg_id, render_body_text(done_txt), reply_markup=kb)
        answer_callback(call["id"])

    elif data == "dxa_toggle_w":
        bot_settings["withdraw_on"] = not bot_settings["withdraw_on"]
        save_db()
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DEV CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "dxa_toggle_refer":
        bot_settings["refer_on"] = not bot_settings.get("refer_on", True)
        save_db()
        status = "ON ✅" if bot_settings["refer_on"] else "OFF ❌"
        answer_callback(call["id"], f"Refer & Earn: {status}", show_alert=True)
        edit_message(chat_id, msg_id, render_body_text("🕹 <b>DEV CONTROL PANEL</b>"), reply_markup=dxa_control_keyboard())

    elif data == "manage_w_methods":
        edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data == "add_wm":
        user_states[chat_id] = "wait_for_add_wm"
        temp_data[chat_id] = {"msg_id": msg_id}
        edit_message(chat_id, msg_id, render_body_text("📝 Send the name of the new Withdrawal Method:"), reply_markup={"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "manage_w_methods", "style": "danger"}]]})

    elif data.startswith("del_wm_"):
        idx = int(data.split("_")[2])
        if 0 <= idx < len(bot_settings["w_methods"]):
            del bot_settings["w_methods"][idx]
            save_db()
            answer_callback(call["id"], "✅ Method deleted!", show_alert=True)
            edit_message(chat_id, msg_id, render_body_text("💳 <b>WITHDRAWAL METHODS</b>\n\nManage your withdrawal methods below:"), reply_markup=w_methods_keyboard())

    elif data.startswith("dxa_"):
        key = data.replace("dxa_", "")
        key_map = {"min_w": "min_withdraw", "otp_r": "otp_reward", "ref_r": "refer_reward", "cool": "cooldown", "num_req": "num_req", "num_share": "num_share", "sup_link": "support_link", "w_group": "w_group"}
        if key in key_map:
            temp_data[chat_id] = {"msg_id": msg_id, "key": key_map[key]}
            user_states[chat_id] = "set_dxa"
            cancel_kb = {"inline_keyboard": [[{"text": "Cancel", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "cancel_dxa_edit", "style": "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(f"📝 Please send the new value for <code>{key_map[key]}</code>:"), reply_markup=cancel_kb)
            answer_callback(call["id"])

    elif data == "get_number":
        local_srvs = set([b["service"] for b in number_batches.values() if b["numbers"]])
        voltx_srvs = set(bot_settings.get("voltx_services", {}).keys())
        all_services = local_srvs.union(voltx_srvs)
        if not all_services:
            answer_callback(call["id"], "❌ No numbers or services available!", show_alert=True)
        else:
            c_msg = bot_settings["custom_messages"].get("get_number", {})
            txt = render_body_text(c_msg.get("text", f"{PEM['pin']} Select Service"))
            apps_db = bot_settings.get("premium_apps", {})
            gn_kb = []
            for s in all_services:
                emoji_id = "5352694861990501856"
                for app_key, app_data in apps_db.items():
                    if s.upper() == app_key or s.upper() in app_key or app_key in s.upper():
                        if "id" in app_data: emoji_id = app_data["id"]; break
                gn_kb.append([{"text": f"{s}", "icon_custom_emoji_id": emoji_id, "callback_data": f"g_s_{s}", "style": "primary"}])
            for b in c_msg.get("buttons", []):
                b_copy = b.copy()
                if "style" not in b_copy: b_copy["style"] = "primary"
                gn_kb.append([b_copy])
            gn_kb.append([{"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}])
            edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": gn_kb})

    elif data.startswith("g_s_"):
        service = data.split("g_s_")[1]
        local_cnts = set([b["country"] for b in number_batches.values() if b["service"] == service and b["numbers"]])
        voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
        all_countries = local_cnts.union(voltx_cnts)
        
        c_msg = bot_settings["custom_messages"].get("select_country", {})
        raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
        txt = render_body_text(raw_txt)
        
        flags_db = bot_settings.get("premium_flags", {})
        kb = []
        for c in all_countries:
            emoji_id = "5780471598922337683"
            display_name = c
            for flag_code, flag_data in flags_db.items():
                iso = flag_data.get("iso", "").upper()
                name = flag_data.get("name", "").upper()
                if c == flag_code or _country_code_matches(c, iso, name):
                    if "id" in flag_data:
                        emoji_id = flag_data["id"]
                        display_name = flag_data.get("name", c)
                        break
            kb.append([{"text": display_name, "icon_custom_emoji_id": emoji_id, "callback_data": f"g_c_{service}_{c}", "style": "success"}])
        
        for b in c_msg.get("buttons", []): 
            b_copy = b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])
            
        kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "close_msg", "style": "danger"}])
        edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": kb})

    elif data.startswith("ntf_get_"):
        # format: ntf_get_{service}||{country}  (|| separator avoids breaking on _ in service names)
        payload = data[len("ntf_get_"):]
        if "||" in payload:
            ntf_service, ntf_country = payload.split("||", 1)
        else:
            # Legacy fallback: ntf_get_{service}_{country}
            parts = payload.split("_", 1)
            ntf_service = parts[0] if parts else ""
            ntf_country = parts[1] if len(parts) > 1 else ""

        # Cooldown check — same as normal GET NUMBER
        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return
        user_cooldowns[chat_id] = now

        available_indices = []
        for b_id, b_data in number_batches.items():
            if b_data["service"].upper() == ntf_service.upper() and b_data["country"] == ntf_country:
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if not n_obj.get("exhausted") and chat_id not in n_obj.get("used_by", []):
                        available_indices.append((b_id, idx))

        if not available_indices:
            answer_callback(call["id"], f"❌ No stock available for {ntf_service}", show_alert=True)
            return

        # Pick numbers — numbers stay in stock until an OTP is actually received;
        # we only mark them "exhausted" (max shares reached) so they're not handed
        # out to further users, but they remain visible/counted as stock.
        random.shuffle(available_indices)
        fetched_nums = []
        for b_id, idx in available_indices:
            if len(fetched_nums) >= bot_settings["num_req"]: break
            n_obj = number_batches[b_id]["numbers"][idx]
            fetched_nums.append(n_obj["num"])
            n_obj["shares"] = n_obj.get("shares", 0) + 1
            n_obj.setdefault("used_by", []).append(chat_id)
            total_assigned_stats += 1
            if n_obj["shares"] >= bot_settings.get("num_share", 1):
                n_obj["exhausted"] = True

        save_db()

        if not fetched_nums:
            answer_callback(call["id"], "❌ No stock available!", show_alert=True)
            return

        # Build card UI — identical to g_c_ flow
        app_full_name, srv_html_cb = get_service_info_html(ntf_service)
        emoji_id_srv = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if ntf_service.upper() == app_key or ntf_service.upper() in app_key or app_key in ntf_service.upper():
                if "id" in app_data:
                    emoji_id_srv = app_data["id"]
                    break

        flags_db = bot_settings.get("premium_flags", {})
        country_name_disp = ntf_country
        country_iso_disp = "XX"
        flag_eid_ntf = None
        flag_char_disp = "🏳️"
        for fc, fd in flags_db.items():
            iso = fd.get("iso", "").upper()
            name = fd.get("name", "").upper()
            if fc == ntf_country or _country_code_matches(ntf_country, iso, name):
                country_name_disp = fd.get("name", ntf_country)
                country_iso_disp = fd.get("iso", "XX")
                flag_eid_ntf = fd.get("id")
                flag_char_disp = fd.get("char", "🏳️")
                break

        hdr_flag_html = f'<tg-emoji emoji-id="{flag_eid_ntf}">{flag_char_disp}</tg-emoji>' if flag_eid_ntf else flag_char_disp
        header_txt = f"{hdr_flag_html}  <b>{country_name_disp.upper()}</b>  {srv_html_cb}"

        kb = []
        for num in fetched_nums:
            display_num = f"+{num}" if not num.startswith("+") else num
            kb.append([{"text": display_num, "icon_custom_emoji_id": emoji_id_srv, "copy_text": {"text": display_num}, "style": "success"}])

        c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
        for c_b in c_btns:
            b_copy = c_b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])

        kb.append([{"text": "Change Country", "icon_custom_emoji_id": "5370715282044100355", "callback_data": f"g_c_{ntf_service}", "style": "success"}])
        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5377336227533969892", "callback_data": f"c_n_{ntf_service}_{ntf_country}", "style": "success"}])
        kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5429405838345265327", "url": bot_settings["otp_link"], "style": "success"}])

        answer_callback(call["id"])
        expire_previous_number(chat_id)
        num_msg_res = send_message(chat_id, header_txt, reply_markup={"inline_keyboard": kb})
        if num_msg_res and "result" in num_msg_res:
            user_active_sessions[chat_id] = {"msg_id": num_msg_res["result"]["message_id"], "nums": fetched_nums, "service": ntf_service}

    elif data.startswith("g_c_") or data.startswith("c_n_"):

        now = time.time()
        if now - user_cooldowns.get(chat_id, 0) < bot_settings["cooldown"]:
            answer_callback(call["id"], f"⌛ Please wait {int(bot_settings['cooldown'] - (now - user_cooldowns.get(chat_id, 0)))}s.", show_alert=True)
            return
        

        user_cooldowns[chat_id] = now
        
        # expire_previous_number is called AFTER successful fetch below



        parts = data.split("_")
        service = parts[2] if len(parts) > 2 else ""
        country = parts[3] if len(parts) > 3 else ""

        # If only service given (e.g. g_c_WHATSAPP), show country selection
        if not country:
            local_cnts = set([b["country"] for b in number_batches.values() if b["service"] == service and b["numbers"]])
            voltx_cnts = set(bot_settings.get("voltx_services", {}).get(service, {}).keys())
            all_countries = local_cnts.union(voltx_cnts)
            c_msg = bot_settings["custom_messages"].get("select_country", {})
            raw_txt = c_msg.get("text", "📌 Select a country for {service}:").replace("{service}", service)
            txt = render_body_text(raw_txt)
            flags_db = bot_settings.get("premium_flags", {})
            ck_kb = []
            for c in all_countries:
                emoji_id = "5780471598922337683"
                display_name = c
                for flag_code, flag_data in flags_db.items():
                    iso = flag_data.get("iso", "").upper()
                    name = flag_data.get("name", "").upper()
                    if c == flag_code or _country_code_matches(c, iso, name):
                        if "id" in flag_data:
                            emoji_id = flag_data["id"]
                            display_name = flag_data.get("name", c)
                            break
                ck_kb.append([{"text": display_name, "icon_custom_emoji_id": emoji_id, "callback_data": f"g_c_{service}_{c}", "style": "success"}])
            ck_kb.append([{"text": "Back", "icon_custom_emoji_id": "5267490665117275176", "callback_data": "close_msg", "style": "danger"}])
            edit_message(chat_id, msg_id, txt, reply_markup={"inline_keyboard": ck_kb})
            return

        available_indices = []
        # Check Local Stock First
        for b_id, b_data in number_batches.items():
            if b_data["service"] == service and b_data["country"] == country:
                for idx, n_obj in enumerate(b_data["numbers"]):
                    if not n_obj.get("exhausted") and chat_id not in n_obj.get("used_by", []):
                        available_indices.append((b_id, idx))

        # IF NO LOCAL STOCK, Check Voltx Services (actually call the Voltx getnum API)
        fetched_nums = []
        if not available_indices:
            voltx_srv_data = bot_settings.get("voltx_services", {}).get(service, {}).get(country)
            voltx_keys = bot_settings.get("voltx_keys", [])
            wanted_count = max(1, bot_settings.get("num_req", 1))

            if voltx_srv_data and len(voltx_srv_data) > 0 and voltx_keys:
                ranges_to_try = list(voltx_srv_data)
                random.shuffle(ranges_to_try)
                # Keep requesting numbers (re-cycling ranges if needed) until we
                # hit num_req or the Voltx API stops returning fresh numbers.
                attempts = 0
                max_attempts = max(wanted_count * len(voltx_keys) * 3, len(ranges_to_try) * len(voltx_keys))
                range_idx = 0
                while len(fetched_nums) < wanted_count and attempts < max_attempts and ranges_to_try:
                    target_range = ranges_to_try[range_idx % len(ranges_to_try)]
                    range_idx += 1
                    got_one = False
                    for api_key in voltx_keys:
                        attempts += 1
                        try:
                            headers = {"mauthapi": api_key}
                            res = requests.post(f"{VOLTX_BASE_URL}/getnum", headers=headers, json={"rid": target_range}, timeout=10)
                            resp_data = res.json()
                            if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data:
                                full_num = str(resp_data["data"].get("full_number") or resp_data["data"].get("no_plus_number") or "").replace("+", "").strip()
                                if full_num and full_num not in fetched_nums:
                                    fetched_nums.append(full_num)
                                    voltx_assigned_numbers[full_num] = chat_id
                                    total_assigned_stats += 1
                                    got_one = True
                                    break
                        except Exception:
                            continue
                    if not got_one and attempts >= max_attempts:
                        break

            if not fetched_nums:
                answer_callback(call["id"])
                edit_message(chat_id, msg_id, render_body_text("❌ <b>Number out of stock!</b>\n\nPlease try again later."), reply_markup={"inline_keyboard": [[{"text": "🔄 Try Again", "icon_custom_emoji_id": "5370715282044100355", "callback_data": "get_number", "style": "primary"}, {"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]})
                return
        else:
            random.shuffle(available_indices)

            for b_id, idx in available_indices:
                if len(fetched_nums) >= bot_settings["num_req"]: break
                n_obj = number_batches[b_id]["numbers"][idx]

                fetched_nums.append(n_obj["num"])
                n_obj["shares"] += 1
                n_obj["used_by"].append(chat_id)
                total_assigned_stats += 1

                if n_obj["shares"] >= bot_settings.get("num_share", 1):
                    n_obj["exhausted"] = True

            save_db()

            if not fetched_nums:
                answer_callback(call["id"])
                edit_message(chat_id, msg_id, render_body_text("❌ <b>Number out of stock!</b>\n\nPlease try again later."), reply_markup={"inline_keyboard": [[{"text": "🔄 Try Again", "icon_custom_emoji_id": "5370715282044100355", "callback_data": "get_number", "style": "primary"}, {"text": "Close", "icon_custom_emoji_id": "5420130255174145507", "callback_data": "close_msg", "style": "danger"}]]})
                return

        app_full_name, srv_html_cb = get_service_info_html(service)
        emoji_id_srv = "5337302974806922068"
        apps_db = bot_settings.get("premium_apps", {})
        for app_key, app_data in apps_db.items():
            if service.upper() == app_key or service.upper() in app_key or app_key in service.upper():
                if "id" in app_data:
                    emoji_id_srv = app_data["id"]
                    break

        # Country display — country can be a phone code (e.g. "880") OR a voltx
        # country key/ISO code (e.g. "SL"), so match against both the dict key
        # and the flag entry's iso/name, not just a raw dict-key lookup.
        flags_db = bot_settings.get("premium_flags", {})
        country_name_disp = country
        country_iso_disp = "XX"
        flag_eid_cb = None
        flag_char_disp = "🏳️"
        for fc, fd in flags_db.items():
            iso = fd.get("iso", "").upper()
            name = fd.get("name", "").upper()
            if fc == country or _country_code_matches(country, iso, name):
                country_name_disp = fd.get("name", country)
                country_iso_disp = fd.get("iso", "XX")
                flag_eid_cb = fd.get("id")
                flag_char_disp = fd.get("char", "🏳️")
                break

        hdr_flag_html3 = f'<tg-emoji emoji-id="{flag_eid_cb}">{flag_char_disp}</tg-emoji>' if flag_eid_cb else flag_char_disp
        header_txt = f"{hdr_flag_html3}  <b>{country_name_disp.upper()}</b>  {srv_html_cb}"

        kb = []
        # Number rows
        for num in fetched_nums:
            display_num = f"+{num}" if not num.startswith("+") else num
            kb.append([{"text": display_num, "icon_custom_emoji_id": emoji_id_srv, "copy_text": {"text": display_num}, "style": "success"}])

        c_btns = bot_settings["custom_messages"].get("get_number", {}).get("buttons", [])
        for c_b in c_btns:
            b_copy = c_b.copy()
            if "style" not in b_copy: b_copy["style"] = "primary"
            kb.append([b_copy])

        # Bottom action row
        kb.append([{"text": "Change Country", "icon_custom_emoji_id": "5370715282044100355", "callback_data": f"g_c_{service}", "style": "success"}])
        kb.append([{"text": "Change Number", "icon_custom_emoji_id": "5377336227533969892", "callback_data": f"c_n_{service}_{country}", "style": "success"}])
        kb.append([{"text": "OTP Group", "icon_custom_emoji_id": "5429405838345265327", "url": bot_settings["otp_link"], "style": "success"}])

        expire_previous_number(chat_id, current_msg_id=msg_id)
        try:
            edit_message(chat_id, msg_id, header_txt, reply_markup={"inline_keyboard": kb})
            user_active_sessions[chat_id] = {"msg_id": msg_id, "nums": fetched_nums, "service": service}
        except:
            num_msg_res = send_message(chat_id, header_txt, reply_markup={"inline_keyboard": kb})
            if num_msg_res and "result" in num_msg_res:
                user_active_sessions[chat_id] = {"msg_id": num_msg_res["result"]["message_id"], "nums": fetched_nums, "service": service}

    elif data.startswith("wapp_") or data.startswith("wrej_"):

        user_id_clicked = call["from"]["id"]
        if not is_admin(user_id_clicked):
            answer_callback(call["id"], "🚫 Only Bot Admins can process withdrawals!", show_alert=True)
            return
            
        action = "APPROVE" if data.startswith("wapp_") else "REJECT"
        req_id = data.replace("wapp_", "").replace("wrej_", "")
        
        if req_id in pending_withdrawals:
            req_data = pending_withdrawals[req_id]
            u_id, amt = req_data["user_id"], req_data["amount"]
            num = req_data["number"]
            full_name = req_data.get("full_name", u_id)
            
            if action == "APPROVE" and len(num) >= 7:
                masked_num = f"{num[:4]}❖DXA❖{num[-3:]}"
            else:
                masked_num = num
            
            status_text = "APPROVED" if action == "APPROVE" else "REJECTED"
            emoji_icon_id = "5352694861990501856" if action == "APPROVE" else "5420130255174145507"
            new_text = f"🎙 <b>WITHDRAWAL {status_text}</b>\n\n👤 <b>USER:</b> <a href='tg://user?id={u_id}'>{full_name}</a>\n💳 <b>WITHDRAWAL:</b> {amt} USDT\n🍏 <b>NUMBER:</b> <code>{masked_num}</code>\n🏦 <b>METHOD:</b> {req_data['method']}\n\n🧾 <b>REQ ID:</b> {req_id}\n👨‍⚖️ <b>PROCESSED BY ADMIN</b>"
            
            kb = {"inline_keyboard": [[{"text": status_text, "icon_custom_emoji_id": emoji_icon_id, "callback_data": "ignore", "style": "success" if action == "APPROVE" else "danger"}]]}
            edit_message(chat_id, msg_id, render_body_text(new_text), reply_markup=kb)
            
            if action == "REJECT":
                update_balance(u_id, amt) 
                send_message(u_id, render_body_text(f"❌ Your {amt} USDT withdrawal request was rejected. Balance refunded."))
            else:
                send_message(u_id, render_body_text(f"{PEM['ok']} Your {amt} USDT withdrawal request has been paid successfully!"))
            
            try:
                with db_lock:
                    conn = get_db_conn()
                    conn.execute("UPDATE withdrawals SET status=? WHERE id=?", ("approved" if action == "APPROVE" else "rejected", req_id))
                    conn.commit()
                    conn.close()
            except: pass
                
            del pending_withdrawals[req_id]
        else:
            answer_callback(call["id"], "❌ Request already processed!", show_alert=True)


def voltx_sms_listener():
    global processed_otps, recent_traffic, voltx_assigned_numbers
    while True:
        try:
            voltx_keys = bot_settings.get("voltx_keys", [])
            for api_key in voltx_keys:
                try:
                    headers = {"mauthapi": api_key}
                    res = requests.get(f"{VOLTX_BASE_URL}/success-otp", headers=headers, timeout=10)
                    resp_data = res.json()
                    
                    if resp_data.get("meta", {}).get("code") == 200 and "data" in resp_data and "otps" in resp_data["data"]:
                        for item in resp_data["data"]["otps"]:
                            num = str(item.get("number", "")).replace("+", "")
                            msg_text = str(item.get("message", ""))
                            otp = extract_otp_code(msg_text) or "CODE"
                            otp_id = str(item.get("otp_id", otp))
                            
                            app_name = "Voltx Service"
                            detected_app = detect_service(msg_text)
                            if detected_app: app_name = detected_app
                                
                            unique_id = f"VOLTX_{num}_{otp_id}"
                            
                            if unique_id not in processed_otps and num:
                                processed_otps.add(unique_id)
                                if len(processed_otps) > 5000: processed_otps.clear()
                                
                                char, iso = get_flag_and_code(num)
                                app_full_name, prem_app_html = get_service_info_html(app_name, msg_text)
                                current_time = time.time()
                                
                                recent_traffic = [t for t in recent_traffic if current_time - t.get("time", 0) <= 3600]
                                recent_traffic.append({"service": app_full_name, "iso": iso, "flag": char, "number": num, "time": current_time})
                                save_local_db()
                                
                                display_num = f"+{num}" if not str(num).startswith("+") else str(num)
                                masked = mask_number(display_num)
                                lang = detect_language(msg_text)
                                
                                display_msg = render_body_text(f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} <b>{iso}</b> <b>{masked}</b> {lang}\n╚═══════════════╝")
                                
                                for fw in bot_settings.get("fw_groups", []):
                                    kb = build_otp_fw_kb(otp, fw)
                                    send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})
                                    
                                owner_id = None
                                owner_service = None
                                clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                
                                for uid, session_data in user_active_sessions.items():
                                    for act_num in session_data.get("nums", []):
                                        act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                                            owner_id = uid
                                            owner_service = session_data.get("service")
                                            break
                                    if owner_id: break
                                    
                                if not owner_id:
                                    for vtx_n, n_owner in voltx_assigned_numbers.items():
                                        clean_vtx = str(vtx_n).replace("+", "").replace(" ", "").replace("-", "").strip()
                                        if clean_vtx == clean_api_num or (len(clean_vtx) >= 8 and clean_vtx.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(clean_vtx[-8:])):
                                            owner_id = n_owner
                                            break
                                        
                                if owner_id:
                                    # Use the batch's assigned service (set by admin) for the owner's
                                    # inbox display + reward, instead of re-detecting from the SMS text.
                                    if owner_service:
                                        owner_app_full_name, owner_prem_app_html = get_service_info_html(owner_service)
                                    else:
                                        owner_app_full_name, owner_prem_app_html = app_full_name, prem_app_html

                                    inbox_msg = render_body_text(f"╔═══════════════╗\n║ {owner_prem_app_html} {get_flag_info_html(display_num)} <b>{iso}</b> {lang}\n╚═══════════════╝\n<b>{display_num}</b>")
                                    inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]
                                    
                                    reward = get_service_otp_reward(owner_app_full_name)
                                    if reward > 0:
                                        update_balance(owner_id, reward)
                                        inbox_kb.append([{"text": f"Added {reward} USDT", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])
                                    
                                    send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
                                    
                                    try:
                                        with db_lock:
                                            conn = get_db_conn()
                                            conn.execute("UPDATE users SET total_otps=total_otps+1 WHERE user_id=?", (owner_id,))
                                            conn.commit()
                                            conn.close()
                                        if owner_id in user_cache: user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps",0)+1
                                        _today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
                                        if daily_otps.get(owner_id, {}).get("date") != _today: daily_otps[owner_id] = {"date": _today, "count": 0}
                                        daily_otps[owner_id]["count"] = daily_otps[owner_id].get("count", 0) + 1
                                    except: pass
                except: pass
        except: pass
        time.sleep(2)

def global_sms_listener():
    # Nexa SMS polling removed — panels handled by panel_monitor_thread and scraper2
    while True:
        time.sleep(60)

def _scraper2_otp_callback(num: str, otp: str, msg_text: str, panel_name: str, cli: str = ""):
    """scraper2 se OTP aaye to yahan handle karo — same logic as panel_monitor_thread.
    
    Service detection priority (scraping method):
      1. cli from scraped table column (if present and not numeric)
      2. detect_service() from message body keywords
      3. panel_name as last fallback
    """
    try:
        unique_id = f"{num}_{otp}"
        if unique_id in processed_otps:
            return
        processed_otps.add(unique_id)
        if len(processed_otps) > 5000:
            processed_otps.clear()

        char, iso = get_flag_and_code(num)

        # Smart service detection for scraping method
        cli_clean = cli.strip() if cli else ""
        _is_cli_numeric = bool(re.match(r'^\+?[\d\s\-]+$', cli_clean)) if cli_clean else True
        if cli_clean and not _is_cli_numeric:
            # CLI from table column — use it directly (e.g. "Facebook", "Paypal")
            service_hint = cli_clean
        else:
            # No CLI → detect from message body keywords
            detected = detect_service(msg_text)
            service_hint = detected if detected else panel_name

        app_full_name, prem_app_html = get_service_info_html(service_hint, msg_text)
        current_time = time.time()

        recent_traffic.append({
            "service": app_full_name, "iso": iso, "flag": char,
            "number": num, "time": current_time
        })
        save_local_db()

        display_num = f"+{num}" if not str(num).startswith("+") else str(num)
        masked = mask_number(display_num)
        lang = detect_language(msg_text)

        display_msg = render_body_text(
            f"╔═══════════════╗\n║ {prem_app_html} {get_flag_info_html(display_num)} <b>{iso}</b> <b>{masked}</b> {lang}\n╚═══════════════╝"
        )

        for fw in bot_settings["fw_groups"]:
            kb = build_otp_fw_kb(otp, fw)
            send_message(fw["chat_id"], display_msg, reply_markup={"inline_keyboard": kb})

        clean_api_num = str(num).replace("+", "").replace(" ", "").replace("-", "").strip()

        # OTP actually received for this number now — remove it from stock.
        remove_number_after_otp(clean_api_num)

        owners = []
        owner_assigned_service = {}

        for uid, session_data in user_active_sessions.items():
            for act_num in session_data.get("nums", []):
                act_clean = str(act_num).replace("+", "").replace(" ", "").replace("-", "").strip()
                if act_clean == clean_api_num or (len(act_clean) >= 8 and act_clean.endswith(clean_api_num[-8:])) or (len(clean_api_num) >= 8 and clean_api_num.endswith(act_clean[-8:])):
                    owners.append(uid)
                    owner_assigned_service[uid] = session_data.get("service")
                    break


        owners = list(set(owners))
        for owner_id in owners:
            # Use the batch's assigned service (set by admin at stock time) for the
            # owner's inbox display + reward, instead of re-detecting from the SMS text.
            assigned_service = owner_assigned_service.get(owner_id)
            if assigned_service:
                owner_app_full_name, owner_prem_app_html = get_service_info_html(assigned_service)
            else:
                owner_app_full_name, owner_prem_app_html = app_full_name, prem_app_html

            inbox_msg = render_body_text(
                f"╔═══════════════╗\n║ {owner_prem_app_html} {get_flag_info_html(display_num)} <b>{iso}</b> {lang}\n╚═══════════════╝\n<b>{display_num}</b>"
            )
            inbox_kb = [[{"text": f"{otp}", "icon_custom_emoji_id": "5353022963132174959", "copy_text": {"text": otp}, "style": "success"}]]

            reward = get_service_otp_reward(owner_app_full_name)
            if reward > 0:
                update_balance(owner_id, reward)
                inbox_kb.append([{"text": f"Added {reward} USDT", "icon_custom_emoji_id": "5420396762189831222", "callback_data": "ignore", "style": "primary"}])

            send_message(owner_id, inbox_msg, reply_markup={"inline_keyboard": inbox_kb})
            try:
                with db_lock:
                    conn = get_db_conn()
                    conn.execute("UPDATE users SET total_otps=total_otps+1 WHERE user_id=?", (owner_id,))
                    conn.commit()
                    conn.close()
                if owner_id in user_cache:
                    user_cache[owner_id]["total_otps"] = user_cache[owner_id].get("total_otps", 0) + 1
                _today = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
                if daily_otps.get(owner_id, {}).get("date") != _today:
                    daily_otps[owner_id] = {"date": _today, "count": 0}
                daily_otps[owner_id]["count"] = daily_otps[owner_id].get("count", 0) + 1
            except Exception:
                pass
    except Exception as e:
        pass


def main():
    global BOT_USERNAME, BOT_NAME
    res = api_call("getMe")
    if res.get("ok"):
        BOT_USERNAME = res["result"]["username"]
        BOT_NAME = res["result"].get("first_name", BOT_USERNAME)
    print(f"🤖 Bot is starting... @{BOT_USERNAME}")

    # Migrate start message to new clean format
    NEW_START_TEXT = (
        '<tg-emoji emoji-id="5199885118214255386">👋</tg-emoji> '
        "Welcome to <b>{bot_name}</b>, <b>{name}</b>!\n\n"
        '<tg-emoji emoji-id="4958479549265347295">⚡</tg-emoji> Fast delivery\n'
        '<tg-emoji emoji-id="5296369303661067030">🔒</tg-emoji> Secure numbers\n'
        '<tg-emoji emoji-id="5017470156276761427">♻️</tg-emoji> Change anytime\n\n'
        '<tg-emoji emoji-id="5042147419156907206">👇</tg-emoji> <i>Choose an option below to begin:</i>'
    )
    bot_settings.setdefault("custom_messages", {}).setdefault("start", {})["text"] = NEW_START_TEXT
    save_db()
    
    threading.Thread(target=panel_monitor_thread, daemon=True).start()
    threading.Thread(target=global_sms_listener, daemon=True).start()
    threading.Thread(target=voltx_sms_listener, daemon=True).start()
    print("📡 Background APIs & Global SMS Listener Started!")

    # 🌟 Scraper2 — Method 2 (IVAS, PSCall, Multi-Panel backup method)
    try:
        import scraper2
        scraper2.start(on_otp_found=_scraper2_otp_callback, get_settings=lambda: bot_settings)
        print("🔄 Scraper2 (Method 2) Started!")
    except Exception as e:
        print(f"⚠️ Scraper2 load error: {e}")
    
    # 🌟 PRO-LEVEL FAST SYSTEM: 500 Workers Pool
    executor = ThreadPoolExecutor(max_workers=500)
    
    offset = None
    while True:
        try:
            updates = api_call(f"getUpdates?timeout=50&offset={offset}")
            if updates and "result" in updates:
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    if "message" in update: 
                        executor.submit(handle_message, update["message"])
                    elif "callback_query" in update: 
                        executor.submit(handle_callback, update["callback_query"])
        except Exception as e:
            time.sleep(2)

if __name__ == "__main__":
    main()    