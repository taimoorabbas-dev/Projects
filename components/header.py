"""components/header.py — Fintech-style Streamlit asset header."""

from __future__ import annotations

import streamlit as st

from services.market_data import AssetSnapshot
from utils.helpers import (
    fmt_price,
    fmt_pct,
)


def render_header(snap: AssetSnapshot) -> None:

    pct = snap.pct_change or 0

    arrow = "▲" if pct >= 0 else "▼"

    delta_color = "normal" if pct >= 0 else "inverse"

    # ─────────────────────────────────────────────
    # Top subtle market context
    # ─────────────────────────────────────────────

    st.caption(
        f"{snap.sector.upper()}  •  {snap.ticker}  •  PAKISTAN STOCK EXCHANGE"
    )

    # ─────────────────────────────────────────────
    # Main header layout
    # ─────────────────────────────────────────────

    left_col, right_col = st.columns([3.5, 1.5])

    # ─────────────────────────────────────────────
    # LEFT SIDE
    # ─────────────────────────────────────────────

    with left_col:

        st.markdown(
            f"""
            ### {snap.full_name}
            """
        )

        tag_col1, tag_col2 = st.columns(2)

        with tag_col1:

            st.info(
                f"Volatility: {snap.volatility_tag}"
            )

        with tag_col2:

            st.info(
                f"Movement: {snap.movement_label}"
            )

    # ─────────────────────────────────────────────
    # RIGHT SIDE
    # ─────────────────────────────────────────────

    with right_col:

        st.metric(
            label="Current Price",
            value=fmt_price(
                snap.current_price,
                snap.currency
            ),
            delta=f"{arrow} {fmt_pct(pct)}",
            delta_color=delta_color
        )

    # ─────────────────────────────────────────────
    # Noise Detection Banner
    # ─────────────────────────────────────────────

    if abs(pct) < 0.5:

        st.warning(
            "Current movement appears within normal market noise range."
        )

    # ─────────────────────────────────────────────
    # Divider
    # ─────────────────────────────────────────────

    st.divider()