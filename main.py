import requests
import os
import sys
from google_play_scraper import Sort, app_list

def send_telegram(token, chat_id, name, artist, app_url, icon_url, store_type):
    message = (
        f"<b>🚀 اكتشاف تطبيق جديد على {store_type}!</b>\n\n"
        f"<b>📦 الاسم:</b> {name}\n"
        f"<b>👨‍💻 المطور:</b> {artist}\n\n"
        f"<i>تنبيه آلي بواسطة رادار طلال</i>"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": icon_url,
        "caption": message,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": "🔗 فتح في المتجر", "url": app_url}]]}
    }
    requests.post(url, json=payload)

def monitor():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    last_id_file = "last_apps_ids.txt"
    
    # تحميل المعرفات القديمة لمنع التكرار
    old_ids = []
    if os.path.exists(last_id_file):
        with open(last_id_file, "r") as f:
            old_ids = f.read().splitlines()

    new_ids = []

    try:
        # --- فحص متجر آبل ---
        apple_url = "https://rss.applemarketingtools.com/api/v2/sa/apps/top-free/5/apps.json"
        apple_data = requests.get(apple_url).json()
        for app in apple_data['feed']['results']:
            aid = f"apple_{app['id']}"
            new_ids.append(aid)
            if aid not in old_ids:
                icon = app['artworkUrl100'].replace('100x100bb', '512x512bb')
                send_telegram(token, chat_id, app['name'], app['artistName'], app['url'], icon, "Apple Store 🍏")

        # --- فحص متجر جوجل بلاي (السعودية) ---
        # نجلب أحدث التطبيقات المجانية في السعودية
        google_apps = app_list(num_res=5, country='sa', lang='ar', sort=Sort.NEWEST)
        for g_app in google_apps:
            gid = f"google_{g_app['appId']}"
            new_ids.append(gid)
            if gid not in old_ids:
                send_telegram(token, chat_id, g_app['title'], g_app['developer'], g_app['url'], g_app['icon'], "Google Play 🤖")

        # حفظ المعرفات الجديدة
        with open(last_id_file, "w") as f:
            f.write("\n".join(new_ids))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor()
