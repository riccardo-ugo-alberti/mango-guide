from __future__ import annotations

import streamlit as st

from src.db import load_reviews
from src.ui import configure_page, empty_state, gallery_card, page_title, show_data_notice


configure_page("Gallery")
page_title("Gallery", "Image-backed tasting notes.")

df, error = load_reviews()
if show_data_notice(error, df):
    st.stop()

gallery = df[df["image_url"].notna() & (df["image_url"].astype(str).str.len() > 0)]

if gallery.empty:
    empty_state("No images yet", "Upload an image or add an image URL to a review.")
    st.stop()

for start in range(0, len(gallery), 3):
    cols = st.columns(3)
    for offset, (_, row) in enumerate(gallery.iloc[start : start + 3].iterrows()):
        with cols[offset]:
            gallery_card(row)
