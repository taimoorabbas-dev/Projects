"""components/metrics_bar.py — Market metrics row."""

from __future__ import annotations

import streamlit as st

from services.market_data import AssetSnapshot

from utils.helpers import (
    fmt_price,
    fmt_volume,
    fmt_market_cap,
    fmt_pe,
)


def render_metrics(
    snap: AssetSnapshot
) -> None:

    # ─────────────────────────────────────────────
    # Top Metrics Row
    # ─────────────────────────────────────────────

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:

        st.metric(
            "Prev Close",
            fmt_price(snap.prev_close)
        )

    with c2:

        rng = (
            f"{snap.day_low or 'N/A'} – {snap.day_high or 'N/A'}"
            if snap.day_low and snap.day_high
            else "N/A"
        )

        st.metric(
            "Day Range",
            rng
        )

    with c3:

        st.metric(
            "Volume",
            fmt_volume(snap.volume)
        )

    with c4:

        st.metric(
            "Market Cap",
            fmt_market_cap(snap.market_cap)
        )

    with c5:

        st.metric(
            "P/E Ratio",
            fmt_pe(snap.pe_ratio)
        )

    with c6:

        rng52 = (
            f"{snap.week_52_low} – {snap.week_52_high}"
            if snap.week_52_low and snap.week_52_high
            else "N/A"
        )

        st.metric(
            "52-Wk Range",
            rng52
        )

    # ─────────────────────────────────────────────
    # 52-Week Position Visualization
    # ─────────────────────────────────────────────

    pos = snap.position_in_range

    if pos is not None:

        # Clamp safely between 0 and 1
        safe_pos = max(
            0.0,
            min(1.0, pos)
        )

        pct_pos = int(
            safe_pos * 100
        )

        st.caption(
            f"52-Week Range Position: {pct_pos}%"
        )

        st.progress(
            safe_pos
        )

        low_col, spacer, high_col = st.columns(
            [1, 2, 1]
        )

        with low_col:

            st.caption(
                f"Low: {snap.week_52_low}"
            )

        with high_col:

            st.caption(
                f"High: {snap.week_52_high}"
            )