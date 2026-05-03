from __future__ import annotations

import pandas as pd
import streamlit as st

from src.db import load_reviews
from src.ui import configure_page, empty_state, hero, mango_card, metric_card


configure_page("Mango Guide")

hero(
    "Mango Guide",
    "Rating the world, one mango at a time. A public notebook for fresh mangoes, gelato, sorbet, desserts, drinks, and every golden bite worth remembering.",
    "🥭 Two reviewers, many mangoes",
)

df, error = load_reviews()

if error:
    st.warning(error)

if df.empty:
    empty_state(
        "The mango shelf is ready",
        "Add the first public review to start building the guide.",
        "🥭",
    )
else:
    total_reviews = len(df)
    average_score = df["final_score"].mean()
    scored = df.dropna(subset=["final_score"]).sort_values("final_score", ascending=False)
    best_review = scored.iloc[0] if not scored.empty else None
    country_count = df["country"].dropna().nunique()
    image_count = df["image_url"].dropna().astype(str).str.len().gt(0).sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Reviews logged", total_reviews, "Tiny trophies of mango research")
    with col2:
        metric_card("Average score", f"{average_score:.2f}" if pd.notna(average_score) else "N/A", "Out of 10")
    with col3:
        metric_card("Countries", country_count, "Where the mango trail goes")
    with col4:
        metric_card("Photo notes", image_count, "Gallery-ready moments")

    st.divider()

    left, right = st.columns([1.2, 0.8])
    with left:
        st.subheader("🏆 Current Mango Champion")
        if best_review is not None:
            mango_card(best_review, show_image=True)
        else:
            empty_state("No champion yet", "Score a review and the crown appears here.", "🏆")

    with right:
        st.subheader("Latest Field Notes")
        recent = df.sort_values("created_at", ascending=False, na_position="last").head(5)
        for _, row in recent.iterrows():
            score = row.get("final_score")
            score_text = f"{score:.1f}" if pd.notna(score) else "N/A"
            st.markdown(f"**{row.get('name') or 'Untitled'}** - {score_text}/10")
            st.caption(row.get("short_review") or "No note yet.")

    st.subheader("Browse the Guide")
    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        empty_state("Ranking", "Find the highest-rated mango experiences.", "🏆")
    with nav2:
        empty_state("Map", "See where the mango trail has landed.", "🗺️")
    with nav3:
        empty_state("Gallery", "Browse the most photogenic bites.", "📸")
