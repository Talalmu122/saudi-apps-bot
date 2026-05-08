import requests
import os
import sys

def monitor():
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('CHAT_ID')
    
    if not token or not chat_id:
        print("Error: المفاتيح السرية غير موجودة")
        sys.exit(1)

    # الرابط المصحح
    url = "https://rss.applemarketingtools.com/api/v2/sa/apps/top-free/10/apps.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        app = data['feed']['results'][0]
        name = app.get('name', 'N/A')
        artist = app.get('artistName', 'N/A')
        app_url = app.get('url', '#')
        
        message = f"🚀 تطبيق سعودي جديد!\n\nالاسم: {name}\nالمطور: {artist}\n[رابط المتجر]({app_url})"
        
        telegram_url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(telegram_url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        })
        print("Success: تم إرسال الإشعار")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    monitor()
