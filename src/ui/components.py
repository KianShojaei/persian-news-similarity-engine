"""Streamlit UI rendering components with adaptive theme colors and Material Symbols icons."""

from typing import List, Tuple
import html
import re
import streamlit as st
import config


def format_post_option_label(index: int, post: str, max_chars: int = 44) -> str:
    """Create a clean, concise, RTL-safe dropdown label for a news post."""
    # Remove decorative geometric bullets and emojis from dropdown preview so it doesn't break RTL
    cleaned = re.sub(r"[^\u0600-\u06FFa-zA-Z0-9\s\.\،\:\-]", " ", post)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > max_chars:
        truncated = cleaned[:max_chars].rsplit(" ", 1)[0]
        cleaned = f"{truncated}..."
    return f"خبر شماره {index + 1} — {cleaned}"


def get_similarity_classification(score: float) -> Tuple[str, str]:
    """Return Persian label and CSS class for a given similarity score (0.0 to 1.0)."""
    if score >= config.SIMILARITY_HIGH_THRESHOLD:
        return "تشابه بالا (High)", "score-badge-high"
    elif score >= config.SIMILARITY_MODERATE_THRESHOLD:
        return "تشابه متوسط (Moderate)", "score-badge-moderate"
    else:
        return "تشابه ضعیف (Low)", "score-badge-low"


