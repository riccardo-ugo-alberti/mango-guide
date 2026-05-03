from __future__ import annotations

import streamlit as st

from src.charts import category_chart, country_chart, reviewer_chart, score_distribution
from src.db import load_reviews
from src.ui import configure_page, page_title, show_data_notice


configure_page("Mango Stats")
page_title("Mango Stats", "Patterns from the mango notebook.")

df, error = load_reviews()
if show_data_notice(error, df):
    st.stop()

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(category_chart(df), use_container_width=True)
with col2:
    st.plotly_chart(country_chart(df), use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(reviewer_chart(df), use_container_width=True)
with col2:
    st.plotly_chart(score_distribution(df), use_container_width=True)

