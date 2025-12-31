# -*- coding: utf-8 -*-

# كلمات البحث
KEYWORDS_AR = [
    "هاكاثون","هاكثون","الهاكاثون","ثون","ثونات","الهاكاثونات","هاكثونات","هاكاثونات",
    "ابتكار","يبتكرون","الابتكار","مبتكرون","نبتكر","ابتكارات","المبتكرون","ابتكاري",
    "فعاليات","فعالية","فعاليه","الفعاليات","الفعالية","الفعاليه"
]
KEYWORDS_EN = ["hackathon","hackathons","innovation","innovate","innovative","event","events","competition","challenge"]
KEYWORDS = KEYWORDS_AR + KEYWORDS_EN

# منصة اعتماد
BASE_URL = "https://portal.etimad.sa/"
SEARCH_PATH = "/ar-sa/search/searchindex?searchText="

# Google Sheets الهدف
SHEET_ID  = "15eOK-kuB2zGOWsNCo1WTu28Xgb8L9Kqzib2UMrHtiwU"
SHEET_TAB = "Sheet1"
SHEET_LINK = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

# الأعمدة المطلوبة بالترتيب في Sheet1
SHEET_COLUMNS = [
    "النشاط الاساسي","اخر توقيت لاستلام الاستفسارات","قيمة الكراسة",
    "الجهة","الرقم المرجعي","اخر موعد لتقديم العرض","الرابط","العنوان","تاريخ نشرها"
]

# مجلد Drive (غير مستخدم حالياً)
DRIVE_FOLDER_ID = "1usCVByq8h-IN2DOXw_buoI9u0vGTCG84"
