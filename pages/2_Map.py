from __future__ import annotations

from html import escape
from typing import Any

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

try:
    from geopy.exc import GeocoderServiceError, GeocoderTimedOut
    from geopy.geocoders import Nominatim
except ImportError:  # pragma: no cover - handled in the UI.
    GeocoderServiceError = GeocoderTimedOut = Exception
    Nominatim = None

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


def has_value(value: Any) -> bool:
    if value is None or pd.isna(value):
        return False
    text = str(value).strip()
    return bool(text and text.lower() != "nan")


def format_value(value: object, fallback: str = "") -> str:
    return str(value).strip() if has_value(value) else fallback


def format_score(value: object) -> str:
    if value is None or pd.isna(value):
        return "N/A"
    return f"{float(value):.1f}"


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


def location_query(row: pd.Series) -> str | None:
    bits = [format_value(row.get("place_name")), format_value(row.get("city"))]
    query = ", ".join(bit for bit in bits if bit)
    return query or None


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def geocode_location(query: str) -> tuple[float, float] | None:
    if Nominatim is None:
        return None

    try:
        geolocator = Nominatim(user_agent="mango-guide", timeout=4)
        location = geolocator.geocode(query, exactly_one=True, timeout=4)
    except (GeocoderTimedOut, GeocoderServiceError, TimeoutError, ValueError):
        return None

    if location is None:
        return None

    return float(location.latitude), float(location.longitude)


def map_coordinates(row: pd.Series) -> tuple[float | None, float | None, str | None]:
    if has_value(row.get("latitude")) and has_value(row.get("longitude")):
        try:
            return float(row["latitude"]), float(row["longitude"]), "manual coordinates"
        except (TypeError, ValueError):
            pass

    query = location_query(row)
    if not query:
        return None, None, None

    geocoded = geocode_location(query)
    if geocoded is None:
        return None, None, None

    lat, lon = geocoded
    return lat, lon, "geocoded address/city"


def mapped_reviews(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    mapped_rows: list[dict[str, Any]] = []
    unmapped_rows: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        lat, lon, source = map_coordinates(row)
        row_data = row.to_dict()
        query = location_query(row)
        row_data["map_query"] = query

        if lat is None or lon is None or source is None:
            if query:
                unmapped_rows.append(row_data)
            continue

        row_data["map_latitude"] = lat
        row_data["map_longitude"] = lon
        row_data["map_source"] = source
        mapped_rows.append(row_data)

    return pd.DataFrame(mapped_rows), pd.DataFrame(unmapped_rows)


def optional_row(label: str, value: object) -> str:
    text = format_value(value)
    if not text:
        return ""
    return f"<tr><th>{escape(label)}</th><td>{escape(text)}</td></tr>"


def popup_html(row: pd.Series) -> str:
    maps_url = build_google_maps_url(
        row.get("map_latitude"),
        row.get("map_longitude"),
        row.get("place_name"),
        row.get("city"),
    )
    maps_link = ""
    if maps_url:
        maps_link = (
            f'<a href="{escape(maps_url, quote=True)}" target="_blank" rel="noopener noreferrer">'
            "Open in Google Maps</a>"
        )

    score_rows = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(format_score(row.get(field)))}</td></tr>"
        for field, label in SCORE_FIELDS
    )

    note = format_value(row.get("short_review"))
    note_html = f'<p style="line-height: 1.45;">{escape(note)}</p>' if note else ""

    return f"""
    <div style="font-family: Inter, Segoe UI, sans-serif; color: #252322; width: 310px;">
        <h4 style="margin: 0 0 8px; color: #342820; font-size: 17px;">{escape(format_value(row.get("name"), "Untitled tasting"))}</h4>
        <div style="margin-bottom: 8px; color: #756a60;">{escape(format_value(row.get("category"), "Unspecified category"))}</div>
        <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
            <tr><th>Final score</th><td>{escape(format_score(row.get("final_score")))}</td></tr>
            {optional_row("Tasted by", row.get("reviewer"))}
            {optional_row("Tasting date", row.get("date_tasted"))}
            {optional_row("City", row.get("city"))}
            {optional_row("Address / Place", row.get("place_name"))}
            {optional_row("Mango origin", row.get("country"))}
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
    "Reviews with coordinates are mapped directly. Reviews with only Address / Place and City are placed with approximate open geocoding."
)

df, error = load_reviews()
if show_data_notice(error, df):
    st.stop()

if "public" in df.columns:
    df = df[df["public"].fillna(False)]

if Nominatim is None:
    st.warning("Address/city geocoding is unavailable until geopy is installed.")

map_df, not_mapped_df = mapped_reviews(df)

if map_df.empty:
    empty_state(
        "No mapped tastings yet",
        "Add coordinates, city, or address/place details to place reviews on the map.",
    )
    if not not_mapped_df.empty:
        st.subheader("Not Mapped Yet")
        st.dataframe(
            not_mapped_df[["name", "city", "place_name", "map_query"]].fillna("").rename(
                columns={
                    "name": "Name",
                    "city": "City",
                    "place_name": "Address / Place",
                    "map_query": "Geocoding query",
                }
            ),
            use_container_width=True,
            hide_index=True,
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
        f"{format_score(row.get('final_score'))}"
    )
    city = format_value(row.get("city"))
    if city:
        tooltip = f"{tooltip} - {city}"

    folium.CircleMarker(
        location=[float(row["map_latitude"]), float(row["map_longitude"])],
        radius=radius,
        color=color,
        weight=2,
        fill=True,
        fill_color=color,
        fill_opacity=0.78,
        tooltip=escape(tooltip),
        popup=folium.Popup(popup_html(row), max_width=370),
    ).add_to(mango_map)

st_folium(mango_map, use_container_width=True, height=620)

st.subheader("Mapped Reviews")
display = map_df.copy()
display["Google Maps"] = display.apply(
    lambda row: build_google_maps_url(row["map_latitude"], row["map_longitude"], row.get("place_name"), row.get("city")),
    axis=1,
)
display = display[
    ["name", "category", "final_score", "city", "place_name", "country", "map_source", "Google Maps"]
].rename(
    columns={
        "name": "Name",
        "category": "Category",
        "final_score": "Score",
        "city": "City",
        "place_name": "Address / Place",
        "country": "Mango origin",
        "map_source": "Map source",
    }
)
display = display.fillna("")

st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Google Maps": st.column_config.LinkColumn("Google Maps", display_text="Open"),
        "Score": st.column_config.NumberColumn("Score", format="%.1f"),
    },
)

if not not_mapped_df.empty:
    st.subheader("Not Mapped Yet")
    st.caption("These reviews have address or city text, but open geocoding could not place them.")
    missing_display = not_mapped_df[["name", "city", "place_name", "map_query"]].fillna("").rename(
        columns={
            "name": "Name",
            "city": "City",
            "place_name": "Address / Place",
            "map_query": "Geocoding query",
        }
    )
    st.dataframe(missing_display, use_container_width=True, hide_index=True)
