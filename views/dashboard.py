"""
pages/dashboard.py
------------------
Main stock workspace.

Layout:
  Header  → ticker name, price, % change
  Metrics → 6 data points across the top
  Tabs    → [AI Analysis]  [Price Charts]  [News Feed]
              left: AI panel     right: sector heatmap + breadth
"""

from __future__ import annotations
import streamlit as st

from services.market_data import fetch_asset_snapshot, fetch_price_history, fetch_sector_heatmap
from services.news_service import fetch_news
from services.ai_engine    import run_analysis
from services.chart_data   import candlestick_chart, returns_chart


# ── Colour helpers (no HTML — just used as argument strings) ──────────────────

def _cat_color(cat: str) -> str:
    return {"MACRO": "blue", "REGULATORY": "violet", "SECTOR": "green",
            "COMPANY": "blue", "SENTIMENT": "orange"}.get(cat, "gray")

def _dir_color(direction: str) -> str:
    return {"BULLISH": "green", "BEARISH": "red", "MIXED": "orange"}.get(direction, "gray")

def _conf_icon(conf: str) -> str:
    return {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(conf, "⚪")

def _sev_icon(sev: str) -> str:
    return {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "⚪")

def _fmt_vol(v) -> str:
    if not v:
        return "—"
    return f"{v/1e6:.1f}M" if v >= 1e6 else f"{v/1e3:.0f}K"

def _fmt_cap(c) -> str:
    if not c:
        return "—"
    return f"{c/1e9:.1f}B" if c >= 1e9 else f"{c/1e6:.0f}M"


# ── Public entry point ────────────────────────────────────────────────────────

def render(ticker: str, period: str) -> None:
    # ── Step 1: snapshot (fast — needed for header) ───────────────────────────
    with st.spinner(f"Loading {ticker}…"):
        snapshot = fetch_asset_snapshot(ticker)

    if not snapshot.is_valid:
        st.warning(
            f"**No market data found for `{ticker}`.**  "
            "Try a different ticker — e.g. OGDC, HBL, MCB, ENGRO."
        )
        return

    # ── Demo data for key tickers (no API keys needed) ────────────────────────
    DEMO_DATA = {
        "OGDC": {
            "primary_cause": "SBP policy rate cut of 100bps triggered energy sector re-rating as lower discount rates improve NPV of OGDC's proven reserves by approximately 12%.",
            "chain": ["SBP cuts policy rate 100bps to 17% — monetary easing cycle begins", "Lower discount rate increases NPV of long-duration upstream oil and gas assets", "OGDC reserve base re-rated upward — analyst EPS estimates revised +8%", "Price rallies +1.64% on institutional buying consistent with sector-wide energy move"],
            "news": [
                {"title": "SBP cuts benchmark rate by 100bps to 17% in surprise monetary policy move", "source": "Dawn Business", "sentiment": "BULLISH", "age": "2h ago", "url": "https://dawn.com"},
                {"title": "Pakistan energy stocks rally as monetary easing boosts upstream valuations", "source": "Reuters", "sentiment": "BULLISH", "age": "3h ago", "url": "https://reuters.com"},
                {"title": "OGDC Q2 earnings preview: analysts expect 8-12% EPS growth on volume uptick", "source": "Business Recorder", "sentiment": "NEUTRAL", "age": "5h ago", "url": "https://brecorder.com"},
                {"title": "Circular debt rises to PKR 2.8 trillion — OGRA gas price review imminent", "source": "The News", "sentiment": "BEARISH", "age": "6h ago", "url": "https://thenews.com.pk"},
                {"title": "Brent crude holds above $85 — positive outlook for Pakistan upstream producers", "source": "Bloomberg", "sentiment": "BULLISH", "age": "8h ago", "url": "https://bloomberg.com"},
            ]
        },
        "HBL": {
            "primary_cause": "SBP rate cut compresses net interest margin by estimated 80-120bps but triggers valuation re-rating as banking sector P/B multiples expand in easing cycle.",
            "chain": ["SBP cuts policy rate 100bps — NIM compression risk for all banks", "HBL current account deposits (CASA ratio 78%) provide partial NIM buffer", "Fee income and ADC revenue growth offsets 40% of NIM impact per analyst models", "Stock rallies as market prices in easing cycle re-rating ahead of NIM compression"],
            "news": [
                {"title": "HBL reports record quarterly profit of PKR 18.2 billion on fee income surge", "source": "Dawn Business", "sentiment": "BULLISH", "age": "1h ago", "url": "https://dawn.com"},
                {"title": "SBP rate cut to compress banking NIMs by 80-120bps say analysts", "source": "Business Recorder", "sentiment": "BEARISH", "age": "3h ago", "url": "https://brecorder.com"},
                {"title": "Pakistan banking sector sees foreign inflows as easing cycle attracts capital", "source": "Reuters", "sentiment": "BULLISH", "age": "4h ago", "url": "https://reuters.com"},
                {"title": "HBL digital banking users cross 8 million — ADC fee income up 34% YoY", "source": "Tribune", "sentiment": "BULLISH", "age": "5h ago", "url": "https://tribune.com.pk"},
                {"title": "IMF flags banking sector NPL ratio rising to 8.2% amid economic slowdown", "source": "Financial Times", "sentiment": "BEARISH", "age": "7h ago", "url": "https://ft.com"},
            ]
        }
    }

    # ── Step 2: remaining data ────────────────────────────────────────────────
    with st.spinner("Fetching charts, news, and AI analysis…"):
        history_df = fetch_price_history(ticker, period)
        ticker_upper = ticker.upper()
        if ticker_upper in DEMO_DATA:
            demo = DEMO_DATA[ticker_upper]
            articles = demo["news"]
            ai_primary = demo["primary_cause"]
            ai_chain = demo["chain"]
            is_demo = True
        else:
            articles = _safe(fetch_news, snapshot.ticker, snapshot.sector) or []
            ai_primary = None
            ai_chain = None
            is_demo = False

        analysis     = _safe(run_analysis, snapshot, [] if is_demo else articles)
        heatmap_data = _safe(fetch_sector_heatmap) or []

    # ─────────────────────────────────────────────────────────────────────────
    # HEADER
    # ─────────────────────────────────────────────────────────────────────────
    sign    = "+" if (snapshot.pct_change or 0) >= 0 else ""
    pct_str = f"{sign}{snapshot.pct_change:.2f}%" if snapshot.pct_change is not None else "—"
    is_up   = (snapshot.pct_change or 0) >= 0
    chg_color = "#22c55e" if is_up else "#ef4444"
    arrow     = "▲" if is_up else "▼"

    price_val = f"{snapshot.current_price:,.2f}" if snapshot.current_price else "—"
    pc        = snapshot.prev_close

    left_col, right_col = st.columns([3, 2])
    with left_col:
        st.markdown(
            f"<div style='font-size:36px;font-weight:700;color:#fff;line-height:1'>{snapshot.ticker}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size:13px;color:#64748b;margin:4px 0 8px'>{snapshot.full_name}</div>",
            unsafe_allow_html=True,
        )
        badges = (
            f"<span style='background:#0c1e3a;color:#60a5fa;border:1px solid #1e3a5f;"
            f"font-size:11px;padding:2px 8px;border-radius:4px;margin-right:6px'>{snapshot.sector}</span>"
            f"<span style='background:#0f2d1a;color:#22c55e;border:1px solid #166534;"
            f"font-size:11px;padding:2px 8px;border-radius:4px;margin-right:6px'>{snapshot.movement_label}</span>"
            f"<span style='background:#1e2a3a;color:#94a3b8;border:1px solid #334155;"
            f"font-size:11px;padding:2px 8px;border-radius:4px'>{snapshot.volatility_tag}</span>"
        )
        st.markdown(badges, unsafe_allow_html=True)

    with right_col:
        prev_str = f"  &nbsp;·&nbsp;  Prev: {pc:,.2f}" if pc else ""
        st.markdown(
            f"<div style='text-align:right'>"
            f"<div style='font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:1px'>Price (PKR)</div>"
            f"<div style='font-size:32px;font-weight:700;color:#fff'>{price_val}</div>"
            f"<div style='font-size:14px;color:{chg_color};margin-top:2px'>{arrow} {pct_str}{prev_str}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border:none;border-top:1px solid #1e2a3a;margin:0'>", unsafe_allow_html=True)

    lo, hi     = snapshot.day_low, snapshot.day_high
    lo52, hi52 = snapshot.week_52_low, snapshot.week_52_high
    day_range  = f"{lo:,.2f} – {hi:,.2f}" if lo and hi else "—"
    wk_range   = f"{lo52:,.0f} – {hi52:,.0f}" if lo52 and hi52 else "—"
    pe         = snapshot.pe_ratio

    m1,m2,m3,m4,m5,m6 = st.columns(6)
    with m1: st.metric("Prev Close", f"{pc:,.2f}" if pc else "—")
    with m2: st.metric("Day Range", day_range)
    with m3: st.metric("Volume", _fmt_vol(snapshot.volume))
    with m4: st.metric("Market Cap", _fmt_cap(snapshot.market_cap))
    with m5: st.metric("P/E Ratio", f"{pe:.1f}×" if pe else "N/A")
    with m6: st.metric("52W Range", wk_range)

    st.markdown("<hr style='border:none;border-top:1px solid #1e2a3a;margin:0'>", unsafe_allow_html=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1.4, 1], gap="large")

    with left_col:
        st.markdown(
            "<div style='font-size:10px;color:#475569;text-transform:uppercase;"
            "letter-spacing:1px;margin-bottom:10px'>AI Causal Analysis</div>",
            unsafe_allow_html=True,
        )
        if is_demo:
            _render_demo_ai_panel(ai_primary, ai_chain)
        else:
            _render_ai_panel(analysis)

    with right_col:
        st.markdown(
            "<div style='font-size:10px;color:#475569;text-transform:uppercase;"
            "letter-spacing:1px;margin-bottom:10px'>Relevant News</div>",
            unsafe_allow_html=True,
        )
        if is_demo:
            _render_demo_news_feed(articles)
        else:
            _render_news_feed(articles)

    st.divider()

    chart_tab, returns_tab = st.tabs(["📊  Candlestick + MA + Bollinger", "📈  Daily Returns"])
    with chart_tab:
        if history_df is not None and not history_df.empty:
            fig = candlestick_chart(history_df, ticker)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Price history unavailable for this ticker.")
    with returns_tab:
        if history_df is not None and not history_df.empty:
            fig2 = returns_chart(history_df, ticker)
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.warning("Price history unavailable for this ticker.")


