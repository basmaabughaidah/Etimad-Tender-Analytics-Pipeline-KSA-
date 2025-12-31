# -*- coding: utf-8 -*-
import os
import sys

# إضافة مسار هذا الملف إلى مسارات بايثون لضمان رؤية modules المجاورة (مثل scraper.py)
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# محاولة الاستيراد بالطريقة المعتادة
try:
    from scraper import scrape_opportunities
except ModuleNotFoundError:
    # خطة بديلة: تحميل scraper.py مباشرة من المسار الكامل
    import importlib.util
    scr_path = os.path.join(HERE, "scraper.py")
    spec = importlib.util.spec_from_file_location("scraper", scr_path)
    scraper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scraper)
    scrape_opportunities = scraper.scrape_opportunities

from sheets_handler import update_sheet
from config import KEYWORDS, SHEET_LINK

def main(headless=False):
    items = scrape_opportunities(KEYWORDS, require_today=True, headless=headless)
    if not items:
        print("لا نتائج منشورة اليوم بالكلمات المحددة.")
        print("الشيت:", SHEET_LINK)
        return
    update_sheet(items)
    print("تم تحديث Sheet1.")
    print("الشيت:", SHEET_LINK)

if __name__ == "__main__":
    main(headless=False)
