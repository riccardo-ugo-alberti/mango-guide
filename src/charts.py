from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


MANGO_COLORS = ["#b88732", "#8f6f4e", "#4f463d", "#c9b89f", "#6f6258", "#d9c79f"]


def _empty_figure(message: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, x=0.5, y=0.5)
    fig.update_layout(height=320, template="plotly_white")
    return fig


def category_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "category" not in df:
        return _empty_figure("No category data yet.")
    counts = df["category"].fillna("Unknown").value_counts().reset_index()
    counts.columns = ["category", "reviews"]
    fig = px.bar(counts, x="category", y="reviews", color="category", color_discrete_sequence=MANGO_COLORS)
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Reviews", template="plotly_white")
    return fig


def country_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "country" not in df:
        return _empty_figure("No country data yet.")
    counts = df["country"].fillna("Unknown").value_counts().head(12).reset_index()
    counts.columns = ["country", "reviews"]
    fig = px.bar(counts, x="reviews", y="country", orientation="h", color="reviews", color_continuous_scale="Brwnyl")
    fig.update_layout(coloraxis_showscale=False, xaxis_title="Reviews", yaxis_title="", template="plotly_white")
    return fig


def reviewer_chart(df: pd.DataFrame) -> go.Figure:
    if df.empty or "reviewer" not in df:
        return _empty_figure("No reviewer data yet.")
    grouped = (
        df.groupby("reviewer", dropna=False)["final_score"]
        .agg(["count", "mean"])
        .reset_index()
        .rename(columns={"count": "reviews", "mean": "average_score"})
    )
    grouped["reviewer"] = grouped["reviewer"].fillna("Unknown")
    fig = px.bar(
        grouped,
        x="reviewer",
        y="average_score",
        text="reviews",
        color="reviewer",
        color_discrete_sequence=MANGO_COLORS,
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Average score", template="plotly_white")
    fig.update_yaxes(range=[0, 10])
    return fig


def score_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty or df["final_score"].dropna().empty:
        return _empty_figure("No score data yet.")
    fig = px.histogram(df, x="final_score", nbins=10, color_discrete_sequence=["#b88732"])
    fig.update_layout(xaxis_title="Final score", yaxis_title="Reviews", template="plotly_white")
    fig.update_xaxes(range=[0, 10])
    return fig
