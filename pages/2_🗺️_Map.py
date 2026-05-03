from __future__ import annotations

import pandas as pd
import streamlit as st

from src.db import load_reviews
from src.ui import configure_page, page_title, show_data_notice


configure_page("Mango Map")
page_title("Mango Map", "A sunny trail of mango finds around the world.")

df, error = load_reviews()
if show_data_notice(error, df):
    st.stop()

map_df = df.dropna(subset=["latitude", "longitude"]).copy()
map_df = map_df.rename(columns={"latitude": "lat", "longitude": "lon"})

if map_df.empty:
    st.info("No reviews have coordinates yet.")
    st.stop()

st.map(map_df[["lat", "lon"]], size=120, color="#ff7a1a")

st.subheader("Mapped Reviews")
display_columns = ["name", "category", "country", "city", "place_name", "final_score", "lat", "lon"]
st.dataframe(map_df[display_columns], use_container_width=True, hide_index=True)

