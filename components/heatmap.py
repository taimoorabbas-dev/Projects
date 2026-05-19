"""components/heatmap.py — Sector heatmap + market breadth (pure Streamlit)."""
from __future__ import annotations
import streamlit as st
from services import chart_data


def render_heatmap(heatmap_data: list[dict]) -> None:
    st.markdown("**Sector Heatmap** — KSE-100 Blue Chips")

    if not heatmap_data:
        st.info("Loading sector data…")
        return

    try:
        fig = chart_data.sector_heatmap(heatmap_data)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    except Exception as e:
        st.warning(f"Heatmap unavailable: {e}")
        return

    # Market breadth
    valid  = [d for d in heatmap_data if d.get("pct_change") is not None]
    if not valid:
        return

    adv   = sum(1 for d in valid if d["pct_change"] > 0)
    dec   = sum(1 for d in valid if d["pct_change"] < 0)
    flat  = len(valid) - adv - dec
    best  = max(valid, key=lambda d: d["pct_change"])
    worst = min(valid, key=lambda d: d["pct_change"])

    st.divider()
    st.markdown("**Market Breadth**")
    b1, b2, b3, b4, b5, b6 = st.columns(6)
    with b1: st.metric("Advancing", adv)
    with b2: st.metric("Declining", dec)
    with b3: st.metric("Flat", flat)
    avg_chg = sum(d["pct_change"] for d in valid) / len(valid)
    with b4: st.metric("Avg Move", f"{avg_chg:+.2f}%")
    with b5: st.metric("Best",  best["ticker"],  f"+{best['pct_change']:.2f}%")
    with b6: st.metric("Worst", worst["ticker"], f"{worst['pct_change']:.2f}%", delta_color="inverse")
