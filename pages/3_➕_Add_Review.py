from __future__ import annotations

from datetime import date

import streamlit as st

from src.config import CURRENCIES, DEFAULT_CATEGORIES, REVIEWERS, get_settings
from src.db import insert_review
from src.scoring import SCORE_FIELDS, calculate_final_score
from src.ui import configure_page, page_title, score_panel


configure_page("Add Mango Review")
page_title("Add Review", "Log a new mango moment for the guide.")

settings = get_settings()
if not settings.app_password:
    st.warning("APP_PASSWORD is not configured. Add it to .env or Streamlit secrets to enable review entry.")
    st.stop()

password = st.text_input("Password", type="password")
if password != settings.app_password:
    st.info("Enter the app password to add a review.")
    st.stop()

st.markdown('<div class="section-panel">', unsafe_allow_html=True)
st.subheader("🥭 Tasting Snapshot")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name", placeholder="Alphonso sorbet at sunset")
    category = st.selectbox("Category", DEFAULT_CATEGORIES)
    reviewer = st.selectbox("Reviewer", REVIEWERS)
    date_tasted = st.date_input("Date tasted", value=date.today())
with col2:
    short_review = st.text_area("Short review", max_chars=500, placeholder="Bright, creamy, wildly mango-forward...")
    image_url = st.text_input("Image URL", placeholder="https://...")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-panel">', unsafe_allow_html=True)
st.subheader("📍 Place")
col1, col2, col3 = st.columns(3)
with col1:
    country = st.text_input("Country")
    city = st.text_input("City")
with col2:
    place_name = st.text_input("Place name")
    latitude = st.number_input("Latitude", value=None, format="%.6f", placeholder="Optional")
with col3:
    longitude = st.number_input("Longitude", value=None, format="%.6f", placeholder="Optional")
    public = st.checkbox("Public", value=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-panel">', unsafe_allow_html=True)
st.subheader("💸 Price")
col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    price = st.number_input("Price", value=None, min_value=0.0, step=0.5, placeholder="Optional")
with col2:
    currency = st.selectbox("Currency", CURRENCIES)
with col3:
    would_eat_again = st.checkbox("Would eat again", value=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-panel">', unsafe_allow_html=True)
st.subheader("⭐ Scorecard")
st.caption(
    "Scores use category-aware weights. Acidity is entered as a raw 0-10 score, then converted internally into balance: 5 is ideal, while too little or too much acidity is penalized."
)
score_values = {}
labels = {
    "sweetness": "Sweetness",
    "acidity": "Acidity raw score",
    "aroma": "Aroma",
    "texture": "Texture",
    "mango_intensity": "Mango intensity",
    "value_for_money": "Value for money",
}
score_cols = st.columns(2)
for index, field in enumerate(SCORE_FIELDS):
    with score_cols[index % 2]:
        score_values[field] = st.slider(labels[field], 0.0, 10.0, 7.0, 0.5)

score_values["category"] = category
suggested_score = calculate_final_score(score_values)
score_panel(suggested_score)

final_score = st.number_input(
    "Optional final score override",
    value=None,
    min_value=0.0,
    max_value=10.0,
    step=0.1,
    placeholder=f"Leave empty to use {suggested_score:.1f}",
)
st.markdown("</div>", unsafe_allow_html=True)

submitted = st.button("Add review", type="primary", use_container_width=True)

if submitted:
    payload = {
        "name": name,
        "category": category,
        "country": country,
        "city": city,
        "place_name": place_name,
        "latitude": latitude,
        "longitude": longitude,
        "date_tasted": date_tasted.isoformat(),
        "reviewer": reviewer,
        "price": price,
        "currency": currency,
        **score_values,
        "final_score": final_score,
        "short_review": short_review,
        "image_url": image_url,
        "would_eat_again": would_eat_again,
        "public": public,
    }
    ok, message = insert_review(payload)
    if ok:
        st.success(message)
    else:
        st.error(message)
