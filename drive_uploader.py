from __future__ import print_function
import os
import pickle
import re
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from config import DRIVE_FOLDER_ID

# الصلاحيات المطلوبة (Drive + Sheets معاً)
SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/spreadsheets'
]

def sanitize_filename(name, idx=0):
    """تنظيف اسم الملف من الرموز غير المسموح بها"""
    if not isinstance(name, str):
        name = str(name)
    
    name = name.strip()
    
    # إذا كان فارغ، استخدم رقم الصف
    if not name or name.lower() in ["n/a", "nan", "none", ""]:
        return f"Item_{idx+1}"
    
    # إزالة الرموز غير المسموح بها في أسماء الملفات
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", name)
    return sanitized if sanitized else f"Item_{idx+1}"


def upload_to_drive(results):
    """يرفع الملفات إلى Google Drive"""
    creds = None

    # تحميل التوكن لو موجود

    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"⚠️ Error loading token.json: {e}")
            creds = None

    # تسجيل الدخول لأول مرة
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    uploaded_files = []

    # قراءة البيانات
    if isinstance(results, str) and results.endswith('.csv'):
        if not os.path.exists(results):
            print(f"⚠️ الملف '{results}' غير موجود!")
            return []
        df = pd.read_csv(results)
    else:
        df = pd.DataFrame(results)

    if df.empty:
        print("⚠️ لا توجد بيانات للرفع.")
        return []

    os.makedirs("data", exist_ok=True)

    print(f"🚀 جاري رفع {len(df)} ملف إلى Google Drive...")

    valid_count = 0
    skipped_count = 0

    for idx, row in df.iterrows():
        try:
            # استخراج العنوان وتنظيفه
            raw_title = str(row.get('title', '')).strip()
            title = sanitize_filename(raw_title)
            
            # تخطي الصفوف الفارغة
            if not title:
                print(f"⏭️ تم تخطي صف بدون عنوان صالح (صف {idx + 2})")
                skipped_count += 1
                continue

            file_name = f"{title}.txt"
            file_path = os.path.join("data", file_name)

            # كتابة محتوى الملف
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"الكلمة المفتاحية: {row.get('keyword', 'N/A')}\n")
                f.write(f"العنوان: {raw_title}\n")
                f.write(f"الرابط: {row.get('link', 'N/A')}\n")
                if 'date' in row and pd.notna(row['date']):
                    f.write(f"التاريخ: {row['date']}\n")
                if 'description' in row and pd.notna(row['description']):
                    f.write(f"الوصف: {row['description']}\n")

            # رفع الملف
            file_metadata = {'name': file_name, 'parents': [DRIVE_FOLDER_ID]}
            media = MediaFileUpload(file_path, mimetype='text/plain')

            uploaded = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            uploaded_files.append({
                "keyword": row.get('keyword', ''),
                "title": title,
                "file_id": uploaded.get("id"),
                "link": row.get('link', '')
            })

            print(f"✅ تم رفع: {file_name}")
            valid_count += 1

        except Exception as e:
            print(f"⚠️ فشل رفع الصف {idx + 2}: {e}")
            skipped_count += 1
            continue

    print(f"\n📊 النتائج:")
    print(f"   • ملفات مرفوعة بنجاح: {valid_count}")
    print(f"   • صفوف تم تخطيها: {skipped_count}")
    print(f"🎉 انتهى! تم رفع {len(uploaded_files)} ملف بنجاح.")
    
    return uploaded_files


if __name__ == "__main__":
    # مثال بسيط للاختبار
    test_data = [
        {
            "keyword": "هاكاثون",
            "title": "فرصة تجريبية",
            "link": "https://portal.etimad.sa",
            "date": "2025-01-15"
        }
    ]
    upload_to_drive(test_data)