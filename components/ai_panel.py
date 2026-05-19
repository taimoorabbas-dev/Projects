"""components/ai_panel.py — Streamlit-native AI analysis panel."""

from __future__ import annotations

import streamlit as st

from services.ai_engine import AIAnalysis
from utils.helpers import (
    category_icon,
    direction_icon,
)


def render_ai_panel(
    analysis: AIAnalysis
) -> None:

    # ─────────────────────────────────────────────
    # Top Summary Metrics
    # ─────────────────────────────────────────────

    stat1, stat2, stat3, stat4 = st.columns(4)

    stat1.metric(
        "AI Confidence",
        analysis.confidence
    )

    stat2.metric(
        "Articles Analysed",
        analysis.articles_analysed
    )

    stat3.metric(
        "Bullish",
        analysis.sentiment_distribution.get(
            "BULLISH",
            0
        )
    )

    stat4.metric(
        "Bearish",
        analysis.sentiment_distribution.get(
            "BEARISH",
            0
        )
    )

    st.caption(
        analysis.confidence_reason
    )

    st.divider()

    # ─────────────────────────────────────────────
    # Noise Warning
    # ─────────────────────────────────────────────

    if analysis.move_is_noise:

        st.warning(
            """
            Today's movement appears within normal market noise range.
            There may not be a single identifiable catalyst.
            """
        )

    # ─────────────────────────────────────────────
    # Primary Cause
    # ─────────────────────────────────────────────

    st.subheader(
        "Primary Cause"
    )

    st.info(
        analysis.primary_cause
    )

    # ─────────────────────────────────────────────
    # Causal Chain
    # ─────────────────────────────────────────────

    if (
        analysis.causal_chain
        and analysis.causal_chain != "N/A"
    ):

        st.subheader(
            "Causal Chain"
        )

        chain_parts = [
            p.strip()
            for p in analysis.causal_chain.split("→")
        ]

        for idx, part in enumerate(chain_parts):

            st.write(
                f"{idx + 1}. {part}"
            )

    # ─────────────────────────────────────────────
    # Explanations
    # ─────────────────────────────────────────────

    tab1, tab2 = st.tabs(
        [
            "Plain English",
            "Technical Analysis"
        ]
    )

    with tab1:

        st.subheader(
            "What Happened?"
        )

        st.write(
            analysis.plain_english
        )

    with tab2:

        st.subheader(
            "Technical Explanation"
        )

        st.write(
            analysis.technical_explanation
        )

        if analysis.technical_context:

            st.caption(
                analysis.technical_context
            )

    st.divider()

    # ─────────────────────────────────────────────
    # Contributing Signals
    # ─────────────────────────────────────────────

    st.subheader(
        "Contributing Signals"
    )

    for signal in analysis.causal_signals:

        with st.container(border=True):

            top1, top2 = st.columns([4, 1])

            with top1:

                st.markdown(
                    f"""
                    ### {category_icon(signal.category)}
                    {direction_icon(signal.direction)}
                    {signal.signal}
                    """
                )

            with top2:

                st.metric(
                    "Weight",
                    f"{int(signal.weight * 100)}%"
                )

            st.caption(
                f"Category: {signal.category}"
            )

            st.write(
                signal.mechanism
            )

            st.info(
                f"Evidence: {signal.evidence}"
            )

            if signal.source:

                st.caption(
                    f"Source: {signal.source}"
                )

            st.progress(
                signal.weight
            )

    # ─────────────────────────────────────────────
    # Risk Flags
    # ─────────────────────────────────────────────

    if analysis.risk_flags:

        st.subheader(
            "Forward Risk Flags"
        )

        for risk in analysis.risk_flags:

            with st.container(border=True):

                top1, top2 = st.columns([2, 1])

                with top1:

                    st.write(
                        f"⚠ {risk.description}"
                    )

                with top2:

                    st.metric(
                        "Severity",
                        risk.severity
                    )

                st.caption(
                    f"Time Horizon: {risk.time_horizon}"
                )