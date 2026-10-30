"""Persian News Similarity Engine (Eitaa & Soroush Plus) - Streamlit Application."""

import asyncio
import sys
from typing import List, Tuple
import streamlit as st
from streamlit import runtime

if not runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", sys.argv[0]] + sys.argv[1:]
    sys.exit(stcli.main())

import config
from src.nlp import PersianNLPPipeline
from src.scrapers import EitaaScraper, SoroushScraper
from src.similarity import FaissSimilarityEngine, LexicalSimilarityEngine
from src.ui import (
    format_post_option_label,
    get_custom_css,
    render_header,
    render_nlp_pipeline_stages,
    render_ranking_list,
    render_scraped_posts_columns,
    render_shared_keywords,
    render_side_by_side_comparison,
    render_similarity_cards,
)

st.set_page_config(
    page_title="تشابه‌سنجی اخبار فارسی | ایتا و سروش‌پلاس",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)


@st.cache_resource
def get_fast_faiss_engine() -> FaissSimilarityEngine:
    return FaissSimilarityEngine(use_neural=False)


@st.cache_resource(show_spinner="در حال بارگذاری مدل زبانی سبک چندزبانه (MiniLM)...")
def get_neural_faiss_engine() -> FaissSimilarityEngine:
    return FaissSimilarityEngine(model_name=config.EMBEDDING_MODEL_NAME, use_neural=True)


@st.cache_resource
def get_lexical_engine() -> LexicalSimilarityEngine:
    return LexicalSimilarityEngine()


@st.cache_resource
def get_nlp_pipeline() -> PersianNLPPipeline:
    return PersianNLPPipeline()


async def scrape_channels(
    eitaa_channel: str,
    soroush_channel: str,
    limit: int = 10,
) -> Tuple[List[str], List[str]]:
    """Fetch latest posts concurrently from public web pages of Eitaa and Soroush Plus."""
    eitaa_scraper = EitaaScraper()
    soroush_scraper = SoroushScraper()

    eitaa_task = eitaa_scraper.fetch_posts(eitaa_channel, limit=limit)
    soroush_task = soroush_scraper.fetch_posts(soroush_channel, limit=limit)

    eitaa_results, soroush_results = await asyncio.gather(
        eitaa_task, soroush_task, return_exceptions=True
    )

    eitaa_posts: List[str] = []
    soroush_posts: List[str] = []

    if isinstance(eitaa_results, Exception):
        st.warning(f"هشدار در واکشی ایتا (@{eitaa_channel}): {eitaa_results}")
    else:
        eitaa_posts = eitaa_results

    if isinstance(soroush_results, Exception):
        st.warning(f"هشدار در واکشی سروش‌پلاس (@{soroush_channel}): {soroush_results}")
    else:
        soroush_posts = soroush_results

    return eitaa_posts, soroush_posts


SAMPLE_EITAA_POSTS = [
    (
        "بانک مرکزی در بخشنامه‌ای ضوابط جدید انتشار و فروش اوراق گواهی سپرده خاص "
        "با نرخ سود علی‌الحساب ۳۰ درصد را به شبکه بانکی ابلاغ کرد. هدف از این اقدام "
        "مهار انتظارات تورمی و هدایت منابع به بخش تولید است."
    ),
    (
        "سازمان هواشناسی کشور از ورود سامانه بارشی جدید به غرب و شمال غرب کشور "
        "خبر داد و نسبت به لغزندگی جاده‌ها و آب‌گرفتگی معابر در ۱۰ استان هشدار سطح نارنجی صادر کرد."
    ),
    (
        "تیم ملی فوتبال ایران در مرحله نیمه‌نهایی جام ملت‌های آسیا با ارائه یک بازی هجومی "
        "موفق شد به فینال رقابت‌ها راه پیدا کند و تحسین هواداران را برانگیزد."
    ),
]

