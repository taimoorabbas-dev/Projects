"""components/metrics_bar.py — Market metrics row (pure Streamlit)."""
from __future__ import annotations
import streamlit as st
from services.market_data import AssetSnapshot


def _fmt_vol(v) -> str:
    if not v:
        return "—"
    return f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}K"


def _fmt_cap(c) -> str:
    if not c:
        return "—"
    return f"{c/1e9:.1f}B" if c >= 1e9 else f"{c/1e6:.0f}M"


def render_metrics(snap: AssetSnapshot) -> None:
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    day_range = (
        f"{snap.day_low:,.2f} – {snap.day_high:,.2f}"
        if snap.day_low and snap.day_high else "N/A"
    )
    wk52_range = (
        f"{snap.week_52_low:,.2f} – {snap.week_52_high:,.2f}"
        if snap.week_52_low and snap.week_52_high else "N/A"
    )

    with c1: st.metric("Prev Close",  f"{snap.prev_close:,.2f}" if snap.prev_close else "—")
    with c2: st.metric("Day Range",   day_range)
    with c3: st.metric("Volume",      _fmt_vol(snap.volume))
    with c4: st.metric("Market Cap",  _fmt_cap(snap.market_cap))
    with c5: st.metric("P/E Ratio",   f"{snap.pe_ratio:.1f}×" if snap.pe_ratio else "N/A")
    with c6: st.metric("52-Wk Range", wk52_range)

    # 52-week position progress bar
    pos = snap.position_in_range
    if pos is not None:
        safe_pos = max(0.0, min(1.0, pos))
        lo = f"{snap.week_52_low:,.2f}"  if snap.week_52_low  else "—"
        hi = f"{snap.week_52_high:,.2f}" if snap.week_52_high else "—"
        st.progress(safe_pos, text=f"52-week position: {safe_pos:.0%}  ({lo} → {hi})")
