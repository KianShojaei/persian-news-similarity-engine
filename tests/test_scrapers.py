"""Unit tests for Eitaa and Soroush Plus scrapers."""

from src.scrapers.eitaa import EitaaScraper
from src.scrapers.soroush import SoroushScraper

MOCK_EITAA_HTML = (
    "<!DOCTYPE html><html><body>"
    "<div class='etme_widget_message_text'>کوتاه</div>"
    "<div class='etme_widget_message_text'>"
    "خبر اول: نرخ تورم سالانه در اردیبهشت ماه با کاهش قابل توجه به رقم ۳۵ درصد رسید و روند نزولی ادامه دارد."
    "</div>"
    "<div class='etme_widget_message_text'>"
    "خبر دوم: سازمان هواشناسی اعلام کرد<br>سامانه بارشی جدید به زودی وارد کشور خواهد شد و بارش‌ها گسترش می‌یابد."
    "</div>"
    "</body></html>"
)

MOCK_SOROUSH_HTML = (
    "<!DOCTYPE html><html><body>"
    "<header><p>پیام‌رسان سروش+ مشاهده در نسخه وب</p></header>"
    "<div class='message-text'>"
    "گزارش بانک مرکزی در سروش پلاس: تسهیلات پرداختی به بخش مسکن و تولید در شش ماهه نخست سال رشد چشمگیری را ثبت کرد."
    "</div>"
    "<div class='message-text'>خیلی کوتاه</div>"
    "<div class='message-text'>"
    "خبرگزاری تسنیم: سازمان هواشناسی کشور نسبت به وقوع سیلاب در ۱۰ استان کشور هشدار جدی صادر نمود و بر لزوم احتیاط تاکید کرد."
    "</div>"
    "<footer><p>دریافت سروش+</p></footer>"
    "</body></html>"
)


def test_eitaa_channel_sanitization() -> None:
    scraper = EitaaScraper()
    assert scraper.sanitize_channel("@farsna") == "farsna"
    assert scraper.sanitize_channel("https://eitaa.com/farsna/") == "farsna"


def test_eitaa_parse_posts() -> None:
    scraper = EitaaScraper()
    posts = scraper.parse_posts(MOCK_EITAA_HTML, limit=10)
    assert len(posts) == 2
    assert "خبر دوم" in posts[0]
    assert "اعلام کرد سامانه" in posts[0]


def test_soroush_channel_sanitization() -> None:
    scraper = SoroushScraper()
    assert scraper.sanitize_channel("@tasnimnews") == "tasnimnews"
    assert scraper.sanitize_channel("https://splus.ir/tasnimnews/") == "tasnimnews"


def test_soroush_parse_posts() -> None:
    scraper = SoroushScraper()
    posts = scraper.parse_posts(MOCK_SOROUSH_HTML, limit=10)
    assert len(posts) == 2
    assert any("تسهیلات پرداختی" in p for p in posts)
    assert any("سازمان هواشناسی کشور" in p for p in posts)


def test_soroush_fallback_parsing() -> None:
    fallback_html = (
        "<div><p>"
        "این یک خبر آزمایشی با ساختار متفاوت در صفحات وب سروش پلاس است که شامل متنی طولانی جهت تست استخراج است."
        "</p></div>"
    )
    scraper = SoroushScraper()
    posts = scraper.parse_posts(fallback_html, limit=5)
    assert len(posts) == 1
    assert "سروش پلاس" in posts[0]
