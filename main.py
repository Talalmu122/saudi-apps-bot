import requests
import os
import sys
from google_play_scraper import Sort, content_selection

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
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

def monitor():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    last_id_file = "last_apps_ids.txt"
    
    old_ids = []
    if os.path.exists(last_id_file):
        with open(last_id_file, "r") as f:
            old_ids = f.read().splitlines()

    new_ids = []

    try:
        # --- متجر آبل ---
        apple_url = "https://rss.applemarketingtools.com/api/v2/sa/apps/top-free/10/apps.json"
        apple_res = requests.get(apple_url).json()
        for app in apple_res['feed']['results']:
            aid = f"apple_{app['id']}"
            new_ids.append(aid)
            if aid not in old_ids:
                icon = app['artworkUrl100'].replace('100x100bb', '512x512bb')
                send_telegram(token, chat_id, app['name'], app['artistName'], app['url'], icon, "Apple Store 🍏")

        # --- متجر جوجل بلاي (التصنيف الجديد) ---
        # بنستخدم طريقة البحث عن أحدث التطبيقات المجانية في السعودية
        from google_play_scraper import search
        
        # بنبحث بكلمة "السعودية" أو نستخدم تصنيف التطبيقات الجديدة
        google_apps = search("السعودية", lang="ar", country="sa", n_hits=10)
        
        for g_app in google_apps:
            gid = f"google_{g_app['appId']}"
            new_ids.append(gid)
            if gid not in old_ids:
                send_telegram(token, chat_id, g_app['title'], g_app.get('developer', 'N/A'), f"https://play.google.com/store/apps/details?id={g_app['appId']}", g_app['icon'], "Google Play 🤖")

        # حفظ المعرفات
        with open(last_id_file, "w") as f:
            f.write("\n".join(new_ids))
            
        print("Done successfully!")

    except Exception as e:
        print(f"Main Error: {e}")

if __name__ == "__main__":
    monitor()
