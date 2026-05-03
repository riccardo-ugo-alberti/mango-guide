from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd
import streamlit as st

from src.config import CURRENCIES, DEFAULT_CATEGORIES, REVIEWERS, get_settings
from src.db import delete_review, get_admin_reviews, insert_review, update_review, upload_review_image
from src.scoring import SCORE_FIELDS, calculate_final_score
from src.ui import configure_page, empty_state, page_title, score_panel


configure_page("Admin")
page_title("Admin", "Create, edit, and curate mango tasting notes.")


def optional_text(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    return cleaned or None


def display_value(value: Any, fallback: str = "") -> str:
    if value is None or pd.isna(value):
        return fallback
    text = str(value).strip()
    if text.lower() == "nan":
        return fallback
    return text or fallback


def optional_number(value: Any) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def option_index(options: list[str], value: Any, default: int = 0) -> int:
    current = display_value(value)
    if current in options:
        return options.index(current)
    return default


def options_with_current(options: list[str], value: Any) -> list[str]:
    current = display_value(value)
    if current and current not in options:
        return [current, *options]
    return options


def parse_date(value: Any) -> date:
    if value is None or pd.isna(value):
        return date.today()
    if isinstance(value, date):
        return value
    try:
        return datetime.fromisoformat(str(value)).date()
    except ValueError:
        return date.today()


def review_options(df: pd.DataFrame) -> list[tuple[str, str]]:
    options: list[tuple[str, str]] = []
    for _, row in df.iterrows():
        review_id = str(row["id"])
        name = display_value(row.get("name"), "Untitled review")
        tasted = display_value(row.get("date_tasted"), "No date")
        reviewer = display_value(row.get("reviewer"), "Unknown reviewer")
        options.append((f"{name} - {tasted} - {reviewer} ({review_id})", review_id))
    return options


def build_payload(prefix: str, row: pd.Series | None = None) -> dict[str, Any] | None:
    row = row if row is not None else pd.Series(dtype=object)

    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader("Basic details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name", value=display_value(row.get("name")), placeholder="Alphonso sorbet", key=f"{prefix}_name")
        category_options = options_with_current(DEFAULT_CATEGORIES, row.get("category"))
        category = st.selectbox(
            "Category",
            category_options,
            index=option_index(category_options, row.get("category")),
            key=f"{prefix}_category",
        )
    with col2:
        reviewer_options = options_with_current(REVIEWERS, row.get("reviewer"))
        reviewer = st.selectbox(
            "Tasted by",
            reviewer_options,
            index=option_index(reviewer_options, row.get("reviewer")),
            key=f"{prefix}_reviewer",
        )
        date_tasted = st.date_input("Tasting date", value=parse_date(row.get("date_tasted")), key=f"{prefix}_date")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader("Location")
    st.caption("Location, mango origin, and map coordinates are optional.")
    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input(
            "City, optional",
            value=display_value(row.get("city")),
            help="Where the tasting took place, if you want to record it.",
            placeholder="Milan",
            key=f"{prefix}_city",
        )
    with col2:
        place_name = st.text_input(
            "Address / Place, optional",
            value=display_value(row.get("place_name")),
            help="Gelateria, market, restaurant, shop, address, or home tasting.",
            placeholder="Gelateria, market, restaurant, shop, address, or home",
            key=f"{prefix}_place_name",
        )

    country = st.text_input(
        "Mango origin, optional",
        value=display_value(row.get("country")),
        help="Origin of the mango itself, if known.",
        placeholder="India, Pakistan, Mexico, Peru, Thailand",
        key=f"{prefix}_country",
    )

    coord_col1, coord_col2 = st.columns(2)
    with coord_col1:
        latitude = st.number_input(
            "Latitude, optional",
            value=optional_number(row.get("latitude")),
            format="%.6f",
            placeholder="Optional",
            help=(
                "Optional. If left blank, the app will try to place the review on "
                "the map using Address / Place and City. Manual coordinates are "
                "still recommended for best accuracy."
            ),
            key=f"{prefix}_latitude",
        )
    with coord_col2:
        longitude = st.number_input(
            "Longitude, optional",
            value=optional_number(row.get("longitude")),
            format="%.6f",
            placeholder="Optional",
            help=(
                "Optional. If left blank, the app will try to place the review on "
                "the map using Address / Place and City. Manual coordinates are "
                "still recommended for best accuracy."
            ),
            key=f"{prefix}_longitude",
        )
    public = st.checkbox("Public", value=bool(row.get("public", True)), key=f"{prefix}_public")
    st.caption(
        "Latitude and longitude are optional. If left blank, the app will try to map "
        "the review from Address / Place and City; manual coordinates are still best "
        "for accuracy."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader("Scores")
    st.caption(
        "Acidity is entered as a raw 0-10 value, then converted internally into balance. A value near 5 is considered most balanced."
    )
    labels = {
        "sweetness": "Sweetness",
        "acidity": "Acidity raw score",
        "aroma": "Aroma",
        "texture": "Texture",
        "mango_intensity": "Mango intensity",
        "value_for_money": "Value for money",
    }
    score_values: dict[str, Any] = {}
    score_cols = st.columns(2)
    for index, field in enumerate(SCORE_FIELDS):
        with score_cols[index % 2]:
            score_values[field] = st.slider(
                labels[field],
                0.0,
                10.0,
                optional_number(row.get(field)) or 7.0,
                0.5,
                key=f"{prefix}_{field}",
            )

    score_values["category"] = category
    suggested_score = calculate_final_score(score_values)
    score_panel(suggested_score)

    final_score = st.number_input(
        "Optional score override",
        value=None,
        min_value=0.0,
        max_value=10.0,
        step=0.1,
        placeholder=f"Leave empty to use {suggested_score:.1f}",
        key=f"{prefix}_final_score",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader("Notes, optional")
    st.caption("Add tasting context, price, or revisit preference if it helps the record.")
    short_review = st.text_area(
        "Tasting notes, optional",
        value=display_value(row.get("short_review")),
        max_chars=500,
        placeholder="Texture, ripeness, aroma, finish...",
        key=f"{prefix}_short_review",
    )
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        price = st.number_input(
            "Price, optional",
            value=optional_number(row.get("price")),
            min_value=0.0,
            step=0.5,
            placeholder="Optional",
            key=f"{prefix}_price",
        )
    with col2:
        currency_options = options_with_current(CURRENCIES, row.get("currency"))
        currency = st.selectbox(
            "Currency, optional",
            currency_options,
            index=option_index(currency_options, row.get("currency")),
            key=f"{prefix}_currency",
        )
    with col3:
        would_eat_again = st.checkbox("Would taste again", value=bool(row.get("would_eat_again", True)), key=f"{prefix}_again")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-panel">', unsafe_allow_html=True)
    st.subheader("Image, optional")
    st.caption("Add an image if you have one. Reviews can also be saved without an image.")
    existing_image_url = display_value(row.get("image_url"))
    if existing_image_url:
        st.caption("Current image URL is kept unless you upload a new image or replace the URL below.")
    uploaded_image = st.file_uploader("Upload image from browser", type=["jpg", "jpeg", "png", "webp"], key=f"{prefix}_upload")
    image_url = st.text_input(
        "Image URL, optional",
        value=existing_image_url,
        placeholder="Paste an image URL if you have one",
        key=f"{prefix}_image_url",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if not name.strip():
        return None

    return {
        "name": name.strip(),
        "category": category,
        "country": optional_text(country),
        "city": optional_text(city),
        "place_name": optional_text(place_name),
        "latitude": latitude,
        "longitude": longitude,
        "date_tasted": date_tasted.isoformat(),
        "reviewer": reviewer,
        "price": price,
        "currency": currency,
        **score_values,
        "final_score": final_score,
        "short_review": optional_text(short_review),
        "image_url": optional_text(image_url),
        "_uploaded_image": uploaded_image,
        "would_eat_again": would_eat_again,
        "public": public,
    }


def apply_image_upload(payload: dict[str, Any]) -> dict[str, Any]:
    uploaded_image = payload.pop("_uploaded_image", None)
    if uploaded_image is None:
        return payload

    upload_ok, uploaded_url, upload_message = upload_review_image(uploaded_image)
    if upload_ok and upload_message:
        st.info(upload_message)
    if upload_ok:
        payload["image_url"] = uploaded_url
    else:
        st.warning("We couldn't attach the uploaded image. The review will still be saved without that upload.")

    return payload


def require_password() -> None:
    settings = get_settings()
    if not settings.app_password:
        st.warning("APP_PASSWORD is not configured. Add it to .env or Streamlit secrets to enable admin access.")
        st.stop()

    if st.session_state.get("admin_authenticated"):
        return

    password = st.text_input("Password", type="password")
    if password == settings.app_password:
        st.session_state["admin_authenticated"] = True
        st.rerun()

    st.info("Enter the app password to manage reviews.")
    st.stop()


require_password()

settings = get_settings()
if not settings.has_admin_credentials:
    st.warning("SUPABASE_SERVICE_ROLE_KEY is missing. Add it to enable add, edit, and delete actions.")
    st.stop()

add_tab, edit_tab, delete_tab = st.tabs(["Add Review", "Edit Review", "Delete Review"])

with add_tab:
    payload = build_payload("add")
    if st.button("Add review", type="primary", use_container_width=True, key="add_submit"):
        if payload is None:
            st.error("Add a name before saving the review.")
        else:
            ok, message = insert_review(apply_image_upload(payload))
            if ok:
                st.success(message)
            else:
                st.error(message)

with edit_tab:
    reviews, error = get_admin_reviews()
    if error:
        st.warning(error)
    elif reviews.empty:
        empty_state("No reviews yet", "Add the first review before editing.")
    else:
        options = review_options(reviews)
        labels = [label for label, _ in options]
        selected_label = st.selectbox("Select review", labels, key="edit_select")
        selected_id = dict(options)[selected_label]
        selected_row = reviews[reviews["id"].astype(str) == selected_id].iloc[0]
        payload = build_payload(f"edit_{selected_id}", selected_row)
        if st.button("Save changes", type="primary", use_container_width=True, key="edit_submit"):
            if payload is None:
                st.error("Add a name before saving the review.")
            else:
                ok, message = update_review(selected_id, apply_image_upload(payload))
                if ok:
                    st.success(message)
                else:
                    st.error(message)

with delete_tab:
    reviews, error = get_admin_reviews()
    if error:
        st.warning(error)
    elif reviews.empty:
        empty_state("No reviews yet", "There is nothing to delete.")
    else:
        options = review_options(reviews)
        labels = [label for label, _ in options]
        selected_label = st.selectbox("Select review to delete", labels, key="delete_select")
        selected_id = dict(options)[selected_label]
        selected_row = reviews[reviews["id"].astype(str) == selected_id].iloc[0]
        st.markdown('<div class="section-panel">', unsafe_allow_html=True)
        st.subheader(display_value(selected_row.get("name"), "Untitled review"))
        st.caption(
            f"{display_value(selected_row.get('category'), 'Unspecified category')} - "
            f"{display_value(selected_row.get('reviewer'), 'Unknown reviewer')} - "
            f"{display_value(selected_row.get('date_tasted'), 'No date')}"
        )
        note = display_value(selected_row.get("short_review"), "No notes recorded.")
        st.write(note)
        st.markdown("</div>", unsafe_allow_html=True)
        confirmed = st.checkbox("I understand this will permanently delete the selected review.", key="delete_confirm")
        if st.button("Delete review", type="primary", use_container_width=True, disabled=not confirmed, key="delete_submit"):
            ok, message = delete_review(selected_id)
            if ok:
                st.success(message)
            else:
                st.error(message)
