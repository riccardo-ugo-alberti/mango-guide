from __future__ import annotations

import streamlit as st

from src.db import load_reviews
from src.ui import configure_page, empty_state, filtered_reviews, mango_card, page_title, show_data_notice


configure_page("Rankings")
page_title("Rankings", "A ranked index of tasting notes.")

df, error = load_reviews()
if show_data_notice(error, df):
    st.stop()

filtered = filtered_reviews(df)
filtered = filtered.sort_values("final_score", ascending=False, na_position="last")

st.subheader("Top Three")
top_three = filtered.head(3)
if top_three.empty:
    empty_state("No matches", "Try loosening the filters.")
else:
    cols = st.columns(3)
    for index, (_, row) in enumerate(top_three.iterrows()):
        with cols[index]:
            mango_card(row, rank=index + 1, show_image=True)

st.subheader("Full Ranking")
columns = [
    "name",
    "category",
    "country",
    "city",
    "place_name",
    "reviewer",
    "final_score",
    "would_eat_again",
]
display = filtered[columns].rename(
    columns={
        "name": "Name",
        "category": "Category",
        "country": "Origin",
        "city": "City",
        "place_name": "Place",
        "reviewer": "Tasted by",
        "final_score": "Score",
        "would_eat_again": "Would taste again",
    }
)
st.dataframe(display, use_container_width=True, hide_index=True)
