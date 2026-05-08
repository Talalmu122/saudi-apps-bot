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

        # نظام منع التكرار الذكي
        last_id_file = "last_app_id.txt"
        if os.path.exists(last_id_file):
            with open(last_id_file, "r") as f:
                if f.read().strip() == app_id:
                    print("لا يوجد تطبيق جديد حالياً.")
                    return

        # استخراج البيانات
        name = app.get('name', 'N/A')
        artist = app.get('artistName', 'N/A')
        app_url = app.get('url', '#')
        
        # --- التعديل السحري للجودة ---
        # نحول الأيقونة من 100 بكسل إلى 512 بكسل لتكون واضحة جداً
        icon_url = app.get('artworkUrl100', '').replace('100x100bb', '512x512bb')
        
        genres = ", ".join([g['name'] for g in app.get('genres', [])[:2]])

        # تنسيق الرسالة بـ HTML لتبدو احترافية
        message = (
            f"<b>🚀 اكتشاف تطبيق سعودي جديد!</b>\n\n"
            f"<b>📦 الاسم:</b> {name}\n"
            f"<b>👨‍💻 المطور:</b> {artist}\n"
            f"<b>📂 التصنيف:</b> {genres}\n\n"
            f"<i>تنبيه آلي بواسطة رادار طلال</i>"
        )

        # إرسال الصورة مع الأزرار التفاعلية
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
        
        # حفظ معرف التطبيق لمنع التكرار في الفحص القادم
        with open(last_id_file, "w") as f:
            f.write(app_id)
            
        print(f"تم الإرسال بنجاح: {name}")
        
    except Exception as e:
        print(f"حدث خطأ: {e}")

if __name__ == "__main__":
    monitor()
