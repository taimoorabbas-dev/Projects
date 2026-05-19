"""components/charts.py — Chart rendering."""
from __future__ import annotations
import streamlit as st
import pandas as pd
from services import chart_data


def render_charts(df: pd.DataFrame, ticker: str) -> None:
    tab1, tab2 = st.tabs(["Candlestick + Indicators", "Returns Analysis"])

    with tab1:
        fig = chart_data.candlestick_chart(df, ticker)
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})
        st.caption(
            "Candlestick • MA-20 • MA-50 • Bollinger Bands • Volume"
            )

    with tab2:
        fig2 = chart_data.returns_chart(df, ticker)
        st.plotly_chart(fig2, use_container_width=True,
                        config={"displayModeBar": False})