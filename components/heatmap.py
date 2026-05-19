"""components/heatmap.py — KSE-100 sector heatmap."""

from __future__ import annotations

import streamlit as st

from services import chart_data


def render_heatmap(
    heatmap_data: list[dict]
) -> None:

    fig = chart_data.sector_heatmap(
        heatmap_data
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )

    # ─────────────────────────────────────────────
    # Market Breadth Summary
    # ─────────────────────────────────────────────

    valid = [
        d for d in heatmap_data
        if d.get("pct_change") is not None
    ]

    if valid:

        gainers = sum(
            1 for d in valid
            if (d["pct_change"] or 0) > 0
        )

        losers = sum(
            1 for d in valid
            if (d["pct_change"] or 0) < 0
        )

        flat = len(valid) - gainers - losers

        avg_chg = (
            sum(d["pct_change"] or 0 for d in valid)
            / len(valid)
        )

        best = max(
            valid,
            key=lambda d: d["pct_change"] or -99
        )

        worst = min(
            valid,
            key=lambda d: d["pct_change"] or 99
        )

        c1, c2, c3, c4, c5, c6 = st.columns(6)

        with c1:

            st.metric(
                "Advancing",
                gainers
            )

        with c2:

            st.metric(
                "Declining",
                losers
            )

        with c3:

            st.metric(
                "Flat",
                flat
            )

        with c4:

            st.metric(
                "Avg Move",
                f"{avg_chg:+.2f}%"
            )

        with c5:

            st.metric(
                "Best Sector",
                f"{best['ticker']} {best['pct_change']:+.1f}%"
            )

        with c6:

            st.metric(
                "Worst Sector",
                f"{worst['ticker']} {worst['pct_change']:+.1f}%"
            )