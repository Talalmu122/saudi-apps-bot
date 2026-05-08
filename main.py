import requests
import os
import sys

def monitor():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    url = "https://rss.applemarketingtools.com/api/v2/sa/apps/top-free/10/apps.json"
    
    try:
        response = requests.get(url)
        data = response.json()
        app = data['feed']['results'][0]
        app_id = app['id'] # معرف فريد للتطبيق

        # ملف مؤقت في سيرفر جيت هاب يحفظ آخر ID أرسلناه
        last_id_file = "last_app_id.txt"
        
        # إذا الملف موجود، نقرأ الـ ID القديم
        if os.path.exists(last_id_file):
            with open(last_id_file, "r") as f:
                if f.read().strip() == app_id:
                    print("لا يوجد تطبيق جديد، لن يتم إرسال رسالة.")
                    return

        # إذا وصلنا هنا، يعني التطبيق جديد!
        name = app.get('name', 'N/A')
        artist = app.get('artistName', 'N/A')
        app_url = app.get('url', '#')
        
        message = f"🚀 تطبيق جديد تم اكتشافه!\n\nالاسم: {name}\nالمطور: {artist}\n[رابط المتجر]({app_url})"
        
        telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(telegram_url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        
        # حفظ الـ ID الجديد عشان ما يتكرر
        with open(last_id_file, "w") as f:
            f.write(app_id)
            
        print(f"Success: تم إرسال {name}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor()
