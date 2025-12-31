# Etimad Tender Analytics Pipeline (KSA)

An automated **data engineering + analytics** pipeline that scrapes public tender listings (Etimad), normalizes and stores **today-only** results in Google Sheets, and generates an **Arabic PDF KPI report** on a daily schedule. The project is designed for operational monitoring of tenders and procurement opportunities with structured reporting and (optionally) a future ML-based classifier once labels are available.

---

## Scientific / Technical Classification

**Domain:** Data Engineering, Information Retrieval, Automated Reporting (Optional: Supervised Learning)  
**System Type:** Daily batch **ETL/ELT pipeline**  
**Core Methods:**
- **Web Scraping & Parsing** (HTML extraction from listing cards)
- **Data Cleaning & Normalization** (Arabic text normalization, numeric/date coercion, deduplication)
- **Lightweight Storage** via **Google Sheets** as a collaborative data layer
- **Descriptive Analytics & KPI Generation** (pandas)
- **Visualization** (matplotlib)
- **Arabic PDF Reporting** (ReportLab + Arabic shaping/bidi)
- **Automated Delivery** (email via SMTP)

**Optional Extension (Deferred):**  
Supervised classification once a `Labels` sheet exists and can be joined reliably using `Reference Number`.

---

## What This Project Does

### Pipeline
1. **Scrape** tender competitions from Etimad (public listing pages)
2. **Normalize** the extracted fields into a consistent schema
3. **Write to Google Sheets** (Sheet1)
   - Keep **today-only** rows in Sheet1/report
   - Highlight today’s rows (visual indicator)
   - Weekly cleanup: remove rows **older than 7 days**
4. **Generate Arabic PDF report** containing:
   1) Greeting page (“السلام عليكم”) + report date/time  
   2) **Today-only table** mirroring Sheet1  
   3) **KPIs by activity** (as per the required KPI structure)  
   4) **Most active days** (weekly trend)  
   5) **Value distribution / summary** (tender values)  
   6) **Daily summary** (count of today’s tenders)  
5. **(Optional)** Send the report via email (SMTP)

---

## Data Schema (Sheet1)

Recommended columns (aligned with the updated requirement):

- Competition Name  
- Reference Number  
- Entity (Agency)  
- Competition Value  
- Inquiry Deadline  
- Submission Deadline  
- Link

> The PDF “Today-only table” is generated to match this schema exactly.

---

## Key Design Rules

- **Today-only visibility:** the sheet and the PDF should reflect **only today’s results**
- **Highlight today’s rows:** rows created on the report date are visually emphasized
- **Weekly cleanup:** delete rows older than **7 days** to keep the sheet lean
- **No ML until labels exist:** classification is postponed until a `Labels` sheet is available and consistent

---

## Tech Stack

- Python
- requests / BeautifulSoup (scraping)
- pandas (data processing)
- matplotlib (charts)
- Google Sheets API (data sync)
- ReportLab (+ Arabic reshaping/bidi) (PDF generation)
- SMTP (email sending)



