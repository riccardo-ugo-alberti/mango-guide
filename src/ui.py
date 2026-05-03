from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st


def configure_page(title: str = "Mango Guide") -> None:
    st.set_page_config(page_title=title, page_icon="🥭", layout="wide")
    inject_style()


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --mango: #f4b000;
            --mango-deep: #c76a00;
            --leaf: #2f9e44;
            --leaf-soft: #dff5df;
            --sunset: #ff7a1a;
            --ink: #2b2118;
            --muted: #74665b;
            --cream: #fff8e8;
            --paper: rgba(255, 255, 255, 0.9);
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(244, 176, 0, 0.18), transparent 30rem),
                radial-gradient(circle at 90% 12%, rgba(47, 158, 68, 0.10), transparent 22rem),
                linear-gradient(180deg, #fffaf0 0%, #ffffff 48%, #f7fff4 100%);
            color: var(--ink);
        }
        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 4rem;
        }
        h1, h2, h3 {
            color: var(--ink);
            letter-spacing: 0;
        }
        section[data-testid="stSidebar"] {
            background: #fff8e8;
            border-right: 1px solid rgba(199, 106, 0, 0.14);
        }
        .mango-hero {
            border: 1px solid rgba(199, 106, 0, 0.18);
            border-radius: 8px;
            padding: clamp(1.2rem, 3vw, 2rem);
            background:
                linear-gradient(135deg, rgba(255, 248, 232, 0.96), rgba(244, 176, 0, 0.14)),
                linear-gradient(90deg, rgba(255,255,255,0.7), rgba(255,255,255,0.35));
            box-shadow: 0 16px 44px rgba(74, 52, 20, 0.08);
            margin-bottom: 1.4rem;
        }
        .mango-hero h1 {
            font-size: clamp(2.1rem, 6vw, 4rem);
            line-height: 1;
            margin: 0 0 0.45rem 0;
        }
        .mango-hero p {
            color: var(--muted);
            font-size: 1.08rem;
            max-width: 48rem;
            margin: 0;
        }
        .mango-kicker {
            color: #7a3e00;
            font-weight: 800;
            text-transform: uppercase;
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            margin-bottom: 0.4rem;
        }
        .metric-card, .mango-card, .empty-state, .gallery-card, .score-panel, .section-panel {
            background: var(--paper);
            border: 1px solid rgba(248, 180, 0, 0.28);
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(74, 52, 20, 0.06);
        }
        .metric-card {
            padding: 1rem;
            min-height: 112px;
        }
        .metric-card .label {
            color: var(--muted);
            font-size: 0.86rem;
            margin-bottom: 0.35rem;
        }
        .metric-card .value {
            color: var(--ink);
            font-size: clamp(1.45rem, 3vw, 2rem);
            font-weight: 900;
            line-height: 1.1;
        }
        .metric-card .hint {
            color: #7a3e00;
            font-size: 0.82rem;
            margin-top: 0.45rem;
        }
        .mango-card {
            padding: 1rem;
            min-height: 190px;
            display: flex;
            flex-direction: column;
            gap: 0.55rem;
        }
        .mango-card img {
            width: 100%;
            aspect-ratio: 4 / 3;
            object-fit: cover;
            border-radius: 6px;
            margin-bottom: 0.2rem;
        }
        .mango-card .title {
            color: #7a3e00;
            font-weight: 900;
            font-size: 1.08rem;
            line-height: 1.25;
        }
        .mango-card .meta, .muted {
            color: var(--muted);
            font-size: 0.9rem;
        }
        .mango-card .note {
            color: #3d3128;
            margin: 0;
            line-height: 1.45;
        }
        .score-badge {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            max-width: 100%;
            gap: 0.35rem;
            padding: 0.28rem 0.58rem;
            border-radius: 999px;
            font-weight: 850;
            font-size: 0.83rem;
            border: 1px solid transparent;
            white-space: normal;
        }
        .score-legendary {
            color: #5c3400;
            background: #ffe8a3;
            border-color: #f4b000;
        }
        .score-excellent {
            color: #1f5f2f;
            background: #dff5df;
            border-color: #79c56b;
        }
        .score-solid {
            color: #28505f;
            background: #d9f2f2;
            border-color: #78c8c8;
        }
        .score-acceptable {
            color: #6b4b00;
            background: #fff1c7;
            border-color: #e4bd4a;
        }
        .score-disappointment {
            color: #7a1e1e;
            background: #ffe3df;
            border-color: #f0a19a;
        }
        .score-missing {
            color: #61564e;
            background: #f2eee8;
            border-color: #ddd2c5;
        }
        .empty-state {
            padding: 1.25rem;
            text-align: center;
            color: var(--muted);
        }
        .empty-state .icon {
            font-size: 2rem;
            margin-bottom: 0.35rem;
        }
        .empty-state strong {
            color: var(--ink);
            display: block;
            margin-bottom: 0.25rem;
        }
        .gallery-card {
            overflow: hidden;
            margin-bottom: 1rem;
        }
        .gallery-card img {
            width: 100%;
            aspect-ratio: 4 / 3;
            object-fit: cover;
            display: block;
        }
        .gallery-card .body {
            padding: 0.85rem;
        }
        .score-panel {
            padding: 1rem;
            border-color: rgba(47, 158, 68, 0.26);
            background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(223,245,223,0.62));
        }
        .score-panel .score-number {
            font-size: 2.2rem;
            font-weight: 900;
            line-height: 1;
            color: #1f5f2f;
        }
        .section-panel {
            padding: 1rem;
            margin-bottom: 1rem;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(47, 158, 68, 0.16);
            border-radius: 8px;
        }
        @media (max-width: 720px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .mango-card, .metric-card {
                min-height: auto;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_data_notice(error: str | None, df: pd.DataFrame) -> bool:
    if error:
        st.warning(error)
        return True
    if df.empty:
        empty_state("No mango reviews yet", "Add the first tasting note to start the guide.", "🥭")
        return True
    return False


def page_title(title: str, caption: str | None = None) -> None:
    st.title(title)
    if caption:
        st.caption(caption)


def hero(title: str, subtitle: str, kicker: str = "Public tasting guide") -> None:
    st.markdown(
        f"""
        <div class="mango-hero">
            <div class="mango-kicker">{escape(kicker)}</div>
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def score_label(score: object) -> tuple[str, str]:
    if pd.isna(score):
        return "No score yet", "score-missing"

    value = float(score)
    if value >= 9.0:
        return "Legendary Mango", "score-legendary"
    if value >= 8.0:
        return "Excellent", "score-excellent"
    if value >= 7.0:
        return "Solid", "score-solid"
    if value >= 6.0:
        return "Acceptable", "score-acceptable"
    return "Mango Disappointment", "score-disappointment"


def score_badge(score: object, compact: bool = False) -> str:
    label, class_name = score_label(score)
    score_text = "N/A" if pd.isna(score) else f"{float(score):.1f}"
    text = score_text if compact else f"Mango Score {score_text} - {label}"
    return f'<span class="score-badge {class_name}">🥭 {escape(text)}</span>'


def metric_card(label: str, value: object, hint: str | None = None) -> None:
    hint_html = f'<div class="hint">{escape(str(hint))}</div>' if hint else ""
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{escape(label)}</div>
            <div class="value">{escape(str(value))}</div>
            {hint_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(title: str, body: str, icon: str = "🥭") -> None:
    st.markdown(
        f"""
        <div class="empty-state">
            <div class="icon">{escape(icon)}</div>
            <strong>{escape(title)}</strong>
            <span>{escape(body)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mango_card(row: pd.Series, rank: int | None = None, show_image: bool = False) -> None:
    title = row.get("name") or "Untitled mango moment"
    score = row.get("final_score")
    place_bits = [row.get("place_name"), row.get("city"), row.get("country")]
    place = ", ".join(str(bit) for bit in place_bits if pd.notna(bit) and bit)
    rank_label = f"#{rank} " if rank is not None else ""
    image_url = row.get("image_url")
    image_html = ""
    if show_image and pd.notna(image_url) and str(image_url).strip():
        image_html = f'<img src="{escape(str(image_url), quote=True)}" alt="{escape(str(title), quote=True)}">'

    st.markdown(
        f"""
        <div class="mango-card">
            {image_html}
            <div class="title">{escape(rank_label + str(title))}</div>
            <div class="meta">{escape(str(row.get("category") or "Mango"))} · {escape(place or "Somewhere sunny")}</div>
            {score_badge(score)}
            <p class="note">{escape(str(row.get("short_review") or "No tasting note yet."))}</p>
            <div class="meta">{escape(str(row.get("reviewer") or "Unknown reviewer"))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def review_card(row: pd.Series, rank: int | None = None) -> None:
    mango_card(row, rank=rank)


def gallery_card(row: pd.Series) -> None:
    title = row.get("name") or "Untitled mango moment"
    image_url = str(row.get("image_url") or "")
    location = " ".join(str(bit) for bit in [row.get("city"), row.get("country")] if pd.notna(bit) and bit)
    st.markdown(
        f"""
        <div class="gallery-card">
            <img src="{escape(image_url, quote=True)}" alt="{escape(str(title), quote=True)}">
            <div class="body">
                <strong>{escape(str(title))}</strong>
                <div style="margin: 0.45rem 0;">{score_badge(row.get("final_score"), compact=True)}</div>
                <div class="muted">{escape(location or "Mango location pending")}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def score_panel(score: float | None) -> None:
    score_text = "N/A" if score is None else f"{score:.2f}"
    st.markdown(
        f"""
        <div class="score-panel">
            <div class="muted">Live calculated final score</div>
            <div class="score-number">{escape(score_text)}</div>
            <div>{score_badge(score)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def filtered_reviews(df: pd.DataFrame) -> pd.DataFrame:
    filtered = df.copy()
    cols = st.columns(3)

    with cols[0]:
        categories = sorted(value for value in filtered["category"].dropna().unique())
        category = st.selectbox("Category", ["All"] + categories)
    with cols[1]:
        countries = sorted(value for value in filtered["country"].dropna().unique())
        country = st.selectbox("Country", ["All"] + countries)
    with cols[2]:
        reviewers = sorted(value for value in filtered["reviewer"].dropna().unique())
        reviewer = st.selectbox("Reviewer", ["All"] + reviewers)

    if category != "All":
        filtered = filtered[filtered["category"] == category]
    if country != "All":
        filtered = filtered[filtered["country"] == country]
    if reviewer != "All":
        filtered = filtered[filtered["reviewer"] == reviewer]

    return filtered
