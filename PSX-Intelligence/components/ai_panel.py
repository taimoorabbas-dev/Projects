"""components/ai_panel.py — AI analysis panel (pure Streamlit)."""
from __future__ import annotations
import streamlit as st
from services.ai_engine import AIAnalysis


def _cat_color(cat: str) -> str:
    return {"MACRO": "blue", "REGULATORY": "violet", "SECTOR": "green",
            "COMPANY": "blue", "SENTIMENT": "orange"}.get(cat, "gray")

def _dir_color(d: str) -> str:
    return {"BULLISH": "green", "BEARISH": "red", "MIXED": "orange"}.get(d, "gray")

def _conf_icon(c: str) -> str:
    return {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(c, "⚪")

def _sev_icon(s: str) -> str:
    return {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(s, "⚪")


def render_ai_panel(analysis: AIAnalysis) -> None:
    # 4 stat metrics
    c1, c2, c3, c4 = st.columns(4)
    bull = analysis.sentiment_distribution.get("BULLISH", 0)
    bear = analysis.sentiment_distribution.get("BEARISH", 0)

    with c1:
        st.metric("Confidence", f"{_conf_icon(analysis.confidence)} {analysis.confidence}")
    with c2:
        st.metric("Articles", analysis.articles_analysed)
    with c3:
        st.metric("Bullish signals", bull)
    with c4:
        st.metric("Bearish signals", bear)

    if analysis.confidence_reason:
        st.caption(analysis.confidence_reason)

    if analysis.move_is_noise:
        st.warning("Move is within normal noise range — no single identifiable catalyst.", icon="⚠️")

    st.divider()

    # Explanation tabs
    plain_tab, tech_tab = st.tabs(["Plain English", "Technical"])
    with plain_tab:
        st.markdown(analysis.plain_english)
    with tech_tab:
        st.markdown(analysis.technical_explanation)
        if analysis.technical_context:
            st.caption(analysis.technical_context)

    st.divider()

    # Primary cause
    st.markdown("**Primary Cause**")
    st.info(analysis.primary_cause, icon="🎯")

    # Causal chain
    chain = (analysis.causal_chain or "").strip()
    if chain and chain != "N/A":
        st.markdown("**Causal Chain**")
        parts = [p.strip() for p in chain.split("→") if p.strip()]
        for i, part in enumerate(parts):
            with st.container(border=True):
                st.markdown(f":gray[**{i + 1}**]   {part}")
            if i < len(parts) - 1:
                st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓")

    # Signals
    if analysis.causal_signals:
        st.divider()
        st.markdown("**Contributing Signals**")
        for sig in analysis.causal_signals:
            with st.container(border=True):
                top, wt = st.columns([4, 1])
                with top:
                    st.markdown(
                        f":{_cat_color(sig.category)}[**{sig.category}**]"
                        f"  :{_dir_color(sig.direction)}[{sig.direction}]"
                    )
                    st.markdown(f"**{sig.signal}**")
                    st.caption(sig.mechanism)
                    if sig.evidence:
                        st.caption(f"*Evidence: {sig.evidence}*")
                with wt:
                    st.metric("Weight", f"{int(sig.weight * 100)}%")
                st.progress(float(sig.weight))

    # Risk flags
    if analysis.risk_flags:
        st.divider()
        st.markdown("**Risk Flags**")
        for flag in analysis.risk_flags:
            msg = f"{_sev_icon(flag.severity)} **{flag.severity}** · *{flag.time_horizon}* — {flag.description}"
            if flag.severity == "HIGH":
                st.error(msg)
            elif flag.severity == "MEDIUM":
                st.warning(msg)
            else:
                st.info(msg)
