import requests
import os
from google_play_scraper import search

# إعدادات التليجرام - تأكد أنك وضعتها في Secrets بجيت هاب
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

def send_telegram(title, developer, link, store_name):
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
        "reply_markup": {
            "inline_keyboard": [[{"text": "📥 تحميل التطبيق", "url": link}]]
        }
    }
    requests.post(url, json=payload)

def hunt_android():
    print("جاري فحص أندرويد...")
    keywords = ["السعودية", "SAUDI", "توصيل", "المدينة المنورة", "متجر"]
    for kw in keywords:
        try:
            # تم حذف 'sort' لتجنب الخطأ الذي ظهر في الصورة
            results = search(kw, lang='ar', country='sa', n_hits=10)
            for app in results:
                app_id = app['appId']
                if not is_sent(app_id):
                    title = app.get('title', 'بدون اسم')
                    developer = app.get('developer', 'مطور غير معروف')
                    link = f"https://play.google.com/store/apps/details?id={app_id}"
                    send_telegram(title, developer, link, "Google Play")
                    save_to_memory(app_id)
        except Exception as e:
            print(f"خطأ في بحث أندرويد للكلمة {kw}: {e}")

def hunt_apple():
    print("جاري فحص آبل ستور...")
    # البحث في أحدث التطبيقات المضافة للمتجر السعودي
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
                send_telegram(title, developer, link, "App Store")
                save_to_memory(app_id)
    except Exception as e:
        print(f"خطأ في جلب بيانات آبل: {e}")

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("خطأ: تأكد من إضافة TELEGRAM_TOKEN و CHAT_ID في Secrets")
    else:
        hunt_android()
        hunt_apple()
