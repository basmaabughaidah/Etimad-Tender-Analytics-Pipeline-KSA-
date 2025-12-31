"""
📊 Reporter Module - Monthly Report Generation (Arabic Supported)
Generates monthly PDF reports with charts using Amiri font and Arabic text reshaping
"""

import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fpdf import FPDF
import calendar
from email_sender import send_report_via_email
import arabic_reshaper
from bidi.algorithm import get_display


# ================================================================
# 📘 Simple PDF Class with Arabic Support
# ================================================================
class SimplePDF(FPDF):
    """Simple PDF class with Arabic (RTL) support using Amiri font"""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

        # Load Amiri font for Arabic support
        try:
            self.add_font('Amiri', '', 'amiri-regular.ttf', uni=True)
            self.add_font('Amiri', 'B', 'amiri-regular.ttf', uni=True)
            self.font_loaded = True
        except Exception as e:
            self.font_loaded = False
            print(f"⚠️ Amiri font not found or error loading: {e}, using default font")

    def reshape_text(self, text):
        """Reshape Arabic text properly"""
        try:
            return get_display(arabic_reshaper.reshape(str(text)))
        except Exception:
            return text

    def header(self):
        """Page header"""
        self.set_font('Amiri', 'B', 16)
        self.cell(0, 10, self.reshape_text('تقرير الفرص'), align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        """Page footer"""
        self.set_y(-15)
        self.set_font('Amiri', '', 8)
        page_label = f'صفحة {self.page_no()}'
        self.cell(0, 10, self.reshape_text(page_label), align='C')

    def chapter_title(self, title):
        """Section title"""
        self.set_font('Amiri', 'B', 14)
        self.set_fill_color(200, 220, 255)
        reshaped_title = self.reshape_text(title)
        self.cell(0, 10, reshaped_title, new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(4)

    def chapter_body(self, text):
        """Body text"""
        self.set_font('Amiri', '', 11)
        reshaped_text = self.reshape_text(text)
        self.multi_cell(0, 6, reshaped_text, align='R')
        self.ln()

    def add_image_centered(self, image_path, width=180):
        """Add centered image"""
        if os.path.exists(image_path):
            img_x = (self.w - width) / 2
            self.image(image_path, x=img_x, y=None, w=width)
            self.ln(5)


# ================================================================
# 🎨 Chart Setup
# ================================================================
def setup_display():
    """Setup matplotlib"""
    plt.style.use('seaborn-v0_8-darkgrid')
    plt.rcParams['figure.facecolor'] = 'white'
    plt.rcParams['font.family'] = 'Amiri'
    plt.rcParams['axes.unicode_minus'] = False


def create_keyword_chart(df, save_path):
    """Keywords chart (Arabic)"""
    try:
        fig, ax = plt.subplots(figsize=(10, 5))
        keyword_counts = df['keyword'].value_counts().head(10)

        # 🔹 Reshape Arabic labels
        reshaped_labels = [get_display(arabic_reshaper.reshape(str(k))) for k in keyword_counts.index]

        ax.barh(reshaped_labels, keyword_counts.values, color='steelblue')
        ax.set_title(get_display(arabic_reshaper.reshape('أهم الكلمات')), fontsize=12, fontweight='bold')
        ax.set_xlabel(get_display(arabic_reshaper.reshape('عدد مرات الظهور')))
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
        print("✅ Keywords chart created (Arabic)")
    except Exception as e:
        print(f"❌ Keywords chart error: {e}")


def create_classification_chart(df, save_path):
    """Classification chart"""
    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        reshaped_labels = [get_display(arabic_reshaper.reshape(str(l))) for l in df['classification'].value_counts().index]
        df['classification'].value_counts().plot(kind='pie', labels=reshaped_labels, ax=ax, autopct='%1.1f%%')
        ax.set_title(get_display(arabic_reshaper.reshape('توزيع التصنيفات')), fontsize=12, fontweight='bold')
        ax.set_ylabel('')
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
        print("✅ Classification chart created (Arabic)")
    except Exception as e:
        print(f"❌ Classification chart error: {e}")


def create_timeline_chart(df, save_path):
    """Timeline chart"""
    try:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        daily = df.groupby(df['date'].dt.date).size()

        fig, ax = plt.subplots(figsize=(12, 5))
        daily.plot(ax=ax, marker='o', color='steelblue', linewidth=2)
        ax.set_title(get_display(arabic_reshaper.reshape('الفرص اليومية')), fontsize=12, fontweight='bold')
        ax.set_xlabel(get_display(arabic_reshaper.reshape('التاريخ')))
        ax.set_ylabel(get_display(arabic_reshaper.reshape('عدد الفرص')))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
        print("✅ Timeline chart created (Arabic)")
    except Exception as e:
        print(f"❌ Timeline chart error: {e}")


# ================================================================
# 📄 Main Report Generator
# ================================================================
def generate_monthly_report(results_data, report_folder="data/reports"):
    """Generate simple monthly PDF report with Arabic support"""

    print("\n📊 Generating monthly report...")

    # Convert to DataFrame
    if isinstance(results_data, list):
        df = pd.DataFrame(results_data)
    else:
        df = results_data.copy()

    if df.empty:
        print("⚠️ No data to report")
        return

    os.makedirs(report_folder, exist_ok=True)

    current_date = datetime.now()
    month_name = calendar.month_name[current_date.month]
    base_filename = f"{current_date.year}_{month_name}"

    try:
        setup_display()

        # Create charts
        print("📈 Creating charts...")
        chart_dir = os.path.join(report_folder, "charts")
        os.makedirs(chart_dir, exist_ok=True)

        chart_paths = {
            'keywords': os.path.join(chart_dir, "keywords.png"),
            'classification': os.path.join(chart_dir, "classification.png"),
            'timeline': os.path.join(chart_dir, "timeline.png"),
        }

        create_keyword_chart(df, chart_paths['keywords'])
        create_classification_chart(df, chart_paths['classification'])
        create_timeline_chart(df, chart_paths['timeline'])

        # Create PDF
        print("📄 Creating PDF...")
        pdf = SimplePDF()

        # Page 1: Summary
        pdf.add_page()
        pdf.chapter_title("ملخص التقرير")

        if 'relevance_score' in df.columns:
            avg_relevance = f"{df['relevance_score'].mean():.1%}"
        else:
            avg_relevance = "N/A"

        summary_text = f"""تم الإنشاء في: {datetime.now().strftime('%d/%m/%Y %H:%M')}
الفترة: {month_name} {current_date.year}
العميل: غفران أ.

الإحصائيات الأساسية:
- عدد الفرص الإجمالي: {len(df)}
- عدد الكلمات المفتاحية الفريدة: {df['keyword'].nunique()}
- متوسط نسبة الأهمية: {avg_relevance}
"""
        pdf.chapter_body(summary_text)

        # Page 2: Keywords
        pdf.add_page()
        pdf.chapter_title("تحليل الكلمات المفتاحية")
        pdf.add_image_centered(chart_paths['keywords'])

        kw_text = "أعلى الكلمات المفتاحية:\n"
        for keyword, count in df['keyword'].value_counts().head(5).items():
            kw_text += f"- {keyword}: {count}\n"
        pdf.chapter_body(kw_text)

        # Page 3: Classification
        pdf.add_page()
        pdf.chapter_title("توزيع التصنيفات")
        pdf.add_image_centered(chart_paths['classification'], 140)

        # Page 4: Timeline
        pdf.add_page()
        pdf.chapter_title("الخط الزمني للفرص")
        pdf.add_image_centered(chart_paths['timeline'])

        # Page 5: Conclusions
        pdf.add_page()
        pdf.chapter_title("الاستنتاجات والتوصيات")

        conclusion_text = """النتائج:
- تم تحليل جميع الفرص بنجاح
- تم تمثيل البيانات في المخططات السابقة
- تظهر الكلمات المفتاحية أنماط توزيع واضحة

التوصيات:
- مراجعة الفرص الأعلى أهمية أولاً
- التركيز على الكلمات المفتاحية الأكثر تكراراً
- متابعة الاتجاهات بشكل دوري
- تحديث عوامل التصفية بناءً على النتائج
"""
        pdf.chapter_body(conclusion_text)

        # Save PDF
        pdf_path = os.path.join(report_folder, f"{base_filename}_report.pdf")
        pdf.output(pdf_path)
        print(f"✅ PDF saved: {pdf_path}")

        # Save text summary
        summary_path = os.path.join(report_folder, f"{base_filename}_summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(f"تقرير الشهر: {month_name} {current_date.year}\n")
            f.write("="*50 + "\n\n")
            f.write(f"عدد الفرص: {len(df)}\n")
            f.write(f"الكلمات المفتاحية الفريدة: {df['keyword'].nunique()}\n\n")
            f.write("تفاصيل الكلمات المفتاحية:\n")
            f.write(df['keyword'].value_counts().to_string())

        print(f"✅ Summary saved: {summary_path}")
        print(f"✅ Report completed!\n")

        # Send email (optional)
        try:
            send_report_via_email(pdf_path)
        except Exception as e:
            print(f"⚠️ Email not sent: {e}")

    except Exception as e:
        print(f"❌ Report error: {e}")
        import traceback
        traceback.print_exc()


# ================================================================
# 🧪 Test Run
# ================================================================
if __name__ == "__main__":
    test_data = [
        {"keyword": "فرصة تدريب", "title": "اختبار 1", "date": "2025-01-01", "classification": "عالية", "relevance_score": 0.85},
        {"keyword": "منحة", "title": "اختبار 2", "date": "2025-01-02", "classification": "متوسطة", "relevance_score": 0.70},
        {"keyword": "فرصة تدريب", "title": "اختبار 3", "date": "2025-01-03", "classification": "عالية", "relevance_score": 0.95},
    ]
    generate_monthly_report(test_data)
