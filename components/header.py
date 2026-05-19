"""components/header.py — Asset header (pure Streamlit)."""
from __future__ import annotations
import streamlit as st
from services.market_data import AssetSnapshot


def render_header(snap: AssetSnapshot) -> None:
    pct      = snap.pct_change or 0.0
    is_up    = pct >= 0
    sign     = "+" if is_up else ""
    color    = "green" if is_up else "red"
    pct_str  = f"{sign}{pct:.2f}%"

    col_name, col_price = st.columns([3, 1])
    with col_name:
        st.title(snap.ticker)
        st.markdown(
            f"**{snap.full_name}**"
            f"  ·  {snap.sector}"
            f"  ·  :{color}[{snap.movement_label}]"
            f"  ·  :gray[{snap.volatility_tag}]"
        )
    with col_price:
        st.metric(
            "Current Price",
            f"PKR {snap.current_price:,.2f}" if snap.current_price else "—",
            pct_str,
            delta_color="normal",
        )

    if abs(pct) < 0.5:
        st.warning(
            "Movement is within normal market noise range — no significant catalyst detected.",
            icon="⚠️",
        )

    st.divider()
