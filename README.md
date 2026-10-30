# 📰 Persian News Similarity Engine (Eitaa & Soroush Plus)
# سامانه هوشمند استخراج و تشابه‌سنجی اخبار فارسی (ایتا و سروش‌پلاس)

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FAISS](https://img.shields.io/badge/Vector%20Search-FAISS%20IndexFlatIP-green.svg)](https://github.com/facebookresearch/faiss)
[![Scikit-Learn](https://img.shields.io/badge/TF--IDF%20%26%20Cosine-Scikit--Learn-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Embeddings](https://img.shields.io/badge/Neural%20Model-MiniLM--L12--v2-orange.svg)](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
[![Tests](https://img.shields.io/badge/Tests-21%20Passed%20(Pytest)-brightgreen.svg?logo=pytest)](https://docs.pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

یک سامانه جامع، ناهمگام (Asynchronous) و مهندسی‌شده برای درس **داده‌کاوی (Data Mining)** و **پردازش زبان طبیعی (NLP)** که آخرین اخبار عمومی را به‌صورت بلادرنگ (Real-time) از دو پیام‌رسان بومی **ایتا (`eitaa.com`)** و **سروش‌پلاس (`splus.ir`)** استخراج کرده، متن فارسی را طی یک خط‌لوله (Pipeline) سه‌مرحله‌ای پالایش می‌کند و میزان تشابه دو خبر را با سه معیار ریاضی **تشابه کسینوسی برداری (FAISS Cosine Similarity)**، **تشابه کسینوسی واژگانی (TF-IDF Cosine Similarity)** و **تشابه مجموعه‌ای ژاکارد (Jaccard Similarity)** مورد سنجش و رتبه‌بندی قرار می‌دهد.

---

## 🎥 ویدیوی دموی محیط برنامه (Project Demo Video)

در پیش‌نمایش زنده زیر می‌توانید نحوه کارکرد بلادرنگ سامانه، استخراج هم‌زمان اخبار از ایتا و سروش‌پلاس، محاسبه معیارهای تشابه کسینوسی و ژاکارد، نمایش کلیدواژه‌های مشترک و مراحل پیش‌پردازش متن فارسی را مشاهده فرمایید:

<div align="center">
  <a href="https://github.com/KianShojaei/persian-news-similarity-engine/raw/main/Video/demo.mp4">
    <img src="./Video/preview.gif" alt="Project Demo Preview" width="100%" style="border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.2);" />
  </a>
  <br/>
  <p>🎬 <b><a href="https://github.com/KianShojaei/persian-news-similarity-engine/raw/main/Video/demo.mp4">دانلود و تماشای ویدیوی کامل با کیفیت اصلی (MP4)</a></b></p>
</div>

---

## 📌 معماری کلان سیستم (System Architecture)

معماری این سامانه بر پایه طراحی ماژولار و جداسازی کامل لایه‌ها (Separation of Concerns) در ۴ لایه اصلی پیاده‌سازی شده است:

```mermaid
flowchart TB
    subgraph Layer1 ["۱. لایه واکشی ناهمگام داده‌ها - Async Scraping Layer"]
        EitaaWeb["Eitaa Web Preview (eitaa.com/channel)"] -->|httpx.AsyncClient + BS4| EScraper["EitaaScraper (DOM Parser & Newest First)"]
        SoroushAPI["Soroush Plus Vitrin API (vitrin.splus.ir)"] -->|MD5 Signed POST Request| SScraper["SoroushScraper (meta/get & channel/archive)"]
    end

    subgraph Layer2 ["۲. لایه پیش‌پردازش متن فارسی - Persian NLP Pipeline"]
        EScraper & SScraper --> Norm["PersianNormalizer: یکسان‌سازی ی/ک عربی، حذف اعراب و نیم‌فاصله"]
        Norm --> Clean["TextCleaner: حذف لینک‌ها، آیدی‌ها، ایموجی‌ها، ارقام و علائم نگارشی"]
        Clean --> Stop["StopwordFilter: حذف ۱۲۰+ کلمه توقف فارسی و استخراج کلیدواژه‌های مشترک"]
    end

    subgraph Layer3 ["۳. لایه موتورهای تشابه‌سنجی داده‌کاوی - Similarity Engines"]
        Stop --> FAISSEng["FaissSimilarityEngine: FAISS IndexFlatIP Cosine Search (Fast N-Gram & Neural MiniLM)"]
        Stop --> TFIDFEng["LexicalSimilarityEngine: Word-Level TF-IDF Vectorizer + Cosine Similarity"]
        Stop --> JaccardEng["Jaccard Set Engine: نسبت اشتراک به اجتماع مجموعه‌های واژگانی"]
    end

    subgraph Layer4 ["۴. لایه رابط کاربری تعاملی - Interactive RTL Streamlit UI"]
        FAISSEng & TFIDFEng & JaccardEng --> Dashboard["داشبورد تحلیلی راست‌چین با فونت وزیرمتن، کارت‌های امتیاز و رتبه‌بندی خودکار"]
    end
```

---

## 🛠️ چالش‌های وب‌اسکریپینگ و نحوه غلبه بر آن‌ها (Scraper Engineering)

یکی از مهم‌ترین چالش‌های فنی این پروژه، تفاوت بنیادین معماری وب در دو پیام‌رسان **ایتا** و **سروش‌پلاس** بود که بدون استفاده از ابزارهای سنگین و کندی مثل Selenium یا Playwright، صرفاً با درخواست‌های ناهمگام (`httpx.AsyncClient`) حل شد:

### ۱. نحوه عملکرد اسکریپر ایتا (`EitaaScraper`)
* سرور ایتا در آدرس `https://eitaa.com/{channel}` یک صفحه SSR (Server-Side Rendered) برمی‌گرداند که پیام‌ها در تگ‌های `div.etme_widget_message_text` قرار دارند.
* چالش اول در ایتا این است که پیام‌ها در HTML از **قدیمی‌ترین (بالای صفحه) به جدیدترین (پایین صفحه)** چیده شده‌اند. اسکریپر ما لیست نودها را معکوس (`reversed`) می‌کند تا همیشه **خبر شماره ۱، جدیدترین خبر منتشرشده در کانال** باشد.
* همچنین تگ‌های `<br>` پیش از استخراج متن با فاصله جایگزین می‌شوند تا کلمات دو خط متوالی به هم نچسبند و پیام‌های کوتاه‌تر از ۳۵ کاراکتر (مانند استیکرها یا کپشن‌های تک‌کلمه‌ای) فیلتر می‌شوند.

### ۲. مهندسی معکوس API امضاشده سروش‌پلاس (`SoroushScraper`)
* **چالش بزرگ:** برخلاف ایتا، وقتی به آدرس `https://splus.ir/{channel}` درخواست HTTP زده می‌شود، سرور تنها یک پوسته خالی React (`<div id="root"></div>`) به همراه پیام `You need to enable JavaScript to run this app` برمی‌گرداند و هیچ متنی از خبرها در HTML وجود ندارد!
* **راه‌حل مهندسی‌شده:** با تحلیل باندل جاوااسکریپت ویترین سروش‌پلاس (`vitrin.splus.ir`)، مکانیزم ارتباطی کلاینت با سرور کشف و در پایتون پیاده‌سازی شد. سرور سروش‌پلاس برای هر درخواست، یک **امضای دیجیتال مبتنی بر هش `MD5`** تولید می‌کند:

```mermaid
sequenceDiagram
    autonumber
    participant App as SoroushScraper (Python)
    participant Hash as MD5 Signature Generator
    participant API as Soroush Vitrin API (vitrin.splus.ir)

    Note over App,Hash: مرحله اول: دریافت شناسه یکتای کانال (meta/get)
    App->>Hash: Sign(SecretKey + json + AppID + meta/get + lookup_payload)
    Hash-->>App: 32-char MD5 Hex Signature
    App->>API: POST /srvcs-app/v1/json/{AppID}/{MD5_Hash}/meta/get
    API-->>App: JSON Response (internal_channel_uuid)

    Note over App,Hash: مرحله دوم: واکشی آرشیو آخرین پیام‌ها (channel/archive)
    App->>Hash: Sign(SecretKey + json + AppID + channel/archive + channel_id_payload)
    Hash-->>App: 32-char MD5 Hex Signature
    App->>API: POST /srvcs-app/v1/json/{AppID}/{MD5_Hash}/channel/archive
    API-->>App: JSON Array of Latest Channel Messages (Newest First)
```

* به لطف این معماری: برنامه در کسری از ثانیه، بدون نیاز به اجرای مرورگر، آخرین اخبار هر کانال سروش‌پلاس را دقیقاً از **جدیدترین پیام به سمت پیام‌های قبلی** (کاملاً هم‌تراز با ایتا) واکشی می‌کند و در صورت نیاز به تعداد خبرهای بیشتر (مثلاً ۲۵ خبر)، صفحه‌بندی (Pagination) را با پارامتر `message_id` ادامه می‌دهد.

---

## 🧹 خط‌لوله پیش‌پردازش متن فارسی (Persian NLP Pipeline)

مقایسه مستقیم متون خام خبری به دلیل تفاوت در کیبوردهای عربی/فارسی، لینک‌های تبلیغاتی انتهای پیام‌ها و افعال ربط، دقت الگوریتم‌های داده‌کاوی را به شدت کاهش می‌دهد. به همین منظور، هر خبر پیش از ورود به موتور تشابه‌سنجی از ۳ مرحله زیر عبور می‌کند:

| مرحله | ماژول | عملیات انجام‌شده | نمونه تغییر روی متن |
| :--- | :--- | :--- | :--- |
| **۰. متن خام** | `Scraper` | دریافت متن اولیه از ایتا و سروش‌پلاس | `بانك مركزي در https://splus.ir/tasnim اعلام كرد: سود ۳۰٪ ابلاغ شد! 🚀 @tasnim` |
| **۱. نرمال‌سازی** | `PersianNormalizer` | تبدیل حروف عربی (`ي` به `ی`، `ك` به `ک`، `ة` به `ه`)، حذف کامل اعراب و تشدید (دسته یونیکد `Mn`) و استانداردسازی نیم‌فاصله (`\u200c`) | `بانک مرکزی در https://splus.ir/tasnim اعلام کرد: سود ۳۰٪ ابلاغ شد! 🚀 @tasnim` |
| **۲. پاک‌سازی نویز** | `TextCleaner` | حذف URLها (`eitaa.com`, `splus.ir`, `http`)، منشن‌ها (`@`)، ایموجی‌ها، اعداد فارسی/عربی/انگلیسی و علائم نگارشی | `بانک مرکزی در اعلام کرد سود ابلاغ شد` |
| **۳. حذف کلمات توقف** | `StopwordFilter` | حذف بیش از ۱۲۰ کلمه توقف (Stopwords) پرتکرار فارسی (*از، به، در، که، کرد، شد، است...*) و حروف تک‌کاراکتری | `بانک مرکزی اعلام سود ابلاغ` |

علاوه بر این، متد `extract_shared_tokens` اشتراک کلمات کلیدی باقی‌مانده بین دو خبر را استخراج کرده و در رابط کاربری به عنوان **کلیدواژه‌های مشترک** نمایش می‌دهد.

---

## 📐 مبانی ریاضی و الگوریتم‌های تشابه‌سنجی (Similarity Metrics)

طبق اصول درس داده‌کاوی، این سامانه به جای اکتفا به یک عدد، تشابه دو خبر را از **۳ دیدگاه ریاضی مکمل** محاسبه و مقایسه می‌کند:

### ۱. تشابه کسینوسی واژگانی (Lexical TF-IDF Cosine Similarity)
در این روش، ابتدا برای دو خبر پالایش‌شده، ماتریس **TF-IDF** (حاصل‌ضرب فراوانی واژه در عکس فراوانی سند) با پشتیبانی از نیم‌فاصله فارسی ساخته می‌شود:

$$\text{TF-IDF}(t, d) = \text{TF}(t, d) \times \left( \ln\frac{1 + N}{1 + \text{DF}(t)} + 1 \right)$$

سپس زاویه کسینوسی بین دو بردار وزن‌دار $\mathbf{x}_{\text{tfidf}}$ و $\mathbf{y}_{\text{tfidf}}$ محاسبه می‌گردد:

$$S_{\text{lexical}}(\mathbf{x}, \mathbf{y}) = \cos(\theta) = \frac{\mathbf{x}_{\text{tfidf}} \cdot \mathbf{y}_{\text{tfidf}}}{\|\mathbf{x}_{\text{tfidf}}\|_2 \, \|\mathbf{y}_{\text{tfidf}}\|_2} \in [0, 1]$$

* **تحلیل:** این معیار زمانی نمره بالا می‌دهد که هر دو خبرگزاری از **واژگان دقیقاً یکسان** استفاده کرده باشند.

---

### ۲. تشابه کسینوسی برداری و معنایی با FAISS (`FaissSimilarityEngine`)
در دنیای واقعی، دو خبرگزاری ممکن است یک خبر واحد را با مشتقات واژگانی متفاوت (مثلاً *«بارش‌ها»* و *«بارندگی»*) یا کلمات هم‌معنی (مثلاً *«تورم»* و *«گرانی»*) منتشر کنند. در این حالت TF-IDF معمولی نمره پایینی می‌دهد.

برای حل این مشکل، بردارهای متراکم (Dense Embeddings) به طول واحد ($L_2$ Normalized: $\|\mathbf{u}\|_2 = \|\mathbf{v}\|_2 = 1$) ساخته شده و وارد نمایه‌ساز برداری **`faiss.IndexFlatIP`** (محصول پژوهشی Meta AI) می‌شوند. از آنجا که بردارها نرمال شده‌اند، ضرب داخلی (Inner Product) در FAISS دقیقاً برابر با **Cosine Similarity** است:

$$S_{\text{FAISS}}(\mathbf{u}, \mathbf{v}) = \cos(\theta) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \sum_{i=1}^{D} u_i v_i$$

#### 💡 چرا از معماری دوحالته (Dual-Mode FAISS) استفاده کردیم؟
ما در این پروژه یک قابلیت هوشمند در نوار کناری برنامه تعبیه کرده‌ایم:
1. **حالت پیش‌فرض و فوق‌سریع (Fast Character N-Gram FAISS):** بدون نیاز به دانلود هیچ مدل حجیمی، کلمات را به زیرواژه‌های ۲ تا ۵ کاراکتری (`char_wb`) با مقیاس لگاریتمی (`sublinear_tf`) تجزیه کرده و در FAISS جستجو می‌کند. این روش در **کمتر از ۰.۰۱ ثانیه** اجرا شده و تمام ریشه‌ها، پسوندها و پیشوندهای مشترک فارسی را تشخیص می‌دهد.
2. **حالت شبکه عصبی عمیق (Optional Lightweight Neural Model - `MiniLM-L12-v2`):** در صورتی که کاربر گزینه مربوطه را در سایدبار فعال کند، مدل زبانی چندزبانه `paraphrase-multilingual-MiniLM-L12-v2` بارگذاری شده و جملات را به بردارهای ۳۸۴ بعدی معنایی تبدیل می‌کند. این مدل حتی اگر دو خبر هیچ کلمه مشترکی نداشته باشند اما مفهوم یکسانی را برسانند، تشابه کسینوسی بالایی را کشف می‌کند.

---

### ۳. تشابه مجموعه‌ای ژاکارد (Jaccard Set Similarity)
به عنوان سومین معیار کلاسیک داده‌کاوی، هر خبر به مجموعه‌ای از توکن‌های یکتا ($A$ و $B$) تبدیل شده و نسبت اندازه اشتراک دو مجموعه به اجتماع آن‌ها محاسبه می‌شود:

$$J(A, B) = \frac{|A \cap B|}{|A \cup B|} = \frac{|A \cap B|}{|A| + |B| - |A \cap B|} \in [0, 1]$$

---

## 🌟 قابلیت‌های کلیدی رابط کاربری (Key UI Features)

* **پشتیبانی کامل از راست‌به‌چپ (RTL) و فونت وزیرمتن (`Vazirmatn`):** طراحی بصری استاندارد با آیکون‌های برداری رسمی گوگل (`Material Symbols Rounded`).
* **سازگاری کامل با هر دو تم روز (Light Mode) و شب (Dark Mode):** استفاده از متغیرهای تطبیقی CSS بدون به‌هم‌ریختگی رنگ‌ها.
* **کشف خودکار مشابه‌ترین خبر (Auto Best-Match Discovery):** کاربر می‌تواند یک خبر از ایتا انتخاب کند تا موتور FAISS در کسری از ثانیه بین تمام خبرهای استخراج‌شده از سروش‌پلاس بگردد، مشابه‌ترین خبر را پیدا کند و جدول رتبه‌بندی کامل (Ranking List) را نمایش دهد.
* **نمایش کلیدواژه‌های مشترک:** استخراج و نمایش تگ‌های واژگانی مشترک بین دو خبر.
* **کالبدشکافی مرحله‌به‌مرحله NLP:** نمایش خروجی هر ۴ مرحله پیش‌پردازش متن برای هر دو خبر در تب مجزا.
* **حالت داده نمونه آفلاین (Offline Demo Mode):** امکان تست و ارائه کامل پروژه حتی در صورت قطع بودن اینترنت.

---

## 📂 ساختار درختی پروژه (Project Structure)

```text
persian-news-similarity-engine/
├── Video/demo.mp4              # ویدیوی دموی محیط برنامه
├── app.py                      # نقطه ورود اصلی اپلیکیشن Streamlit
├── config.py                   # تنظیمات سراسری و اعتبارسنجی با Pydantic v2
├── requirements.txt            # لیست وابستگی‌ها و کتابخانه‌های پایتون
├── .env.example                # الگوی متغیرهای محیطی
├── LICENSE                     # مجوز انتشار MIT
├── README.md                   # مستندات جامع پروژه
│
├── src/
│   ├── scrapers/               # لایه واکشی ناهمگام اخبار
│   │   ├── base.py             # کلاس پایه HTTP ناهمگام و مدیریت خطاها
│   │   ├── eitaa.py            # اسکریپر وب ایتا (eitaa.com)
│   │   └── soroush.py          # کلاینت API امضاشده (MD5) و پارسر سروش‌پلاس (splus.ir)
│   │
│   ├── nlp/                    # لایه پردازش زبان طبیعی فارسی
│   │   ├── __init__.py         # کلاس ارکستریتور PersianNLPPipeline
│   │   ├── normalizer.py       # یکسان‌ساز حروف، اعراب‌زدا و اصلاح نیم‌فاصله
│   │   ├── cleaner.py          # حذف لینک، منشن، ایموجی، اعداد و علائم نگارشی
│   │   └── stopwords.py        # فیلتر ۱۲۰+ کلمه توقف فارسی
│   │
│   ├── similarity/             # لایه الگوریتم‌های داده‌کاوی و تشابه‌سنجی
│   │   ├── faiss_engine.py     # موتور جستجوی برداری FAISS (دوحالته: N-Gram و MiniLM)
│   │   └── lexical_engine.py   # موتور TF-IDF Cosine Similarity و Jaccard Similarity
│   │
│   └── ui/                     # لایه نمایش و رابط کاربری
│       ├── styles.py           # استایل‌های تطبیقی CSS، فونت وزیرمتن و تنظیمات RTL
│       └── components.py       # کامپوننت‌های کارت‌های امتیاز، مقایسه و رتبه‌بندی
│
└── tests/                      # مجموعه تست‌های واحد (۲۱ تست خودکار Pytest)
    ├── test_nlp.py             # تست‌های نرمال‌ساز، پاک‌ساز و کلمات توقف
    ├── test_scrapers.py        # تست‌های استخراج پیام از ایتا و سروش‌پلاس
    ├── test_similarity.py      # تست‌های ریاضی Cosine Similarity، FAISS و Jaccard
    └── test_ui.py              # تست‌های دسته‌بندی امتیازات و استایل‌ها
```

---

## 🚀 راهنمای نصب و اجرا (Quickstart Guide)

### ۱. ساخت و فعال‌سازی محیط مجازی (Virtual Environment)
```powershell
python -m venv .venv
# در ویندوز (PowerShell):
.\.venv\Scripts\Activate.ps1
# در لینوکس یا مک:
# source .venv/bin/activate
```

### ۲. نصب کتابخانه‌های مورد نیاز
```powershell
pip install -r requirements.txt
```

### ۳. اجرای تست‌های خودکار (Unit Tests)
برای اطمینان از صحت عملکرد تمام ماژول‌ها (NLP، اسکریپرها و فرمول‌های ریاضی Cosine و Jaccard):
```powershell
pytest tests/ -v
```
خروجی:
```text
tests/test_nlp.py .......        PASSED
tests/test_scrapers.py .....     PASSED
tests/test_similarity.py ....... PASSED
tests/test_ui.py ..              PASSED
======================== 21 passed ========================
```

### ۴. اجرای برنامه تحت وب (Streamlit Web App)
```powershell
streamlit run app.py
```
سپس مرورگر شما به‌طور خودکار در آدرس **`http://localhost:8501`** باز خواهد شد.

---

## 📜 مجوز انتشار (License)

این پروژه تحت مجوز **MIT License** منتشر شده است. برای مشاهده جزئیات بیشتر به فایل [LICENSE](./LICENSE) مراجعه فرمایید.
