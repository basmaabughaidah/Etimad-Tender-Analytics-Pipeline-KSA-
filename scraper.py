# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import quote
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import dateparser

from config import BASE_URL, SEARCH_PATH, KEYWORDS, SHEET_COLUMNS

SEARCH_URL = BASE_URL.rstrip("/") + SEARCH_PATH

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "ar-SA,ar;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml",
    "Connection": "keep-alive",
}

def _is_today(text):
    if not text:
        return False
    t = str(text).strip()
    if "اليوم" in t or "Today" in t:
        return True
    dt = dateparser.parse(t, languages=["ar", "en"])
    return bool(dt and dt.date() == datetime.now().date())

def _grab(label, txt):
    m = re.search(rf"{label}\s*[:：]?\s*([^\n|]+)", txt)
    return m.group(1).strip() if m else ""

def _extract_from_card(card):
    txt = card.get_text(" ", strip=True)
    a   = card.find("a", href=True)
    t   = card.find(["h5","h4","a"])

    link  = a["href"] if a else ""
    link  = link if link.startswith("http") else (BASE_URL.rstrip("/") + link if link else "")
    title = t.get_text(strip=True) if t else ""

    item = {
        "النشاط الاساسي": _grab("النشاط الاساسي", txt) or _grab("نوع المنافسة", txt),
        "اخر توقيت لاستلام الاستفسارات": _grab("اخر توقيت لاستلام الاستفسارات", txt) or _grab("آخر موعد للاستفسارات", txt),
        "قيمة الكراسة": _grab("قيمة الكراسة", txt) or _grab("قيمة وثائق المنافسة", txt),
        "الجهة": _grab("الجهة", txt) or _grab("الجهة الحكومية", txt) or _grab("الجهة الحكومية المعلنة", txt),
        "الرقم المرجعي": _grab("الرقم المرجعي", txt) or _grab("رقم المنافسة", txt) or _grab("رقم المرجع", txt),
        "اخر موعد لتقديم العرض": _grab("اخر موعد لتقديم العرض", txt) or _grab("آخر موعد لتقديم العروض", txt),
        "الرابط": link,
        "العنوان": title,
        "تاريخ نشرها": _grab("تاريخ نشرها", txt) or _grab("تاريخ النشر", txt) or _grab("تاريخ الطرح", txt),
    }
    return item

def _fetch_html(url, tries=3, timeout=30):
    for i in range(tries):
        try:
            r = requests.get(url, headers=HEADERS, timeout=timeout)
            if r.status_code == 200 and ("</html>" in r.text.lower() or r.text.strip()):
                return r.text
        except Exception:
            pass
        time.sleep(1 + i)
    return ""

def scrape_opportunities(keywords=KEYWORDS, require_today=True, per_kw_limit=25, headless=False):
    # headless الوسيط موجود للإتساق مع orchestrator لكنه غير مستخدم هنا
    results, seen = [], set()

    for kw in keywords:
        url = SEARCH_URL + quote(kw)
        html = _fetch_html(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "lxml")

        # بطاقات محتملة
        cards = soup.select("div.card-body")
        if not cards:
            cards = soup.select("div.card")
        if not cards:
            # fallback: حاول نلقط عناصر شبيهة
            cards = soup.select("li, article, div")

        picked = 0
        for c in cards:
            if picked >= per_kw_limit:
                break

            item = _extract_from_card(c)
            if not item["العنوان"] or not item["الرابط"]:
                continue

            pub = item.get("تاريخ نشرها", "")
            if require_today and pub and not _is_today(pub):
                continue

            key = (item.get("الرقم المرجعي",""), item["العنوان"], item["الرابط"])
            if key in seen:
                continue
            seen.add(key)

            # أعِد ترتيب الأعمدة لتطابق Sheet1 تمامًا
            ordered = {col: item.get(col, "") for col in SHEET_COLUMNS}
            results.append(ordered)
            picked += 1

    return results