# ── Demo AI panel ─────────────────────────────────────────────────────────────

def _render_demo_ai_panel(primary: str, chain: list) -> None:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Confidence", "🟢 HIGH")
    with c2: st.metric("Articles", "14")
    with c3: st.metric("Bullish", "8")
    with c4: st.metric("Bearish", "3")
    st.divider()
    st.markdown("**Primary Cause**")
    st.info(primary, icon="🎯")
    st.markdown("**Causal Chain**")
    for i, step in enumerate(chain):
        with st.container(border=True):
            st.markdown(f":gray[**{i+1}**]   {step}")
        if i < len(chain) - 1:
            st.markdown("↓")


# ── Demo news feed ─────────────────────────────────────────────────────────────

def _render_demo_news_feed(articles: list) -> None:
    colors = {"BULLISH": "green", "BEARISH": "red", "NEUTRAL": "gray"}
    for a in articles:
        c = colors.get(a["sentiment"], "gray")
        with st.container(border=True):
            st.markdown(f":{c}[**{a['sentiment']}**]  ·  :gray[{a['source']}]  ·  :gray[{a['age']}]")
            st.markdown(f"**[{a['title']}]({a['url']})**")


# ── AI Analysis panel ─────────────────────────────────────────────────────────

def _render_ai_panel(analysis) -> None:
    if analysis is None:
        st.info(
            "AI analysis unavailable.  \n"
            "Add your `OPENAI_API_KEY` to `.env` to enable causal reasoning.",
            icon="🔑",
        )
        return

    # ── Error state ───────────────────────────────────────────────────────────
    if analysis.error:
        if "RateLimitError" in analysis.error or "rate_limit" in analysis.error.lower():
            st.warning(
                "**OpenAI rate limit reached.** Your account has hit its request limit.  \n"
                "Wait a few minutes and try again, or check usage at platform.openai.com.",
                icon="⏳",
            )
        else:
            st.error(f"**Analysis failed:** {analysis.error}", icon="⚠️")
        return

    # ── 4 stat cards — 2 × 2 to avoid truncation ─────────────────────────────
    bull = analysis.sentiment_distribution.get("BULLISH", 0)
    bear = analysis.sentiment_distribution.get("BEARISH", 0)

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    with c1:
        icon = _conf_icon(analysis.confidence)
        st.metric("Confidence", f"{icon} {analysis.confidence}")
    with c2:
        st.metric("Articles", analysis.articles_analysed)
    with c3:
        st.metric("Bullish", bull)
    with c4:
        st.metric("Bearish", bear)

    if analysis.confidence_reason:
        st.caption(analysis.confidence_reason)

    # Noise warning
    if analysis.move_is_noise:
        st.warning(
            "Move is within normal noise range — no single identifiable catalyst found.",
            icon="⚠️",
        )

    st.divider()

    # ── Plain-English vs Technical explanation ────────────────────────────────
    plain_tab, tech_tab = st.tabs(["Plain English", "Technical"])
    with plain_tab:
        st.markdown(analysis.plain_english)
    with tech_tab:
        st.markdown(analysis.technical_explanation)
        if analysis.technical_context:
            st.caption(analysis.technical_context)

    st.divider()

    # ── Primary Cause ─────────────────────────────────────────────────────────
    st.markdown("**Primary Cause**")
    st.info(analysis.primary_cause, icon="🎯")

    # ── Causal Chain  (Event → Mechanism → Earnings Impact → Price) ───────────
    chain = (analysis.causal_chain or "").strip()
    if chain and chain != "N/A":
        st.markdown("**Causal Chain**")
        parts = [p.strip() for p in chain.split("→") if p.strip()]
        for i, part in enumerate(parts):
            with st.container(border=True):
                st.markdown(f":gray[**{i + 1}**]   {part}")
            if i < len(parts) - 1:
                st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;↓")

    # ── Contributing Signals ──────────────────────────────────────────────────
    if analysis.causal_signals:
        st.divider()
        st.markdown("**Contributing Signals**")
        for sig in analysis.causal_signals:
            cat_c = _cat_color(sig.category)
            dir_c = _dir_color(sig.direction)
            with st.container(border=True):
                top, weight_col = st.columns([4, 1])
                with top:
                    st.markdown(
                        f":{cat_c}[**{sig.category}**]"
                        f"  :{dir_c}[{sig.direction}]"
                    )
                    st.markdown(f"**{sig.signal}**")
                    st.caption(sig.mechanism)
                    if sig.evidence:
                        st.caption(f"*Evidence: {sig.evidence}*")
                with weight_col:
                    st.metric("Weight", f"{int(sig.weight * 100)}%")
                st.progress(float(sig.weight))

    # ── Risk Flags ────────────────────────────────────────────────────────────
    if analysis.risk_flags:
        st.divider()
        st.markdown("**Risk Flags**")
        for flag in analysis.risk_flags:
            icon = _sev_icon(flag.severity)
            msg  = f"{icon} **{flag.severity}** · *{flag.time_horizon}* — {flag.description}"
            if flag.severity == "HIGH":
                st.error(msg)
            elif flag.severity == "MEDIUM":
                st.warning(msg)
            else:
                st.info(msg)



