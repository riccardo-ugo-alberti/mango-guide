from __future__ import annotations

import base64
from html import escape
import mimetypes
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import streamlit as st


def configure_page(title: str = "Mango Guide") -> None:
    st.set_page_config(page_title=title, page_icon="MG", layout="wide")
    inject_style()


def inject_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ivory: #fbf7ef;
            --sand: #e7dac7;
            --sand-soft: #f4ecdf;
            --mango: #c99535;
            --mango-muted: #b88732;
            --brown: #342820;
            --charcoal: #252322;
            --muted: #756a60;
            --line: rgba(52, 40, 32, 0.14);
            --paper: rgba(255, 252, 246, 0.92);
        }
        .stApp {
            background:
                linear-gradient(180deg, #fbf7ef 0%, #fffdf8 46%, #f7f1e7 100%);
            color: var(--charcoal);
        }
        .block-container {
            max-width: 1120px;
            padding-top: 2.4rem;
            padding-bottom: 5rem;
        }
        section[data-testid="stSidebar"] {
            background: #f4ecdf;
            border-right: 1px solid var(--line);
        }
        section[data-testid="stSidebar"] * {
            letter-spacing: 0;
        }
        h1, h2, h3 {
            color: var(--brown);
            letter-spacing: 0;
            font-weight: 650;
        }
        h1 {
            font-size: clamp(2.25rem, 5vw, 4.2rem);
            line-height: 0.98;
        }
        h2 {
            margin-top: 1.8rem;
        }
        p, label, .stMarkdown, [data-testid="stCaptionContainer"] {
            color: var(--charcoal);
        }
        .mango-hero {
            border-top: 1px solid var(--brown);
            border-bottom: 1px solid var(--line);
            padding: clamp(2rem, 5vw, 4.5rem) 0 clamp(1.6rem, 4vw, 3rem);
            margin-bottom: 2rem;
        }
        .mango-hero h1 {
            margin: 0 0 0.8rem 0;
            max-width: 760px;
        }
        .mango-hero p {
            color: var(--muted);
            font-size: clamp(1rem, 2vw, 1.18rem);
            line-height: 1.7;
            max-width: 710px;
            margin: 0;
        }
        .mango-kicker {
            color: var(--mango-muted);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            margin-bottom: 0.8rem;
            text-transform: uppercase;
        }
        .metric-card, .mango-card, .empty-state, .gallery-card, .score-panel, .section-panel, .variety-card {
            background: var(--paper);
            border: 1px solid var(--line);
            border-radius: 6px;
            box-shadow: 0 10px 30px rgba(52, 40, 32, 0.045);
        }
        .metric-card {
            min-height: 120px;
            padding: 1.1rem 1rem;
        }
        .metric-card .label {
            color: var(--muted);
            font-size: 0.78rem;
            letter-spacing: 0.08em;
            margin-bottom: 0.55rem;
            text-transform: uppercase;
        }
        .metric-card .value {
            color: var(--brown);
            font-size: clamp(1.45rem, 3vw, 2rem);
            font-weight: 650;
            line-height: 1.15;
        }
        .metric-card .hint {
            border-top: 1px solid rgba(52, 40, 32, 0.10);
            color: var(--muted);
            font-size: 0.86rem;
            margin-top: 0.8rem;
            padding-top: 0.55rem;
        }
        .mango-card {
            min-height: 220px;
            padding: 1.15rem;
            display: flex;
            flex-direction: column;
            gap: 0.7rem;
        }
        .mango-card img {
            width: 100%;
            aspect-ratio: 4 / 3;
            object-fit: cover;
            border-radius: 4px;
            margin-bottom: 0.4rem;
            filter: saturate(0.92) contrast(0.98);
        }
        .mango-card .title {
            color: var(--brown);
            font-weight: 650;
            font-size: 1.12rem;
            line-height: 1.28;
        }
        .mango-card .meta, .muted {
            color: var(--muted);
            font-size: 0.9rem;
            line-height: 1.45;
        }
        .mango-card .note {
            color: var(--charcoal);
            margin: 0;
            line-height: 1.55;
        }
        .maps-link {
            color: var(--mango-muted);
            font-size: 0.86rem;
            font-weight: 600;
            text-decoration: none;
        }
        .maps-link:hover {
            color: var(--brown);
            text-decoration: underline;
        }
        .score-badge {
            display: inline-flex;
            width: fit-content;
            max-width: 100%;
            padding: 0.28rem 0.62rem;
            border-radius: 999px;
            font-weight: 650;
            font-size: 0.8rem;
            border: 1px solid rgba(52, 40, 32, 0.14);
            background: #f5efe4;
            color: var(--brown);
            white-space: normal;
        }
        .score-exceptional {
            background: #efe0bf;
            border-color: rgba(177, 127, 41, 0.45);
        }
        .score-excellent, .score-very-good {
            background: #eee8d8;
        }
        .score-good {
            background: #f4ead7;
        }
        .score-fair, .score-disappointing, .score-missing {
            background: #f1ece6;
            color: #665a50;
        }
        .empty-state {
            padding: 1.4rem;
            text-align: left;
            color: var(--muted);
        }
        .empty-state strong {
            color: var(--brown);
            display: block;
            font-weight: 650;
            margin-bottom: 0.35rem;
        }
        .gallery-card {
            overflow: hidden;
            margin-bottom: 1.15rem;
        }
        .gallery-card img {
            width: 100%;
            aspect-ratio: 4 / 3;
            object-fit: cover;
            display: block;
            filter: saturate(0.9) contrast(0.98);
        }
        .gallery-card .body {
            padding: 0.95rem;
        }
        .variety-card {
            overflow: hidden;
            margin-bottom: 1.1rem;
            min-height: 360px;
        }
        .variety-card img, .variety-placeholder {
            width: 100%;
            aspect-ratio: 4 / 3;
            display: block;
        }
        .variety-card img {
            object-fit: cover;
            filter: saturate(0.88) contrast(0.98);
        }
        .variety-placeholder {
            background:
                linear-gradient(135deg, #f4ecdf, #fbf7ef);
            border-bottom: 1px solid var(--line);
            color: var(--muted);
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 1rem;
            font-size: 0.78rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .variety-card .body {
            padding: 1rem;
        }
        .variety-card .name {
            color: var(--brown);
            font-weight: 650;
            font-size: 1.05rem;
            margin-bottom: 0.45rem;
        }
        .variety-card .description {
            color: var(--charcoal);
            font-size: 0.92rem;
            line-height: 1.55;
        }
        .score-panel {
            padding: 1.15rem;
            background: #fbf7ef;
        }
        .score-panel .score-number {
            font-size: 2.2rem;
            font-weight: 650;
            line-height: 1;
            color: var(--brown);
            margin: 0.35rem 0;
        }
        .section-panel {
            padding: clamp(1rem, 3vw, 1.35rem);
            margin-bottom: 1.2rem;
        }
        .section-panel h3 {
            margin-top: 0;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid var(--line);
            border-radius: 6px;
        }
        .stButton > button {
            border-radius: 4px;
            font-weight: 600;
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
        empty_state("No tasting notes yet", "Add the first review to begin the guide.")
        return True
    return False


def page_title(title: str, caption: str | None = None) -> None:
    st.title(title)
    if caption:
        st.caption(caption)


def hero(title: str, subtitle: str, kicker: str = "Private gastronomic guide") -> None:
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
        return "Not scored", "score-missing"

    value = float(score)
    if value >= 9.0:
        return "Exceptional", "score-exceptional"
    if value >= 8.0:
        return "Excellent", "score-excellent"
    if value >= 7.0:
        return "Very Good", "score-very-good"
    if value >= 6.0:
        return "Good", "score-good"
    if value >= 5.0:
        return "Fair", "score-fair"
    return "Disappointing", "score-disappointing"


def score_badge(score: object, compact: bool = False) -> str:
    label, class_name = score_label(score)
    score_text = "N/A" if pd.isna(score) else f"{float(score):.1f}"
    text = score_text if compact else f"Score {score_text} - {label}"
    return f'<span class="score-badge {class_name}">{escape(text)}</span>'


def _has_value(value: object) -> bool:
    if value is None:
        return False
    if pd.isna(value):
        return False
    return bool(str(value).strip())


def build_google_maps_url(
    latitude: object = None,
    longitude: object = None,
    place_name: object = None,
    city: object = None,
) -> str | None:
    if _has_value(latitude) and _has_value(longitude):
        try:
            lat = float(latitude)
            lon = float(longitude)
        except (TypeError, ValueError):
            pass
        else:
            return f"https://www.google.com/maps/search/?api=1&query={lat:.6f},{lon:.6f}"

    query_bits = [str(bit).strip() for bit in (place_name, city) if _has_value(bit)]
    if len(query_bits) >= 2:
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(', '.join(query_bits))}"

    return None


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


def empty_state(title: str, body: str, icon: str | None = None) -> None:
    _ = icon
    st.markdown(
        f"""
        <div class="empty-state">
            <strong>{escape(title)}</strong>
            <span>{escape(body)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mango_card(row: pd.Series, rank: int | None = None, show_image: bool = False) -> None:
    title = row.get("name") or "Untitled tasting"
    score = row.get("final_score")
    place_bits = [row.get("place_name"), row.get("city")]
    place = ", ".join(str(bit) for bit in place_bits if pd.notna(bit) and bit)
    mango_origin = row.get("country")
    rank_label = f"No. {rank} " if rank is not None else ""
    image_url = row.get("image_url")
    image_html = ""
    if show_image and pd.notna(image_url) and str(image_url).strip() and not _is_local_image_path(str(image_url)):
        image_html = f'<img src="{escape(str(image_url), quote=True)}" alt="{escape(str(title), quote=True)}">'
    maps_url = build_google_maps_url(
        row.get("latitude"),
        row.get("longitude"),
        row.get("place_name"),
        row.get("city"),
    )
    maps_html = (
        f'<a class="maps-link" href="{escape(maps_url, quote=True)}" target="_blank" rel="noopener noreferrer">'
        "Open in Google Maps</a>"
        if maps_url
        else ""
    )

    st.markdown(
        f"""
        <div class="mango-card">
            {image_html}
            <div class="title">{escape(rank_label + str(title))}</div>
            <div class="meta">Category: {escape(str(row.get("category") or "Unspecified"))}</div>
            <div class="meta">Location: {escape(place or "Not recorded")}</div>
            <div class="meta">Mango origin: {escape(str(mango_origin) if _has_value(mango_origin) else "Unknown")}</div>
            {score_badge(score)}
            <p class="note">{escape(str(row.get("short_review") or "No notes recorded."))}</p>
            {maps_html}
            <div class="meta">Tasted by {escape(str(row.get("reviewer") or "Unknown reviewer"))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def review_card(row: pd.Series, rank: int | None = None) -> None:
    mango_card(row, rank=rank)


def _is_local_image_path(image_url: str) -> bool:
    return image_url.startswith("uploads/") or image_url.startswith("uploads\\")


def gallery_card(row: pd.Series) -> None:
    title = row.get("name") or "Untitled tasting"
    image_url = str(row.get("image_url") or "")
    location = " ".join(str(bit) for bit in [row.get("place_name"), row.get("city")] if pd.notna(bit) and bit)
    mango_origin = row.get("country")
    location_label = location or "Location not recorded"
    if _has_value(mango_origin):
        location_label = f"{location_label} - Mango origin: {mango_origin}"

    if _is_local_image_path(image_url) and Path(image_url).exists():
        st.image(image_url, use_container_width=True)
        st.markdown(
            f"""
            <div class="gallery-card">
                <div class="body">
                    <strong>{escape(str(title))}</strong>
                    <div style="margin: 0.45rem 0;">{score_badge(row.get("final_score"), compact=True)}</div>
                    <div class="muted">{escape(location_label)}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <div class="gallery-card">
            <img src="{escape(image_url, quote=True)}" alt="{escape(str(title), quote=True)}">
            <div class="body">
                <strong>{escape(str(title))}</strong>
                <div style="margin: 0.45rem 0;">{score_badge(row.get("final_score"), compact=True)}</div>
                <div class="muted">{escape(location_label)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _image_data_uri(image_path: Path) -> str | None:
    if not image_path.exists() or not image_path.is_file():
        return None

    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/jpeg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def mango_variety_card(name: str, description: str, image_path: str | Path) -> None:
    path = Path(image_path)
    image_uri = _image_data_uri(path)
    if image_uri:
        media_html = f'<img src="{image_uri}" alt="{escape(name, quote=True)}">'
    else:
        media_html = f'<div class="variety-placeholder">{escape(name)}</div>'

    st.markdown(
        f"""
        <div class="variety-card">
            {media_html}
            <div class="body">
                <div class="name">{escape(name)}</div>
                <div class="description">{escape(description)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def score_panel(score: float | None) -> None:
    score_text = "N/A" if score is None else f"{score:.1f}"
    st.markdown(
        f"""
        <div class="score-panel">
            <div class="muted">Calculated score</div>
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
        country = st.selectbox("Mango origin", ["All"] + countries)
    with cols[2]:
        reviewers = sorted(value for value in filtered["reviewer"].dropna().unique())
        reviewer = st.selectbox("Tasted by", ["All"] + reviewers)

    if category != "All":
        filtered = filtered[filtered["category"] == category]
    if country != "All":
        filtered = filtered[filtered["country"] == country]
    if reviewer != "All":
        filtered = filtered[filtered["reviewer"] == reviewer]

    return filtered
