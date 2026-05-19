"""
pages/market_overview.py
------------------------
Market-wide view with three tabs:
  1. Sector Heatmap  — live treemap + market breadth
  2. Sector Breakdown — all 10 sectors with clickable tickers
  3. Macro Indicators — SBP / PBS placeholders (live feed future phase)
"""

from __future__ import annotations
import streamlit as st

from services.market_data import fetch_sector_heatmap
from services.chart_data  import sector_heatmap as build_heatmap_fig
from config.constants     import SECTOR_MAP, PSX_TICKERS


def render() -> None:
    st.title("Market Overview")
    st.caption("Sector performance, heatmap, and macro indicators for KSE-100.")
    st.divider()

    # ── Index snapshot strip (placeholder — live feed pending) ───────────────
    st.markdown("**Index Snapshot**")
    i1, i2, i3, i4 = st.columns(4)
    with i1: st.metric("KSE-100",        "—", "Live feed pending")
    with i2: st.metric("KSE-30",         "—", "")
    with i3: st.metric("KMI-30",         "—", "")
    with i4: st.metric("KMI All-Share",  "—", "")

    st.divider()

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📊  Sector Heatmap", "🗂️  Sector Breakdown", "🌐  Macro Indicators"])

    # ── TAB 1: Heatmap ────────────────────────────────────────────────────────
    with tab1:
        with st.spinner("Fetching live prices for blue chips…"):
            try:
                heatmap_data = fetch_sector_heatmap()
            except Exception as e:
                st.error(f"Could not load heatmap: {e}")
                heatmap_data = []

        if heatmap_data:
            fig = build_heatmap_fig(heatmap_data)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            # Breadth stats
            valid = [d for d in heatmap_data if d.get("pct_change") is not None]
            adv   = sum(1 for d in valid if d["pct_change"] > 0)
            dec   = sum(1 for d in valid if d["pct_change"] < 0)
            flat  = len(valid) - adv - dec
            moves = [abs(d["pct_change"]) for d in valid]
            avg   = sum(moves) / len(moves) if moves else 0.0
            best  = max(valid, key=lambda d: d["pct_change"], default=None)
            worst = min(valid, key=lambda d: d["pct_change"], default=None)

            st.divider()
            st.markdown("**Market Breadth**")
            b1, b2, b3, b4 = st.columns(4)
            with b1: st.metric("Advancing", adv)
            with b2: st.metric("Declining",  dec)
            with b3: st.metric("Flat",        flat)
            with b4: st.metric("Avg Move",    f"{avg:.2f}%")

            if best and worst:
                b5, b6 = st.columns(2)
                with b5:
                    st.metric(f"Best · {best['ticker']}",   f"+{best['pct_change']:.2f}%")
                with b6:
                    st.metric(f"Worst · {worst['ticker']}", f"{worst['pct_change']:.2f}%")
        else:
            st.info("No heatmap data available. Check your internet connection or yfinance status.")

    # ── TAB 2: Sector Breakdown ───────────────────────────────────────────────
    with tab2:
        if not SECTOR_MAP:
            st.info("Sector data unavailable.")
        else:
            st.markdown(
                "All 10 KSE-100 sectors — click any ticker to open its AI workspace."
            )
            st.divider()
            for sector, tickers in SECTOR_MAP.items():
                with st.expander(f"**{sector}** — {len(tickers)} companies"):
                    # Show tickers as clickable buttons in a grid
                    cols = st.columns(min(len(tickers), 6))
                    for j, t in enumerate(tickers):
                        with cols[j % 6]:
                            if st.button(t, key=f"sect_{sector}_{t}", use_container_width=True):
                                st.session_state["ticker"] = t
                                st.session_state["page"]   = "Dashboard"
                                st.rerun()

    # ── TAB 3: Macro Indicators ───────────────────────────────────────────────
    with tab3:
        st.markdown("**Pakistan Macro Indicators**")
        st.info(
            "Live data from SBP, PBS, and IMF will be integrated in the next phase.  \n"
            "For now, these are the key indicators the AI engine watches when "
            "explaining stock movements.",
            icon="ℹ️",
        )
        st.divider()

        macro_rows = [
            [
                ("Policy Rate (SBP)",       "—", "SBP data pending"),
                ("CPI Inflation (YoY)",     "—", "PBS data pending"),
                ("PKR / USD",               "—", "FX feed pending"),
            ],
            [
                ("Forex Reserves (SBP)",    "—", "SBP data pending"),
                ("Current Account",         "—", "SBP data pending"),
                ("GDP Growth (YoY)",        "—", "PBS data pending"),
            ],
        ]
        for row in macro_rows:
            cols = st.columns(3)
            for col, (label, val, note) in zip(cols, row):
                with col:
                    st.metric(label, val, note)
            st.write("")

        st.divider()
        st.markdown(
            "**Why these matter:** The AI engine uses macro context to explain sector "
            "movements — e.g. an SBP rate cut directly affects banking NIM, while a "
            "PKR/USD depreciation boosts energy (Brent denominated) but pressures "
            "pharma and cement (import-cost sensitive)."
        )
