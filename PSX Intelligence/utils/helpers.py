"""utils/helpers.py — Pure formatting utilities. No business logic."""
from __future__ import annotations
from typing import Optional


def fmt_price(price: Optional[float], currency: str = "PKR") -> str:
    if price is None: return "N/A"
    return f"{currency} {price:,.2f}"

def fmt_pct(pct: Optional[float]) -> str:
    if pct is None: return "N/A"
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.2f}%"

def fmt_volume(vol: Optional[int]) -> str:
    if vol is None: return "N/A"
    if vol >= 1_000_000: return f"{vol/1_000_000:.2f}M"
    if vol >= 1_000: return f"{vol/1_000:.1f}K"
    return f"{vol:,}"

def fmt_market_cap(mc: Optional[float]) -> str:
    if mc is None: return "N/A"
    if mc >= 1_000_000_000: return f"PKR {mc/1_000_000_000:.2f}B"
    if mc >= 1_000_000: return f"PKR {mc/1_000_000:.2f}M"
    return f"PKR {mc:,.0f}"

def fmt_pe(pe: Optional[float]) -> str:
    if pe is None: return "N/A"
    return f"{pe:.1f}x"

def fmt_yield(y: Optional[float]) -> str:
    if y is None: return "N/A"
    return f"{y*100:.2f}%"

def pct_color(pct: Optional[float]) -> str:
    if pct is None: return "#4a6080"
    return "#00d97e" if pct >= 0 else "#ff4d6d"

def confidence_color(c: str) -> str:
    return {"HIGH": "#00d97e", "MEDIUM": "#ffb347", "LOW": "#ff4d6d"}.get(c, "#4a6080")

def severity_color(s: str) -> str:
    return {"HIGH": "#ff4d6d", "MEDIUM": "#ffb347", "LOW": "#4d9fff"}.get(s, "#4a6080")

def category_icon(cat: str) -> str:
    return {"MACRO": "🌐", "REGULATORY": "⚖️", "SECTOR": "🏭",
            "COMPANY": "🏢", "SENTIMENT": "📊"}.get(cat, "📌")

def direction_icon(d: str) -> str:
    return {"BULLISH": "▲", "BEARISH": "▼", "MIXED": "◆"}.get(d, "─")

def direction_color(d: str) -> str:
    return {"BULLISH": "#00d97e", "BEARISH": "#ff4d6d",
            "MIXED": "#ffb347", "NEUTRAL": "#4a6080"}.get(d, "#4a6080")

def sentiment_color(s: str) -> str:
    return {"BULLISH": "#00d97e", "BEARISH": "#ff4d6d",
            "NEUTRAL": "#4a6080"}.get(s, "#4a6080")

def sentiment_badge_class(s: str) -> str:
    return {"BULLISH": "badge-bull", "BEARISH": "badge-bear",
            "NEUTRAL": "badge-neut"}.get(s, "badge-neut")