import requests
import os
import sys
import google_play_scraper # استدعاء شامل لتجنب أخطاء المكتبة

def send_telegram(token, chat_id, name, artist, app_url, icon_url, store_type):
    # تنسيق الرسالة بشكل احترافي للقناة
    message = (
        f"<b>📱 تطبيق جديد تم رصده!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📦 الاسم:</b> {name}\n"
        f"<b>👨‍💻 المطور:</b> {artist}\n"
        f"<b>🏪 المتجر:</b> {store_type}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>تنبيه آلي بواسطة رادار طلال التقني</i>"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": icon_url,
        "caption": message,
        "parse_mode": "HTML",
        "reply_markup": {"inline_keyboard": [[{"text": "📥 تحميل التطبيق الآن", "url": app_url}]]}
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

def monitor():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID') 
    last_id_file = "last_apps_ids.txt"
    
    old_ids = set()
    if os.path.exists(last_id_file):
        with open(last_id_file, "r") as f:
            old_ids = set(f.read().splitlines())

    current_ids = set()

    try:
        # --- فحص متجر آبل ---
        apple_url = "https://rss.applemarketingtools.com/api/v2/sa/apps/top-free/10/apps.json"
        apple_res = requests.get(apple_url).json()
        for app in apple_res['feed']['results']:
            aid = f"apple_{app['id']}"
            current_ids.add(aid)
            if aid not in old_ids:
                icon = app['artworkUrl100'].replace('100x100bb', '512x512bb')
                send_telegram(token, chat_id, app['name'], app['artistName'], app['url'], icon, "Apple Store 🍏")

        # --- فحص متجر جوجل بلاي ---
        google_results = google_play_scraper.search("Saudi Arabia", lang="ar", country="sa", n_hits=10)
        for g_app in google_results:
            gid = f"google_{g_app['appId']}"
            current_ids.add(gid)
            if gid not in old_ids:
                g_url = f"https://play.google.com/store/apps/details?id={g_app['appId']}"
                send_telegram(token, chat_id, g_app['title'], g_app.get('developer', 'N/A'), g_url, g_app['icon'], "Google Play 🤖")

        # حفظ المعرفات للمرة القادمة
        with open(last_id_file, "w") as f:
            f.write("\n".join(current_ids))
            
    except Exception as e:
        print(f"Main Error: {e}")

if __name__ == "__main__":
    monitor()
