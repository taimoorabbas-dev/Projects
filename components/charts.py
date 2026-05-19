"""components/charts.py — Price chart tabs (pure Streamlit)."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from services import chart_data


def render_charts(df: pd.DataFrame, ticker: str) -> None:
    st.markdown("**Price Chart**")
    tab_candle, tab_returns = st.tabs(["Candlestick + MA + Bollinger", "Returns"])

    with tab_candle:
        try:
            fig = chart_data.candlestick_chart(df, ticker)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("Candlestick · MA-20 · MA-50 · Bollinger Bands · Volume")
        except Exception as e:
            st.warning(f"Chart unavailable: {e}")

    with tab_returns:
        try:
            fig2 = chart_data.returns_chart(df, ticker)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        except Exception as e:
            st.warning(f"Returns chart unavailable: {e}")
