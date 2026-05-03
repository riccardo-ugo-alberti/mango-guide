from __future__ import annotations

import pandas as pd
import streamlit as st

from src.db import load_reviews
from src.ui import configure_page, empty_state, gallery_card, page_title, show_data_notice


configure_page("Mango Gallery")
page_title("Mango Gallery", "A visual shelf for mangoes worth remembering.")

df, error = load_reviews()
if show_data_notice(error, df):
    st.stop()

gallery = df[df["image_url"].notna() & (df["image_url"].astype(str).str.len() > 0)]

if gallery.empty:
    empty_state("No images yet", "Add an image URL to a review and it will appear here.", "📸")
    st.stop()

for start in range(0, len(gallery), 3):
    cols = st.columns(3)
    for offset, (_, row) in enumerate(gallery.iloc[start : start + 3].iterrows()):
        with cols[offset]:
            gallery_card(row)
