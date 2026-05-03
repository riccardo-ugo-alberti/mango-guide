from __future__ import annotations

import os

import streamlit as st


def _debug_enabled() -> bool:
    try:
        raw_value = st.secrets.get("DEBUG", os.getenv("DEBUG", ""))
    except Exception:
        raw_value = os.getenv("DEBUG", "")

    return str(raw_value).strip().lower() in {"1", "true", "yes", "on"}


debug_enabled = _debug_enabled()
st.set_option("client.showErrorDetails", "full" if debug_enabled else "none")


pages = [
    st.Page("pages/0_Overview.py", title="Overview", default=True),
    st.Page("pages/1_Rankings.py", title="Rankings"),
    st.Page("pages/2_Map.py", title="Map"),
    st.Page("pages/3_Add_Review.py", title="Add Review"),
    st.Page("pages/4_Gallery.py", title="Gallery"),
    st.Page("pages/5_Statistics.py", title="Statistics"),
]


navigation = st.navigation(pages)
_ = navigation.run()
