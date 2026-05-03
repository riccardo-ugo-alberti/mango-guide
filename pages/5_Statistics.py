from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.charts import MANGO_COLORS, score_distribution
from src.db import load_reviews
from src.scoring import SCORE_FIELDS
from src.ui import configure_page, empty_state, metric_card, page_title, show_data_notice


configure_page("Statistics")
page_title("Statistics", "A concise view of the guide's tasting data.")

df, error = load_reviews()
if show_data_notice(error, df):
    st.stop()

scored = df[df["final_score"].notna()].copy()

metric_cols = st.columns(4)
with metric_cols[0]:
    metric_card("Total reviews", len(df), "Published tasting notes")
with metric_cols[1]:
    metric_card("Average score", f"{scored['final_score'].mean():.2f}" if not scored.empty else "N/A", "Out of 10")
with metric_cols[2]:
    metric_card("Highest score", f"{scored['final_score'].max():.1f}" if not scored.empty else "N/A", "Best recorded")
with metric_cols[3]:
    metric_card("Lowest score", f"{scored['final_score'].min():.1f}" if not scored.empty else "N/A", "Lowest recorded")

if scored.empty:
    empty_state("No scored reviews yet", "Add scored tasting notes to unlock statistics.")
    st.stop()

st.divider()

left, right = st.columns(2)

with left:
    st.subheader("Average Score by Category")
    category_scores = (
        scored.dropna(subset=["category"])
        .groupby("category", as_index=False)["final_score"]
        .mean()
        .sort_values("final_score", ascending=False)
    )
    if len(category_scores) >= 1:
        fig = px.bar(
            category_scores,
            x="category",
            y="final_score",
            color="category",
            color_discrete_sequence=MANGO_COLORS,
        )
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Average score", template="plotly_white")
        fig.update_yaxes(range=[0, 10])
        st.plotly_chart(fig, use_container_width=True)
    else:
        empty_state("No category analysis", "Category averages need scored reviews with categories.")

with right:
    st.subheader("Average Score by Reviewer")
    reviewer_scores = (
        scored.dropna(subset=["reviewer"])
        .groupby("reviewer", as_index=False)["final_score"]
        .mean()
        .sort_values("final_score", ascending=False)
    )
    if len(reviewer_scores) >= 1:
        fig = px.bar(
            reviewer_scores,
            x="reviewer",
            y="final_score",
            color="reviewer",
            color_discrete_sequence=MANGO_COLORS,
        )
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Average score", template="plotly_white")
        fig.update_yaxes(range=[0, 10])
        st.plotly_chart(fig, use_container_width=True)
    else:
        empty_state("No reviewer analysis", "Reviewer averages need scored reviews with reviewers.")

left, right = st.columns(2)

with left:
    st.subheader("Score Distribution")
    if len(scored) >= 2:
        st.plotly_chart(score_distribution(scored), use_container_width=True)
    else:
        empty_state("No distribution yet", "Score distribution needs at least two scored reviews.")

with right:
    st.subheader("Category Mix")
    category_mix = df["category"].dropna()
    category_mix = category_mix[category_mix.astype(str).str.strip().ne("")]
    if not category_mix.empty:
        counts = category_mix.value_counts().rename_axis("category").reset_index(name="reviews")
        fig = px.pie(counts, names="category", values="reviews", color_discrete_sequence=MANGO_COLORS)
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        empty_state("No category mix", "Add categories to reviews to see the mix.")

left, right = st.columns(2)

with left:
    st.subheader("Criteria Averages")
    criteria = df[list(SCORE_FIELDS)].apply(pd.to_numeric, errors="coerce").mean().dropna()
    if not criteria.empty:
        criteria_df = criteria.rename_axis("criterion").reset_index(name="average_score")
        criteria_df["criterion"] = criteria_df["criterion"].str.replace("_", " ").str.title()
        fig = px.bar(
            criteria_df,
            x="average_score",
            y="criterion",
            orientation="h",
            color="average_score",
            color_continuous_scale="Brwnyl",
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Average score", yaxis_title="", template="plotly_white")
        fig.update_xaxes(range=[0, 10])
        st.plotly_chart(fig, use_container_width=True)
    else:
        empty_state("No criteria averages", "Criteria averages need individual scores.")

with right:
    st.subheader("Mango Origin Counts")
    origins = df["country"].dropna()
    origins = origins[origins.astype(str).str.strip().ne("")]
    origins = origins[origins.astype(str).str.lower().ne("nan")]
    if not origins.empty:
        counts = origins.value_counts().head(12).rename_axis("mango_origin").reset_index(name="reviews")
        fig = px.bar(
            counts,
            x="reviews",
            y="mango_origin",
            orientation="h",
            color="reviews",
            color_continuous_scale="Brwnyl",
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Reviews", yaxis_title="", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        empty_state("No mango origins yet", "Origin counts appear after reviews include mango origin.")
