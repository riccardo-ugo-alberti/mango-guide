from __future__ import annotations

import streamlit as st


pages = [
    st.Page("pages/0_Overview.py", title="Overview", default=True),
    st.Page("pages/1_Rankings.py", title="Rankings"),
    st.Page("pages/2_Map.py", title="Map"),
    st.Page("pages/3_Add_Review.py", title="Add Review"),
    st.Page("pages/4_Gallery.py", title="Gallery"),
    st.Page("pages/5_Statistics.py", title="Statistics"),
]


navigation = st.navigation(pages)
navigation.run()
