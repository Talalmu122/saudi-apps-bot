import requests
import os
from google_play_scraper import Sort, search
# ملاحظة: سنستخدم مكتبة requests لجلب بيانات آبل مباشرة لأنها أسرع وأدق للجديد
import datetime

# إعدادات التليجرام
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
MEMORY_FILE = "talal_test.txt"

def is_sent(app_id):
    if not os.path.exists(MEMORY_FILE):
        return False
    with open(MEMORY_FILE, 'r') as f:
        return app_id in f.read()

def save_to_memory(app_id):
    with open(MEMORY_FILE, 'a') as f:
        f.write(app_id + '\n')

def send_telegram(title, developer, link, icon, store_name):
    message = (
        f"🚀 <b>تطبيق سعودي جديد رصده الرادار!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📱 التطبيق:</b> {title}\n"
        f"<b>🏢 المطور:</b> {developer}\n"
        f"<b>🏪 المتجر:</b> {store_name}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>رادار طلال للبرامج السعودية</i>"
    )
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": "📥 تحميل التطبيق", "url": link}]]}
    }
    requests.post(url, json=payload)

def hunt_android():
    print("جاري فحص أندرويد...")
    # كلمات بحث قوية لصيد التطبيقات المحلية
    keywords = ["السعودية", "SAUDI", "توصيل", "المدينة المنورة", "متجر"]
    for kw in keywords:
        results = search(kw, lang='ar', country='sa', n_hits=10, sort=Sort.NEWEST)
        for app in results:
            app_id = app['appId']
            if not is_sent(app_id):
                send_telegram(app['title'], app['developer'], f"https://play.google.com/store/apps/details?id={app_id}", app['icon'], "Google Play")
                save_to_memory(app_id)

def hunt_apple():
    print("جاري فحص آبل ستور...")
    # نبحث في آبل عن طريق الـ RSS Feed الرسمي حقهم للجديد في السعودية
    # هذا الرابط يجلب "أحدث" التطبيقات التي نزلت في المتجر السعودي
    url = "https://itunes.apple.com/sa/rss/newapplications/limit=20/json"
    try:
        response = requests.get(url).json()
        entries = response.get('feed', {}).get('entry', [])
        for entry in entries:
            app_id = entry['id']['attributes']['im:id']
            if not is_sent(app_id):
                title = entry['im:name']['label']
                developer = entry['im:artist']['label']
                link = entry['link']['attributes']['href']
                icon = entry['im:image'][2]['label']
                send_telegram(title, developer, link, icon, "App Store")
                save_to_memory(app_id)
    except:
        print("خطأ في جلب بيانات آبل")

if __name__ == "__main__":
    hunt_android()
    hunt_apple()