SAMPLE_SOROUSH_POSTS = [
    (
        "بر اساس بخشنامه جدید بانک مرکزی، اوراق گواهی سپرده مدت‌دار با سود علی‌الحساب ۳۰ درصد "
        "با هدف مهار تورم و تأمین مالی پروژه‌های پیشران و تولیدی از امروز در تمامی شعب عرضه می‌شود."
    ),
    (
        "هشدار نارنجی سازمان هواشناسی: نفوذ سامانه بارشی پرقدرت به مناطق شمال غربی و غربی کشور؛ "
        "مسافران از سفرهای غیرضروری و تردد در حاشیه رودخانه‌ها اکیداً خودداری نمایند."
    ),
    (
        "شاخص کل بورس اوراق بهادار تهران در پایان معاملات امروز با رشد ۱۰ هزار واحدی "
        "به تراز ۲ میلیون و ۱۵۰ هزار واحد رسید و نمادهای فلزی بیشترین تقاضا را ثبت کردند."
    ),
]


def main() -> None:
    if "eitaa_posts" not in st.session_state:
        st.session_state["eitaa_posts"] = []
    if "soroush_posts" not in st.session_state:
        st.session_state["soroush_posts"] = []
    if "eitaa_channel_name" not in st.session_state:
        st.session_state["eitaa_channel_name"] = config.DEFAULT_EITAA_CHANNEL
    if "soroush_channel_name" not in st.session_state:
        st.session_state["soroush_channel_name"] = config.DEFAULT_SOROUSH_CHANNEL
    if "selected_eitaa_idx" not in st.session_state:
        st.session_state["selected_eitaa_idx"] = 0
    if "selected_soroush_idx" not in st.session_state:
        st.session_state["selected_soroush_idx"] = 0

    CHANNEL_PRESETS = [
        ("farsna", "خبرگزاری فارس (farsna)"),
        ("tasnimnews", "خبرگزاری تسنیم (tasnimnews)"),
        ("iribnews", "خبرگزاری صدا و سیما (iribnews)"),
        ("akharinkhabar", "آخرین خبر (akharinkhabar)"),
        ("mehrnews", "خبرگزاری مهر (mehrnews)"),
        ("isna", "خبرگزاری ایسنا (isna)"),
        ("irnanews", "خبرگزاری ایرنا (irnanews)"),
        ("custom", "کانال دیگر (ورود دستی شناسه)"),
    ]
    preset_keys = [k for k, _ in CHANNEL_PRESETS]

    with st.sidebar:
        st.markdown(
            '<h3 style="display:flex; align-items:center; gap:8px;"><span class="ms-icon">tune</span> تنظیمات کانال‌های ایتا و سروش‌پلاس</h3>',
            unsafe_allow_html=True,
        )

        st.markdown("**کانال ایتا (eitaa.com):**")
        curr_eitaa = st.session_state.get("eitaa_channel_name", config.DEFAULT_EITAA_CHANNEL)
        default_eitaa_idx = preset_keys.index(curr_eitaa) if curr_eitaa in preset_keys else len(preset_keys) - 1

        selected_eitaa_preset = st.selectbox(
            "انتخاب کانال ایتا",
            options=preset_keys,
            index=default_eitaa_idx,
            format_func=lambda k: next(label for key, label in CHANNEL_PRESETS if key == k),
            key="eitaa_select_widget",
        )

        if selected_eitaa_preset == "custom":
            eitaa_final_channel = st.text_input(
                "شناسه کانال ایتا",
                value=curr_eitaa if curr_eitaa not in preset_keys else "",
                placeholder="مثال: farsna",
            ).strip().lstrip("@")
        else:
            eitaa_final_channel = selected_eitaa_preset

        st.markdown("**کانال سروش‌پلاس (splus.ir):**")
        curr_soroush = st.session_state.get("soroush_channel_name", config.DEFAULT_SOROUSH_CHANNEL)
        default_soroush_idx = preset_keys.index(curr_soroush) if curr_soroush in preset_keys else len(preset_keys) - 1

        selected_soroush_preset = st.selectbox(
            "انتخاب کانال سروش‌پلاس",
            options=preset_keys,
            index=default_soroush_idx,
            format_func=lambda k: next(label for key, label in CHANNEL_PRESETS if key == k),
            key="soroush_select_widget",
        )

        if selected_soroush_preset == "custom":
            soroush_final_channel = st.text_input(
                "شناسه کانال سروش‌پلاس",
                value=curr_soroush if curr_soroush not in preset_keys else "",
                placeholder="مثال: tasnimnews",
            ).strip().lstrip("@")
        else:
            soroush_final_channel = selected_soroush_preset

        posts_limit = st.slider(
            "تعداد خبرهای دریافتی از هر کانال:",
            min_value=3,
            max_value=25,
            value=8,
            step=1,
        )

        st.markdown("---")
        st.markdown(
            '<div style="font-weight:700; display:flex; align-items:center; gap:6px; margin-bottom:6px;"><span class="ms-icon">memory</span> تنظیمات موتور هوش مصنوعی (FAISS):</div>',
            unsafe_allow_html=True,
        )
        use_neural_model = st.checkbox(
            "استفاده از مدل زبانی شبکه عصبی (MiniLM)",
            value=False,
            help="در حالت پیش‌فرض از موتور فوق‌سریع FAISS Char-Ngram استفاده می‌شود. با فعال‌سازی این گزینه، مدل سبک چندزبانه بارگذاری می‌گردد.",
        )

        st.markdown("---")
        fetch_col, sample_col = st.columns(2)
        with fetch_col:
            fetch_button = st.button("واکشی آنلاین", use_container_width=True, type="primary")
        with sample_col:
            load_sample_button = st.button("داده نمونه", use_container_width=True)

        st.markdown("---")
        st.markdown(
            '<div style="font-size: 0.82rem; line-height: 1.7; background: rgba(128,128,128,0.08); padding: 12px; border-radius: 10px;">'
            '<div style="display:flex; align-items:center; gap:6px; font-weight:700; margin-bottom:4px;"><span class="ms-icon">info</span> مراحل کار سیستم:</div>'
            '۱. دریافت هم‌زمان آخرین اخبار از <code>eitaa.com</code> و <code>splus.ir</code><br/>'
            '۲. نرمال‌سازی، حذف نویز و حذف کلمات توقف فارسی<br/>'
            '۳. محاسبه <b>Cosine Similarity</b> (با FAISS و TF-IDF) و <b>Jaccard Similarity</b>'
            '</div>',
            unsafe_allow_html=True,
        )

    engine_mode_label = "مدل زبانی MiniLM + FAISS" if use_neural_model else "سریع (FAISS N-Gram)"
    render_header(
        eitaa_channel=st.session_state.get("eitaa_channel_name", ""),
        soroush_channel=st.session_state.get("soroush_channel_name", ""),
        engine_mode=engine_mode_label,
    )

    faiss_engine = get_neural_faiss_engine() if use_neural_model else get_fast_faiss_engine()
    lexical_engine = get_lexical_engine()
    nlp_pipeline = get_nlp_pipeline()

    if fetch_button:
        clean_eitaa = eitaa_final_channel.strip().lstrip("@")
        clean_soroush = soroush_final_channel.strip().lstrip("@")

        if not clean_eitaa or not clean_soroush:
            st.error("لطفاً شناسه هر دو کانال ایتا و سروش‌پلاس را مشخص کنید.")
        else:
            with st.spinner(f"در حال دریافت آخرین اخبار از ایتا (@{clean_eitaa}) و سروش‌پلاس (@{clean_soroush})..."):
                e_posts, s_posts = asyncio.run(
                    scrape_channels(clean_eitaa, clean_soroush, limit=posts_limit)
                )
                if not e_posts and not s_posts:
                    st.error("پیامی دریافت نشد. لطفاً اتصال اینترنت یا شناسه کانال را بررسی کنید یا از دکمه «داده نمونه» استفاده نمایید.")
                elif not s_posts:
                    st.warning(
                        f"از ایتا {len(e_posts)} خبر دریافت شد اما کانال @{clean_soroush} در سروش‌پلاس پیامی نداشت."
                    )
                    st.session_state["eitaa_posts"] = e_posts
                    st.session_state["eitaa_channel_name"] = clean_eitaa
                elif not e_posts:
                    st.warning(
                        f"از سروش‌پلاس {len(s_posts)} خبر دریافت شد اما کانال @{clean_eitaa} در ایتا پیامی نداشت."
                    )
                    st.session_state["soroush_posts"] = s_posts
                    st.session_state["soroush_channel_name"] = clean_soroush
                else:
                    st.session_state["eitaa_posts"] = e_posts
                    st.session_state["soroush_posts"] = s_posts
                    st.session_state["eitaa_channel_name"] = clean_eitaa
                    st.session_state["soroush_channel_name"] = clean_soroush
                    st.success(
                        f"دریافت موفق: {len(e_posts)} خبر جدید از ایتا و {len(s_posts)} خبر جدید از سروش‌پلاس (به ترتیب از آخرین خبر) استخراج شد."
                    )

    if load_sample_button:
        st.session_state["eitaa_posts"] = SAMPLE_EITAA_POSTS.copy()
        st.session_state["soroush_posts"] = SAMPLE_SOROUSH_POSTS.copy()
        st.session_state["eitaa_channel_name"] = "farsna"
        st.session_state["soroush_channel_name"] = "tasnimnews"
        st.info("داده‌های خبری نمونه برای ایتا و سروش‌پلاس بارگذاری شدند.")

    eitaa_posts: List[str] = st.session_state["eitaa_posts"]
    soroush_posts: List[str] = st.session_state["soroush_posts"]

    if not eitaa_posts or not soroush_posts:
        st.info(
            "برای شروع، از منوی سمت راست کانال‌های ایتا و سروش‌پلاس را انتخاب کرده و روی "
            "«واکشی آنلاین» یا «داده نمونه» کلیک کنید."
        )
        return

    tab_similarity, tab_feed, tab_pipeline = st.tabs([
        "سنجش تشابه کسینوسی و ژاکارد (Cosine & Jaccard)",
        f"فید اخبار دریافتی ({len(eitaa_posts)} ایتا | {len(soroush_posts)} سروش‌پلاس)",
        "مراحل پیش‌پردازش متن فارسی (NLP Pipeline)",
    ])

    with tab_similarity:
        st.markdown(
            '<h3 style="display:flex; align-items:center; gap:8px;"><span class="ms-icon" style="color:#0284c7;">compare_arrows</span> انتخاب خبر از ایتا و سروش‌پلاس جهت محاسبه تشابه</h3>',
            unsafe_allow_html=True,
        )

        col_select_eitaa, col_mode = st.columns([1, 1])

        with col_select_eitaa:
            st.markdown(f"**خبر مرجع از ایتا (@{st.session_state['eitaa_channel_name']}):**")
            eitaa_options = [format_post_option_label(i, post) for i, post in enumerate(eitaa_posts)]
            selected_eitaa_idx = st.selectbox(
                "انتخاب خبر ایتا",
                range(len(eitaa_posts)),
                index=0,
                format_func=lambda i: eitaa_options[i],
                label_visibility="collapsed",
            )
            st.session_state["selected_eitaa_idx"] = selected_eitaa_idx

        selected_eitaa_raw = eitaa_posts[selected_eitaa_idx]
        eitaa_cleaned = nlp_pipeline.transform(selected_eitaa_raw)

        with col_mode:
            st.markdown(f"**نحوه انتخاب خبر از سروش‌پلاس (@{st.session_state['soroush_channel_name']}):**")
            match_strategy = st.radio(
                "راهبرد تطبیق با سروش‌پلاس",
                [
                    "یافتن خودکار مشابه‌ترین خبر در سروش‌پلاس (با FAISS Cosine Search)",
                    "مقایسه با آخرین خبر کانال سروش‌پلاس (خبر شماره ۱)",
                    "انتخاب دستی خبر از سروش‌پلاس",
                ],
                label_visibility="collapsed",
            )

            selected_soroush_idx: int = 0
            rankings: List[Tuple[int, float]] = []

            if match_strategy.startswith("یافتن خودکار"):
                soroush_cleaned_list = [nlp_pipeline.transform(p) for p in soroush_posts]
                index, _ = faiss_engine.build_index(soroush_cleaned_list)
                rankings = faiss_engine.search_top_k(
                    index=index,
                    query=eitaa_cleaned,
                    top_k=len(soroush_posts),
                )
                if rankings:
                    selected_soroush_idx = rankings[0][0]
                st.caption(f"مشابه‌ترین خبر در سروش‌پلاس: **خبر شماره {selected_soroush_idx + 1}**")
            elif match_strategy.startswith("مقایسه با آخرین"):
                selected_soroush_idx = 0
            else:
                soroush_options = [format_post_option_label(i, post) for i, post in enumerate(soroush_posts)]
                selected_soroush_idx = st.selectbox(
                    "انتخاب دستی خبر سروش‌پلاس",
                    range(len(soroush_posts)),
                    index=0,
                    format_func=lambda i: soroush_options[i],
                    label_visibility="collapsed",
                )

            st.session_state["selected_soroush_idx"] = selected_soroush_idx

        selected_soroush_raw = soroush_posts[selected_soroush_idx]
        soroush_cleaned = nlp_pipeline.transform(selected_soroush_raw)

        semantic_cos = faiss_engine.compute_similarity(eitaa_cleaned, soroush_cleaned)
        lexical_cos = lexical_engine.compute_similarity(eitaa_cleaned, soroush_cleaned)
        jaccard_sim = lexical_engine.compute_jaccard_similarity(eitaa_cleaned, soroush_cleaned)

        render_similarity_cards(
            semantic_score=semantic_cos,
            lexical_score=lexical_cos,
            jaccard_score=jaccard_sim,
        )

        render_side_by_side_comparison(
            eitaa_text=selected_eitaa_raw,
            soroush_text=selected_soroush_raw,
            eitaa_channel=st.session_state["eitaa_channel_name"],
            soroush_channel=st.session_state["soroush_channel_name"],
        )

        shared_tokens = nlp_pipeline.extract_shared_tokens(eitaa_cleaned, soroush_cleaned)
        render_shared_keywords(shared_tokens)

        if rankings and len(rankings) > 1:
            st.markdown("---")
            render_ranking_list(
                soroush_posts=soroush_posts,
                rankings=rankings,
                soroush_channel=st.session_state["soroush_channel_name"],
            )

    with tab_feed:
        render_scraped_posts_columns(
            eitaa_posts=eitaa_posts,
            soroush_posts=soroush_posts,
            eitaa_channel=st.session_state["eitaa_channel_name"],
            soroush_channel=st.session_state["soroush_channel_name"],
        )

    with tab_pipeline:
        cur_e = st.session_state.get("selected_eitaa_idx", 0)
        cur_s = st.session_state.get("selected_soroush_idx", 0)
        eitaa_stages = nlp_pipeline.transform_detailed(eitaa_posts[cur_e])
        soroush_stages = nlp_pipeline.transform_detailed(soroush_posts[cur_s])
        render_nlp_pipeline_stages(eitaa_stages, soroush_stages)


if __name__ == "__main__":
    main()
