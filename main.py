import requests
import os
import google_play_scraper

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
    
    # 1. قراءة المعرفات القديمة إذا كانت موجودة
    old_ids = set()
    if os.path.exists(last_id_file):
        with open(last_id_file, "r") as f:
            old_ids = set(f.read().splitlines())

    current_ids = set()
    to_send = []

    try:
        # فحص آبل
        apple_url = "https://rss.applemarketingtools.com/api/v2/sa/apps/top-free/10/apps.json"
        apple_res = requests.get(apple_url).json()
        for app in apple_res['feed']['results']:
            aid = f"apple_{app['id']}"
            current_ids.add(aid)
            if aid not in old_ids:
                icon = app['artworkUrl100'].replace('100x100bb', '512x512bb')
                to_send.append((app['name'], app['artistName'], app['url'], icon, "Apple Store 🍏"))

        # فحص جوجل بلاي
        google_results = google_play_scraper.search("Saudi Arabia", lang="ar", country="sa", n_hits=10)
        for g_app in google_results:
            gid = f"google_{g_app['appId']}"
            current_ids.add(gid)
            if gid not in old_ids:
                g_url = f"https://play.google.com/store/apps/details?id={g_app['appId']}"
                to_send.append((g_app['title'], g_app.get('developer', 'N/A'), g_url, g_app['icon'], "Google Play 🤖"))

        # 2. إرسال التطبيقات الجديدة فقط
        for item in to_send:
            send_telegram(token, chat_id, *item)

        # 3. حفظ كل المعرفات الحالية لتكون "ذاكرة" للمرة القادمة
        with open(last_id_file, "w") as f:
            f.write("\n".join(current_ids))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor()