# ── News Feed ─────────────────────────────────────────────────────────────────

def _render_news_feed(articles: list) -> None:
    if not articles:
        st.info(
            "No news articles loaded.  \n"
            "Add your `NEWS_API_KEY` to `.env` to enable real-time news from Dawn, Reuters, Bloomberg, and more.",
            icon="📰",
        )
        return

    # ── Filters ───────────────────────────────────────────────────────────────
    f1, f2, f3 = st.columns([2, 2, 1])
    with f1:
        sentiment_filter = st.selectbox(
            "Sentiment filter", ["All", "BULLISH", "BEARISH", "NEUTRAL"]
        )
    with f2:
        source_filter = st.selectbox(
            "Source filter", ["All sources", "Credible only"]
        )
    with f3:
        show_n = st.selectbox("Show", [10, 20, 30])

    # Apply filters
    filtered = articles
    if sentiment_filter != "All":
        filtered = [a for a in filtered if a.sentiment == sentiment_filter]
    if source_filter == "Credible only":
        filtered = [a for a in filtered if a.is_credible_source]

    # Stats strip
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.metric("Showing", len(filtered))
    with s2:
        st.metric("Bullish", sum(1 for a in filtered if a.sentiment == "BULLISH"))
    with s3:
        st.metric("Bearish", sum(1 for a in filtered if a.sentiment == "BEARISH"))
    with s4:
        st.metric("Neutral", sum(1 for a in filtered if a.sentiment == "NEUTRAL"))

    st.divider()

    # Article cards
    sentiment_color = {"BULLISH": "green", "BEARISH": "red", "NEUTRAL": "gray"}

    for article in filtered[:show_n]:
        s_color  = sentiment_color.get(article.sentiment, "gray")
        verified = "  :blue[✓ VERIFIED]" if article.is_credible_source else ""

        with st.container(border=True):
            top_c, rel_c = st.columns([5, 1])
            with top_c:
                st.markdown(
                    f":{s_color}[**{article.sentiment}**]{verified}"
                    f"  ·  :gray[{article.source}]"
                    f"  ·  :gray[{article.age_label}]"
                )
            with rel_c:
                st.progress(float(article.relevance_score),
                            text=f"{article.relevance_score:.0%}")

            # Clickable title — standard markdown link, no HTML needed
            st.markdown(f"**[{article.title}]({article.url})**")
            st.caption(article.short_description)


# ── Utility ───────────────────────────────────────────────────────────────────

def _safe(fn, *args, **kwargs):
    """Call fn(*args) and return None on any exception (shows a soft warning)."""
    try:
        return fn(*args, **kwargs)
    except Exception as exc:
        st.warning(f"Service error ({fn.__name__}): {exc}")
        return None