def render_header(eitaa_channel: str = "", soroush_channel: str = "", engine_mode: str = "سریع") -> None:
    """Render modern hero header banner for Eitaa & Soroush Plus with Material icons."""
    eitaa_name = config.get_channel_display_name(eitaa_channel) if eitaa_channel else "ایتا"
    soroush_name = config.get_channel_display_name(soroush_channel) if soroush_channel else "سروش‌پلاس"

    header_html = (
        '<div class="app-hero-header">'
        '<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">'
        '<div>'
        '<h1 style="display: flex; align-items: center; gap: 10px;">'
        '<span class="ms-icon" style="font-size: 2rem;">analytics</span>'
        '<span>سامانه هوشمند تشابه‌سنجی اخبار فارسی (ایتا و سروش‌پلاس)</span>'
        '</h1>'
        '<p>استخراج پیام‌ها از Eitaa و Soroush Plus • پیش‌پردازش متن فارسی • محاسبه Cosine Similarity و Jaccard</p>'
        '</div>'
        '<div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">'
        f'<span class="platform-badge platform-eitaa"><span class="ms-icon">rss_feed</span> ایتا: {html.escape(eitaa_name)}</span>'
        f'<span class="platform-badge platform-soroush"><span class="ms-icon">hub</span> سروش‌پلاس: {html.escape(soroush_name)}</span>'
        '<span style="background: rgba(255,255,255,0.18); color: #fff; padding: 5px 12px; border-radius: 9999px; font-size: 0.82rem;">Cosine + Jaccard</span>'
        f'<span style="background: rgba(255,255,255,0.18); color: #fff; padding: 5px 12px; border-radius: 9999px; font-size: 0.82rem;">موتور: {html.escape(engine_mode)}</span>'
        '</div></div></div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


def render_scraped_posts_columns(
    eitaa_posts: List[str],
    soroush_posts: List[str],
    eitaa_channel: str,
    soroush_channel: str,
) -> None:
    """Render scraped posts from Eitaa and Soroush Plus in two side-by-side columns."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<div class="column-header-box column-header-eitaa">'
            f'<span style="display:flex; align-items:center; gap:6px;"><span class="ms-icon">newspaper</span> اخبار دریافت‌شده از پیام‌رسان ایتا</span>'
            f'<span class="platform-badge platform-eitaa">@{html.escape(eitaa_channel)} ({len(eitaa_posts)} خبر)</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        for i, post in enumerate(eitaa_posts, 1):
            escaped_text = html.escape(post)
            st.markdown(
                f'<div class="post-feed-card">'
                f'<div class="post-card-top">'
                f'<span class="post-card-index">خبر شماره {i} (جدیدترین)</span>' if i == 1 else f'<div class="post-feed-card"><div class="post-card-top"><span class="post-card-index">خبر شماره {i}</span>'
                f'<span style="font-size: 0.78rem; color: #ea580c; font-weight: 700;">eitaa.com/{html.escape(eitaa_channel)}</span>'
                f'</div>'
                f'<div class="post-card-text">{escaped_text}</div>'
                f'<div class="post-card-footer">'
                f'<span><span class="ms-icon" style="font-size:1rem;">notes</span> {len(post.split())} کلمه</span>'
                f'<span><span class="ms-icon" style="font-size:1rem;">text_fields</span> {len(post)} کاراکتر</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            f'<div class="column-header-box column-header-soroush">'
            f'<span style="display:flex; align-items:center; gap:6px;"><span class="ms-icon">newspaper</span> اخبار دریافت‌شده از پیام‌رسان سروش‌پلاس</span>'
            f'<span class="platform-badge platform-soroush">@{html.escape(soroush_channel)} ({len(soroush_posts)} خبر)</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
        for i, post in enumerate(soroush_posts, 1):
            escaped_text = html.escape(post)
            st.markdown(
                f'<div class="post-feed-card">'
                f'<div class="post-card-top">'
                f'<span class="post-card-index">خبر شماره {i} (جدیدترین)</span>' if i == 1 else f'<div class="post-feed-card"><div class="post-card-top"><span class="post-card-index">خبر شماره {i}</span>'
                f'<span style="font-size: 0.78rem; color: #0284c7; font-weight: 700;">splus.ir/{html.escape(soroush_channel)}</span>'
                f'</div>'
                f'<div class="post-card-text">{escaped_text}</div>'
                f'<div class="post-card-footer">'
                f'<span><span class="ms-icon" style="font-size:1rem;">notes</span> {len(post.split())} کلمه</span>'
                f'<span><span class="ms-icon" style="font-size:1rem;">text_fields</span> {len(post)} کاراکتر</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )


def render_similarity_cards(
    semantic_score: float,
    lexical_score: float,
    jaccard_score: float = 0.0,
) -> None:
    """Render three visual score cards showing FAISS Cosine, TF-IDF Cosine, and Jaccard Similarity."""
    sem_pct = round(semantic_score * 100, 1)
    lex_pct = round(lexical_score * 100, 1)
    jac_pct = round(jaccard_score * 100, 1)

    sem_label, sem_badge = get_similarity_classification(semantic_score)
    lex_label, lex_badge = get_similarity_classification(lexical_score)
    jac_label, jac_badge = get_similarity_classification(jaccard_score)

    card_html = (
        '<div class="metric-card-wrapper">'
        '<div class="similarity-metric-card metric-semantic">'
        '<div class="metric-score-title"><span class="ms-icon">neurology</span> تشابه کسینوسی برداری (FAISS Cosine)</div>'
        f'<div class="metric-score-value">{sem_pct}%</div>'
        f'<div class="metric-cosine-raw">cos(θ) = {semantic_score:.4f}</div>'
        '<div style="font-size: 0.82rem; color: #cbd5e1;">جستجوی برداری FAISS IndexFlatIP</div>'
        f'<span class="score-badge {sem_badge}">{sem_label}</span>'
        '</div>'
        '<div class="similarity-metric-card metric-lexical">'
        '<div class="metric-score-title"><span class="ms-icon">calculate</span> تشابه کسینوسی واژگانی (TF-IDF Cosine)</div>'
        f'<div class="metric-score-value">{lex_pct}%</div>'
        f'<div class="metric-cosine-raw">cos(θ) = {lexical_score:.4f}</div>'
        '<div style="font-size: 0.82rem; color: #e0f2fe;">ماتریس وزن‌دهی TF-IDF + Cosine Similarity</div>'
        f'<span class="score-badge {lex_badge}">{lex_label}</span>'
        '</div>'
        '<div class="similarity-metric-card metric-hybrid">'
        '<div class="metric-score-title"><span class="ms-icon">join_inner</span> تشابه مجموعه‌ای ژاکارد (Jaccard Similarity)</div>'
        f'<div class="metric-score-value">{jac_pct}%</div>'
        f'<div class="metric-cosine-raw">J(A,B) = {jaccard_score:.4f}</div>'
        '<div style="font-size: 0.82rem; color: #cbd5e1;">نسبت اشتراک به اجتماع کلمات |A∩B| / |A∪B|</div>'
        f'<span class="score-badge {jac_badge}">{jac_label}</span>'
        '</div>'
        '</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)


def render_side_by_side_comparison(
    eitaa_text: str,
    soroush_text: str,
    eitaa_channel: str,
    soroush_channel: str,
) -> None:
    """Render side-by-side comparison of selected raw news posts."""
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f'<div class="comparison-card">'
            f'<div class="comparison-card-header">'
            f'<span style="font-weight: 800; font-size: 1.05rem; color: #ea580c; display:flex; align-items:center; gap:6px;"><span class="ms-icon">article</span> خبر انتخاب‌شده از ایتا</span>'
            f'<span class="platform-badge platform-eitaa">@{html.escape(eitaa_channel)}</span>'
            f'</div>'
            f'<div class="comparison-card-body">{html.escape(eitaa_text)}</div>'
            f'<div style="margin-top: 1rem; font-size: 0.82rem; opacity: 0.75; display: flex; gap: 14px;">'
            f'<span>تعداد کاراکتر: {len(eitaa_text):,}</span>'
            f'<span>تعداد کلمات: {len(eitaa_text.split()):,}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f'<div class="comparison-card">'
            f'<div class="comparison-card-header">'
            f'<span style="font-weight: 800; font-size: 1.05rem; color: #0284c7; display:flex; align-items:center; gap:6px;"><span class="ms-icon">article</span> خبر انتخاب‌شده از سروش‌پلاس</span>'
            f'<span class="platform-badge platform-soroush">@{html.escape(soroush_channel)}</span>'
            f'</div>'
            f'<div class="comparison-card-body">{html.escape(soroush_text)}</div>'
            f'<div style="margin-top: 1rem; font-size: 0.82rem; opacity: 0.75; display: flex; gap: 14px;">'
            f'<span>تعداد کاراکتر: {len(soroush_text):,}</span>'
            f'<span>تعداد کلمات: {len(soroush_text.split()):,}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def render_shared_keywords(shared_tokens: List[str]) -> None:
    """Render shared keywords between the two news articles."""
    st.markdown(
        '<h4 style="display:flex; align-items:center; gap:6px;"><span class="ms-icon" style="color:#0284c7;">link</span> کلیدواژه‌های مشترک استخراج‌شده بین دو خبر:</h4>',
        unsafe_allow_html=True,
    )
    if not shared_tokens:
        st.info("کلمه کلیدی دقیقاً یکسانی (پس از حذف کلمات توقف) بین این دو خبر یافت نشد.")
        return

    chips_html = "".join(f'<span class="keyword-chip">{html.escape(tok)}</span>' for tok in shared_tokens)
    st.markdown(
        f'<div style="background: var(--secondary-background-color); border: 1px solid rgba(128,128,128,0.2); padding: 12px; border-radius: 14px; margin-bottom: 1rem;">{chips_html}</div>',
        unsafe_allow_html=True,
    )


def render_nlp_pipeline_stages(
    stages_eitaa: Tuple[str, str, str, str],
    stages_soroush: Tuple[str, str, str, str],
) -> None:
    """Render detailed step-by-step cleaned NLP pipeline stages with Material icons."""
    stage_names = [
        ("۱. متن اولیه خبر (Raw Text)", "متن خام واکشی‌شده از ایتا و سروش‌پلاس", "download"),
        ("۲. نرمال‌سازی فارسی (Persian Normalizer)", "یکسان‌سازی ی/ک، حذف اعراب و استانداردسازی نیم‌فاصله", "auto_fix_high"),
        ("۳. پاک‌سازی نویز (Text Cleaner)", "حذف لینک‌ها، آیدی‌ها، ایموجی‌ها، اعداد و علائم نگارشی", "cleaning_services"),
        ("۴. حذف کلمات توقف (Stopwords Removal)", "حذف کلمات پرتکرار بی‌ارزش جهت محاسبه دقیق Cosine Similarity", "filter_alt"),
    ]

    for i, (title, desc, icon_name) in enumerate(stage_names):
        text_eitaa = html.escape(stages_eitaa[i]) if stages_eitaa[i] else "(بدون محتوا)"
        text_soroush = html.escape(stages_soroush[i]) if stages_soroush[i] else "(بدون محتوا)"

        st.markdown(
            f'<div class="nlp-stage-card">'
            f'<div class="nlp-stage-title"><span class="ms-icon">{icon_name}</span><span>{html.escape(title)}</span></div>'
            f'<div class="nlp-stage-desc">{html.escape(desc)}</div>'
            f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px;">'
            f'<div><div style="color: #ea580c; font-weight: 700; margin-bottom: 6px;">ایتا</div>'
            f'<div class="nlp-text-box nlp-text-box-eitaa">{text_eitaa}</div></div>'
            f'<div><div style="color: #0284c7; font-weight: 700; margin-bottom: 6px;">سروش‌پلاس</div>'
            f'<div class="nlp-text-box nlp-text-box-soroush">{text_soroush}</div></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )


def render_ranking_list(
    soroush_posts: List[str],
    rankings: List[Tuple[int, float]],
    soroush_channel: str,
) -> None:
    """Render ranked list of candidate Soroush Plus posts sorted by Cosine Similarity."""
    st.markdown(
        '<h3 style="display:flex; align-items:center; gap:8px;"><span class="ms-icon" style="color:#0284c7;">leaderboard</span> رتبه‌بندی تشابه کسینوسی تمام خبرهای سروش‌پلاس با خبر انتخابی ایتا</h3>',
        unsafe_allow_html=True,
    )
    for rank, (idx, score) in enumerate(rankings, start=1):
        post_snippet = soroush_posts[idx]
        preview = post_snippet[:140] + ("..." if len(post_snippet) > 140 else "")
        score_pct = round(score * 100, 1)
        label, badge_class = get_similarity_classification(score)

        st.markdown(
            f'<div class="ranking-row">'
            f'<div style="flex: 1;">'
            f'<div style="font-weight: 800; font-size: 0.96rem; margin-bottom: 4px;">'
            f'رتبه {rank}: خبر شماره {idx + 1} از سروش‌پلاس (@{html.escape(soroush_channel)})'
            f'</div>'
            f'<div style="font-size: 0.88rem; opacity: 0.85; line-height: 1.7;">{html.escape(preview)}</div>'
            f'</div>'
            f'<div style="text-align: left; min-width: 160px;">'
            f'<span style="font-size: 1.35rem; font-weight: 900; color: #0284c7;">{score_pct}%</span>'
            f'<div style="font-size: 0.76rem; opacity: 0.75; direction: ltr;">cos(θ) = {score:.4f}</div>'
            f'<span class="score-badge {badge_class}" style="font-size: 0.74rem; padding: 2px 10px;">{label}</span>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
