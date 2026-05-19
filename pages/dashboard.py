from __future__ import annotations

import streamlit as st

from services.market_data import (
    fetch_asset_snapshot,
    fetch_price_history,
    fetch_sector_heatmap,
)
from services.news_service import fetch_news
from services.ai_engine import run_analysis

from components.header import render_header
from components.metrics_bar import render_metrics
from components.ai_panel import render_ai_panel
from components.charts import render_charts
from components.heatmap import render_heatmap
from components.news_feed import render_news_feed


@st.cache_data(ttl=300, show_spinner=False)
def _snapshot(query: str):
    return fetch_asset_snapshot(query)

@st.cache_data(ttl=300, show_spinner=False)
def _history(query: str, period: str):
    return fetch_price_history(query, period)

@st.cache_data(ttl=600, show_spinner=False)
def _news(ticker: str, sector: str):
    return fetch_news(ticker, sector)

@st.cache_data(ttl=300, show_spinner=False)
def _heatmap():
    return fetch_sector_heatmap()


def render(query: str, chart_period: str) -> None:

    with st.spinner("Fetching market snapshot..."):
        snapshot = _snapshot(query)

    with st.spinner("Loading price history..."):
        history_df = _history(query, chart_period)

    with st.spinner("Aggregating news across 16+ queries..."):
        articles = _news(snapshot.ticker, snapshot.sector)

    with st.spinner("Building sector heatmap..."):
        heatmap_data = _heatmap()

    with st.spinner("Running AI causal analysis..."):
        analysis = run_analysis(snapshot, articles)

    render_header(snapshot)
    render_metrics(snapshot)

    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("AI Market Intelligence")
        render_ai_panel(analysis)
        st.divider()
        st.subheader("Technical Analysis")
        render_charts(history_df, snapshot.ticker)

    with right_col:
        st.subheader("KSE-100 Sector Heatmap")
        render_heatmap(heatmap_data)
        st.divider()
        st.subheader("News Intelligence Feed")
        render_news_feed(articles)