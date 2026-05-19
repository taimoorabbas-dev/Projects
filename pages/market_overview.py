from __future__ import annotations

import streamlit as st
import pandas as pd

from config.constants import SECTOR_MAP, EARNINGS_SENSITIVITY
from services.market_data import fetch_sector_heatmap
from services import chart_data


@st.cache_data(ttl=300, show_spinner=False)
def _heatmap():
    return fetch_sector_heatmap()


def render() -> None:

    st.title("KSE-100 Market Overview")
    st.caption(
        "Live snapshot of Pakistan Stock Exchange blue chips. "
        "Data from yfinance (15-20 min delay)."
    )

    st.divider()

    with st.spinner("Loading heatmap..."):
        heatmap_data = _heatmap()

    st.subheader("Blue Chip Heatmap")
    fig = chart_data.sector_heatmap(heatmap_data)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.divider()

    st.subheader("Gainers & Losers")

    valid = [d for d in heatmap_data if d.get("pct_change") is not None]

    if valid:
        df = pd.DataFrame(valid).rename(columns={
            "ticker":     "Ticker",
            "name":       "Company",
            "sector":     "Sector",
            "pct_change": "Today %",
            "price":      "Price (PKR)",
        })
        df = df.sort_values("Today %", ascending=False)

        col_gain, col_lose = st.columns(2)

        with col_gain:
            st.caption("🟢 Top Gainers")
            top5 = df[df["Today %"] > 0].head(5)[
                ["Ticker", "Company", "Today %", "Price (PKR)"]
            ]
            st.dataframe(
                top5,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Today %": st.column_config.NumberColumn(format="%.2f%%"),
                    "Price (PKR)": st.column_config.NumberColumn(format="PKR %.2f"),
                },
            )

        with col_lose:
            st.caption("🔴 Top Losers")
            bot5 = df[df["Today %"] < 0].tail(5).sort_values("Today %")[
                ["Ticker", "Company", "Today %", "Price (PKR)"]
            ]
            st.dataframe(
                bot5,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Today %": st.column_config.NumberColumn(format="%.2f%%"),
                    "Price (PKR)": st.column_config.NumberColumn(format="PKR %.2f"),
                },
            )

    st.divider()

    st.subheader("Sector Intelligence")
    st.caption(
        "What drives each sector's earnings — "
        "understanding this is how you understand PSX."
    )

    for sector, tickers in SECTOR_MAP.items():
        sensitivity = EARNINGS_SENSITIVITY.get(sector, {})
        biz_model   = sensitivity.get("business_model_plain_english", "")
        driver      = sensitivity.get("primary_revenue_driver", "")
        sensitivities = sensitivity.get("sensitivities", [])

        with st.expander(f"**{sector}** — {', '.join(tickers[:4])}..."):

            if biz_model:
                st.info(f"**How this sector makes money:** {biz_model}")

            if driver:
                st.caption(f"Primary earnings driver: {driver}")

            if sensitivities:
                st.caption("**Key variables that move stock prices in this sector:**")
                for s in sensitivities[:3]:
                    with st.container(border=True):
                        st.markdown(f"**{s['variable']}** — {s['direction']}")
                        st.caption(s.get("simple_explanation", ""))
                        if s.get("magnitude"):
                            st.caption(f"Magnitude: *{s['magnitude']}*")

            regulators = sensitivity.get("regulators", [])
            if regulators:
                st.caption(f"Regulators: {' · '.join(regulators)}")