from __future__ import annotations

from html import escape

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from src.db import load_reviews
from src.ui import build_google_maps_url, configure_page, empty_state, page_title, show_data_notice


SCORE_FIELDS = [
    ("sweetness", "Sweetness"),
    ("acidity", "Acidity"),
    ("aroma", "Aroma"),
    ("texture", "Texture"),
    ("mango_intensity", "Mango intensity"),
    ("value_for_money", "Value for money"),
]


def score_style(score: object) -> tuple[str, int]:
    if pd.isna(score):
        return "#9c9288", 5

    value = float(score)
    if value >= 9.0:
        return "#7f5314", 9
    if value >= 8.0:
        return "#b88732", 8
    if value >= 7.0:
        return "#c9a55d", 7
    return "#9c9288", 6


def format_value(value: object, fallback: str = "Not recorded") -> str:
    if value is None or pd.isna(value) or not str(value).strip():
        return fallback
    return str(value)


def format_score(value: object) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value):.1f}"


def popup_html(row: pd.Series) -> str:
    maps_url = build_google_maps_url(
        row.get("latitude"),
        row.get("longitude"),
        row.get("place_name"),
        row.get("city"),
    )
    maps_link = ""
    if maps_url:
        maps_link = (
            f'<a href="{escape(maps_url, quote=True)}" target="_blank" rel="noopener noreferrer">'
            "Open in Google Maps</a>"
        )

    optional_rows = ""
    if format_value(row.get("place_name"), ""):
        optional_rows += f"<tr><th>Address / Place</th><td>{escape(format_value(row.get('place_name')))}</td></tr>"
    if format_value(row.get("country"), ""):
        optional_rows += f"<tr><th>Mango origin</th><td>{escape(format_value(row.get('country'), 'Unknown'))}</td></tr>"

    score_rows = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(format_score(row.get(field)))}</td></tr>"
        for field, label in SCORE_FIELDS
    )

    note = format_value(row.get("short_review"), "")
    note_html = f'<p class="note">{escape(note)}</p>' if note else ""

    return f"""
    <div style="font-family: Inter, Segoe UI, sans-serif; color: #252322; width: 300px;">
        <h4 style="margin: 0 0 8px; color: #342820; font-size: 17px;">{escape(format_value(row.get("name"), "Untitled tasting"))}</h4>
        <div style="margin-bottom: 8px; color: #756a60;">{escape(format_value(row.get("category"), "Unspecified"))}</div>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <tr><th>Overall score</th><td>{escape(format_score(row.get("final_score")))}</td></tr>
            <tr><th>Tasted by</th><td>{escape(format_value(row.get("reviewer"), "Unknown reviewer"))}</td></tr>
            <tr><th>Tasting date</th><td>{escape(format_value(row.get("date_tasted")))}</td></tr>
            <tr><th>City</th><td>{escape(format_value(row.get("city")))}</td></tr>
            {optional_rows}
        </table>
        {note_html}
        <div style="margin: 10px 0 4px; font-weight: 650; color: #342820;">Individual scores</div>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            {score_rows}
        </table>
        <div style="margin-top: 10px; font-size: 13px;">{maps_link}</div>
    </div>
    """


configure_page("Map")
page_title("Map", "A geographic record of mango tastings.")
st.caption(
    "A geographic record of where each mango tasting took place. Add latitude and longitude to place a review on the map."
)

df, error = load_reviews()
if show_data_notice(error, df):
    st.stop()

if "public" in df.columns:
    df = df[df["public"].fillna(False)]

map_df = df.dropna(subset=["latitude", "longitude"]).copy()

if map_df.empty:
    empty_state(
        "No mapped tastings yet",
        "Reviews need latitude and longitude before they can appear on the map.",
    )
    st.stop()

mango_map = folium.Map(
    location=[20, 0],
    zoom_start=2,
    tiles="CartoDB positron",
    control_scale=True,
)

for _, row in map_df.iterrows():
    color, radius = score_style(row.get("final_score"))
    tooltip = (
        f"{format_value(row.get('name'), 'Untitled tasting')} - "
        f"{format_score(row.get('final_score'))} - "
        f"{format_value(row.get('city'), 'No city')}"
    )
    folium.CircleMarker(
        location=[float(row["latitude"]), float(row["longitude"])],
        radius=radius,
        color=color,
        weight=2,
        fill=True,
        fill_color=color,
        fill_opacity=0.78,
        tooltip=escape(tooltip),
        popup=folium.Popup(popup_html(row), max_width=360),
    ).add_to(mango_map)

st_folium(mango_map, use_container_width=True, height=620)

st.subheader("Mapped Reviews")
display = map_df.copy()
display["Google Maps"] = display.apply(
    lambda row: build_google_maps_url(row["latitude"], row["longitude"], row.get("place_name"), row.get("city")),
    axis=1,
)
display = display[
    ["name", "category", "final_score", "city", "place_name", "country", "Google Maps"]
].rename(
    columns={
        "name": "Name",
        "category": "Category",
        "final_score": "Score",
        "city": "City",
        "place_name": "Address / Place",
        "country": "Mango origin",
    }
)

st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Google Maps": st.column_config.LinkColumn("Google Maps", display_text="Open"),
        "Score": st.column_config.NumberColumn("Score", format="%.1f"),
    },
)
