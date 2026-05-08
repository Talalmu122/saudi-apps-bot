import requests
import os
import sys

def monitor():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    # رابط أحدث التطبيقات المجانية في السعودية
    url = "https://rss.applemarketingtools.com/api/v2/sa/apps/top-free/10/apps.json"
    
    try:
        response = requests.get(url)
        data = response.json()
        app = data['feed']['results'][0]
        app_id = app['id']

        # منع التكرار
        last_id_file = "last_app_id.txt"
        if os.path.exists(last_id_file):
            with open(last_id_file, "r") as f:
                if f.read().strip() == app_id:
                    print("لا يوجد جديد.")
                    return

        # استخراج البيانات باحترافية
        name = app.get('name', 'N/A')
        artist = app.get('artistName', 'N/A')
        app_url = app.get('url', '#')
        icon_url = app.get('artworkUrl100', '') # أيقونة التطبيق
        genres = ", ".join([g['name'] for g in app.get('genres', [])[:2]]) # التصنيف

        # صياغة الرسالة بـ Markdown
        message = (
            f"<b>🚀 اكتشاف تطبيق سعودي جديد!</b>\n\n"
            f"<b>📦 الاسم:</b> {name}\n"
            f"<b>👨‍💻 المطور:</b> {artist}\n"
            f"<b>📂 التصنيف:</b> {genres}\n\n"
            f"<i>تنبيه آلي بواسطة رادار طلال</i>"
        )

        # إرسال الصورة مع الأزرار
        telegram_url = f"https://api.telegram.org/bot{token}/sendPhoto"
        payload = {
            "chat_id": chat_id,
            "photo": icon_url,
            "caption": message,
            "parse_mode": "HTML",
            "reply_markup": {
                "inline_keyboard": [[
                    {"text": "🔗 فتح في المتجر", "url": app_url}
                ]]
            }
        }
        
        requests.post(telegram_url, json=payload)
        
        with open(last_id_file, "w") as f:
            f.write(app_id)
            
        print(f"Success: Sent {name}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor()
