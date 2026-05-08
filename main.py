import requests
import os
from google_play_scraper import search
import io

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

def send_to_telegram_with_photo(title, developer, link, icon_url, store_name):
    # تنسيق الرسالة بشكل جمالي
    caption = (
        f"🚀 <b>تطبيق سعودي جديد رصده الرادار!</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>📱 التطبيق:</b> {title}\n"
        f"<b>🏢 المطور:</b> {developer}\n"
        f"<b>🏪 المتجر:</b> {store_name}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📍 <i>رادار طلال للبرامج السعودية</i>"
    )
    
    # رابط إرسال الصورة في تليجرام
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    
    payload = {
        "chat_id": CHAT_ID,
        "photo": icon_url, # نرسل رابط الصورة مباشرة لتليجرام ليرسلها كصورة
        "caption": caption,
        "parse_mode": "HTML",
        "reply_markup": {
            "inline_keyboard": [[{"text": "📥 تحميل التطبيق", "url": link}]]
        }
    }
    
    try:
        r = requests.post(url, json=payload)
        # إذا فشل إرسال الصورة (مثلاً الرابط خربان)، نرسلها كنص عادي عشان ما نفوت التطبيق
        if r.status_code != 200:
            print(f"فشل إرسال الصورة لـ {title}، جاري الإرسال كنص.")
            # هنا كود الإرسال النصي الاحتياطي
            text_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
            text_payload = payload.copy()
            text_payload["text"] = caption + f"\n\n🖼 <a href='{icon_url}'>عرض الأيقونة</a>"
            del text_payload["photo"]
            del text_payload["caption"]
            requests.post(text_url, json=text_payload)
    except Exception as e:
        print(f"خطأ غير متوقع في الإرسال: {e}")

def hunt_android():
    print("جاري فحص أندرويد بالصور...")
    keywords = ["السعودية", "SAUDI", "توصيل", "المدينة المنورة", "متجر"]
    for kw in keywords:
        try:
            results = search(kw, lang='ar', country='sa', n_hits=10)
            for app in results:
                app_id = app['appId']
                if not is_sent(app_id):
                    title = app.get('title', 'بدون اسم')
                    developer = app.get('developer', 'مطور غير معروف')
                    link = f"https://play.google.com/store/apps/details?id={app_id}"
                    # جوجل يعطي الأيقونة بجودة جيدة
                    icon_url = app.get('icon', '')
                    
                    if icon_url:
                        send_to_telegram_with_photo(title, developer, link, icon_url, "Google Play")
                        save_to_memory(app_id)
                    else:
                        print(f"تطبيق {title} بدون أيقونة، تخطي.")

        except Exception as e:
            print(f"خطأ في أندرويد: {e}")

def hunt_apple():
    print("جاري فحص آبل بالصور عالية الجودة...")
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
                
                # جلب الأيقونة الأساسية (جودتها ضعيفة 100x100)
                low_res_icon = entry['im:image'][2]['label'] 
                
                # 🛠 الخدعة: تغيير الرابط لطلب جودة 1000x1000 بيكسل
                high_res_icon = low_res_icon.replace("100x100bb", "1000x1000bb")
                
                send_to_telegram_with_photo(title, developer, link, high_res_icon, "App Store")
                save_to_memory(app_id)
    except Exception as e:
        print(f"خطأ في جلب بيانات آبل: {e}")

if __name__ == "__main__":
    if not TOKEN or not CHAT_ID:
        print("خطأ: تأكد من Secrets")
    else:
        hunt_android()
        hunt_apple()
