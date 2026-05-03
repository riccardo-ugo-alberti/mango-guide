from __future__ import annotations

import streamlit as st

from src.db import load_reviews
from src.ui import configure_page, page_title, show_data_notice


configure_page("Map")
page_title("Map", "Recorded places and origins with coordinates.")

df, error = load_reviews()
if show_data_notice(error, df):
    st.stop()

map_df = df.dropna(subset=["latitude", "longitude"]).copy()
map_df = map_df.rename(columns={"latitude": "lat", "longitude": "lon"})

if map_df.empty:
    st.info("No tasting notes have coordinates yet.")
    st.stop()

st.map(map_df[["lat", "lon"]], size=95, color="#b88732")

st.subheader("Mapped Tasting Notes")
display_columns = ["name", "category", "country", "city", "place_name", "final_score", "lat", "lon"]
display = map_df[display_columns].rename(
    columns={
        "name": "Name",
        "category": "Category",
        "country": "Origin",
        "city": "City",
        "place_name": "Place",
        "final_score": "Score",
    }
)
st.dataframe(display, use_container_width=True, hide_index=True)
