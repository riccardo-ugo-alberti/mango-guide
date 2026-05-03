from __future__ import annotations

import pandas as pd
import streamlit as st

from src.db import load_reviews
from src.ui import configure_page, empty_state, hero, mango_card, mango_variety_card, metric_card


MANGO_VARIETIES = [
    {
        "name": "Alphonso",
        "image": "assets/mango_varieties/alphonso.jpg",
        "description": "Intensely aromatic, rich, creamy and deeply sweet. Often considered one of the finest Indian mangoes. Best tasted fresh when fully ripe.",
    },
    {
        "name": "Kesar",
        "image": "assets/mango_varieties/kesar.jpg",
        "description": "Fragrant, sweet and saffron-colored. Excellent fresh, but especially good in desserts, juices and lassi-style preparations.",
    },
    {
        "name": "Ataulfo / Honey",
        "image": "assets/mango_varieties/ataulfo.jpg",
        "description": "Small, buttery, very sweet and low in fiber. One of the most reliable varieties for fresh eating.",
    },
    {
        "name": "Kent",
        "image": "assets/mango_varieties/kent.jpg",
        "description": "Juicy, smooth and balanced, usually with low fiber. Good for fresh eating, smoothies and sorbets.",
    },
    {
        "name": "Keitt",
        "image": "assets/mango_varieties/keitt.jpg",
        "description": "Large and often green even when ripe. Mild, juicy and useful as a late-season mango.",
    },
    {
        "name": "Tommy Atkins",
        "image": "assets/mango_varieties/tommy-atkins.jpg",
        "description": "Very common and visually attractive, but often firmer, more fibrous and less aromatic than the best eating varieties.",
    },
]


configure_page("Mango Guide")

hero(
    "Mango Guide",
    "A small private guide to mango-led tastings, from fresh fruit to gelato, sorbet, desserts, drinks, and savory dishes.",
    "Tasting notes and rankings",
)

df, error = load_reviews()

if error:
    st.warning(error)

if df.empty:
    empty_state("No tasting notes yet", "Add the first review to begin the guide.")
else:
    total_reviews = len(df)
    average_score = df["final_score"].mean()
    scored = df.dropna(subset=["final_score"]).sort_values("final_score", ascending=False)
    best_review = scored.iloc[0] if not scored.empty else None
    country_count = df["country"].dropna().nunique()
    image_count = df["image_url"].dropna().astype(str).str.len().gt(0).sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Tasting notes", total_reviews, "Published reviews")
    with col2:
        metric_card("Average score", f"{average_score:.2f}" if pd.notna(average_score) else "N/A", "Out of 10")
    with col3:
        metric_card("Origins", country_count, "Countries recorded")
    with col4:
        metric_card("Images", image_count, "Visual records")

with st.expander("Our Suggestions"):
    st.markdown(
        """
        Mangoes are best tasted fresh and in season. Ripeness matters more than appearance:
        a good mango should feel slightly soft, smell aromatic near the stem, and feel heavy
        for its size. Avoid fruit that is completely hard, smells fermented, or seems
        excessively fibrous.

        For sorbets and gelato, mango intensity and natural acidity matter more than
        sweetness alone. The strongest tasting experiences balance aroma, texture,
        sweetness, acidity, and freshness.
        """
    )

    st.subheader("Mango Varieties")
    st.caption(
        "Variety matters. Some mangoes are floral and creamy, others are juicy, mild, fibrous or better suited to sorbets and desserts."
    )

    for start in range(0, len(MANGO_VARIETIES), 3):
        cols = st.columns(3)
        for offset, variety in enumerate(MANGO_VARIETIES[start : start + 3]):
            with cols[offset]:
                mango_variety_card(
                    variety["name"],
                    variety["description"],
                    variety["image"],
                )

if not df.empty:
    st.divider()

    left, right = st.columns([1.2, 0.8])
    with left:
        st.subheader("Highest Rated")
        if best_review is not None:
            mango_card(best_review, show_image=True)
        else:
            empty_state("No scores yet", "Add a scored tasting note to establish the first ranking.")

    with right:
        st.subheader("Recent Tasting Notes")
        recent = df.sort_values("created_at", ascending=False, na_position="last").head(5)
        for _, row in recent.iterrows():
            score = row.get("final_score")
            score_text = f"{score:.1f}" if pd.notna(score) else "N/A"
            st.markdown(f"**{row.get('name') or 'Untitled'}**")
            st.caption(f"Score {score_text} - {row.get('short_review') or 'No notes recorded.'}")

    st.subheader("Guide Sections")
    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        empty_state("Rankings", "Compare tasting notes by score.")
    with nav2:
        empty_state("Map", "View recorded origins and places.")
    with nav3:
        empty_state("Gallery", "Browse image-backed reviews.")
