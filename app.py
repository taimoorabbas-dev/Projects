"""
app.py
------
PSX Intelligence — Entry point.
Run with:  streamlit run app.py

Handles:
  - Page config and theme
  - Sidebar (search, quick picks, navigation, period selector)
  - Homepage (hero, search, market snapshot, feature cards)
  - Session state initialisation
  - Routing to the correct page
"""

from __future__ import annotations
import streamlit as st

st.set_page_config(
    page_title="PSX Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""<style>
[data-testid="stSidebar"]{display:none}
[data-testid="collapsedControl"]{display:none}
[data-testid="stToolbar"]{display:none}
header[data-testid="stHeader"]{display:none}
.block-container {
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-top: 0rem !important;
    max-width: 100% !important;
}
.ticker-tape-fixed {
    position: sticky;
    top: 0;
    z-index: 999;
}
</style>""", unsafe_allow_html=True)

from config.constants import ALIAS_MAP, CHART_PERIODS, PSX_TICKERS
from views import dashboard, market_overview, portfolio_page


# ── Default session state ──────────────────────────────────────────────────────
def _init_state() -> None:
    defaults = {
        "page":         "Home",
        "ticker":       "OGDC",
        "chart_period": "6mo",
        "portfolio": [
            {"ticker": "OGDC", "shares": 500,  "avg_cost": 162.50, "stop_loss": 118.0, "target": 185.0},
            {"ticker": "HBL",  "shares": 200,  "avg_cost": 148.75, "stop_loss": 133.0, "target": 168.0},
            {"ticker": "MCB",  "shares": 150,  "avg_cost": 207.00, "stop_loss": 188.0, "target": 232.0},
        ],
        "watchlist": [
            {"ticker": "OGDC",  "target": "185"},
            {"ticker": "HBL",   "target": "168"},
            {"ticker": "ENGRO", "target": "310"},
        ],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _resolve_ticker(query: str) -> str:
    q = (query or "").strip()
    if not q:
        return st.session_state.get("ticker", "OGDC")
    upper = q.upper()
    if upper in PSX_TICKERS:
        return upper
    alias = ALIAS_MAP.get(q.lower())
    return alias if alias else upper


def _go_to_dashboard(ticker: str) -> None:
    st.session_state["ticker"] = _resolve_ticker(ticker)
    st.session_state["page"]   = "Dashboard"
    st.rerun()


# ── Sidebar ────────────────────────────────────────────────────────────────────
def _sidebar() -> None:
    with st.sidebar:
        st.markdown("## 📈 PSX Intelligence")
        st.caption("Pakistan Stock Exchange · AI Platform")
        st.divider()

        # Search
        query = st.text_input(
            "Search",
            placeholder="Ticker or company — OGDC, HBL…",
            label_visibility="collapsed",
        )
        if st.button("Open Workspace", use_container_width=True, type="primary"):
            if query.strip():
                _go_to_dashboard(query.strip())

        # Quick picks — 3 columns so ticker labels don't wrap
        st.caption("Quick picks")
        row1 = st.columns(3)
        row2 = st.columns(2)
        picks = [("OGDC", row1[0]), ("HBL", row1[1]), ("MCB", row1[2]),
                 ("HUBC", row2[0]), ("PSO", row2[1])]
        for t, col in picks:
            with col:
                if st.button(t, key=f"qp_{t}", use_container_width=True):
                    _go_to_dashboard(t)

        st.divider()

        # Chart period
        period = st.selectbox(
            "Chart period",
            CHART_PERIODS,
            index=CHART_PERIODS.index(st.session_state.get("chart_period", "6mo")),
        )
        st.session_state["chart_period"] = period

        st.divider()

        # Navigation
        pages   = ["Home", "Dashboard", "Market Overview", "Portfolio", "Watchlist"]
        current = st.session_state.get("page", "Home")
        idx     = pages.index(current) if current in pages else 0

        selected = st.radio("Navigate", pages, index=idx, label_visibility="collapsed")
        if selected != current:
            st.session_state["page"] = selected
            st.rerun()

        st.divider()
        st.caption("Built with Python · Streamlit · OpenAI · yfinance")


# ── Top ticker tape ───────────────────────────────────────────────────────────
def _render_topbar() -> None:
    tickers = [
        ("KSE-100", "+0.82%", True),
        ("OGDC", "+1.2%", True),
        ("HBL", "+0.7%", True),
        ("MCB", "-0.4%", False),
        ("PSO", "-1.1%", False),
        ("HUBC", "+0.3%", True),
        ("ENGRO", "+2.1%", True),
    ]
    items = []
    for t, pct, up in tickers:
        color = "#22c55e" if up else "#ef4444"
        dot = "●"
        items.append(f"<span style='color:#e2e8f0;font-weight:600'>{t}</span> <span style='color:{color}'>{dot} {pct}</span>")
    tape = "<span style='color:#334155'>  ·  </span>".join(items)
    st.markdown(
        f"<div class='ticker-tape-fixed' style='background:#080d1a;padding:6px 16px;border-bottom:1px solid #1e2a3a;font-size:12px;margin:0'>{tape}</div>",
        unsafe_allow_html=True,
    )


# ── Top navigation bar ────────────────────────────────────────────────────────
def _render_navbar() -> None:
    st.markdown(
        "<div style='background:#0f172a;border-bottom:1px solid #1e2a3a;padding:4px 0 0 0;margin-bottom:0'></div>",
        unsafe_allow_html=True,
    )
    pages = ["Home", "Dashboard", "Market Overview", "Portfolio", "Watchlist"]
    current = st.session_state.get("page", "Home")
    cols = st.columns([1, 1.3, 1.6, 1.1, 1.1, 1, 2.8])
    nav_map = zip(pages, cols[:5])
    for page_name, col in nav_map:
        with col:
            btn_type = "primary" if current == page_name else "secondary"
            if st.button(page_name, key=f"nav_{page_name}", type=btn_type, use_container_width=True):
                st.session_state["page"] = page_name
                st.rerun()
    with cols[5]:
        pass
    with cols[6]:
        search = st.text_input("navsearch", placeholder="🔍  Search — OGDC, HBL, MCB...", label_visibility="collapsed", key="nav_search_input")
        if search and search != st.session_state.get("_last_nav_search", ""):
            st.session_state["_last_nav_search"] = search
            _go_to_dashboard(search)


# ── Homepage ───────────────────────────────────────────────────────────────────
def _render_homepage() -> None:
    st.markdown("<div style='padding:40px 0 8px 0'></div>", unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:11px;color:#3b82f6;letter-spacing:2px;text-transform:uppercase;margin-bottom:4px'>"
        "Pakistan Stock Exchange · AI Platform</p>",
        unsafe_allow_html=True,
    )
    st.markdown("## AI-Powered Pakistan Stock Intelligence")
    st.markdown(
        "<p style='color:#64748b;font-size:15px;margin-bottom:24px'>"
        "Track sentiment, technicals, macro signals, and AI-generated causal analysis "
        "— built for PSX investors.</p>",
        unsafe_allow_html=True,
    )

    _, search_col, _ = st.columns([0.5, 5, 0.5])
    with search_col:
        with st.form("home_search_form"):
            search_query = st.text_input(
                "Search",
                placeholder="Search ticker or company — e.g. OGDC, HBL, Hub Power…",
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button(
                "Open Stock Workspace",
                use_container_width=True,
                type="primary",
            )
        if submitted and search_query.strip():
            _go_to_dashboard(search_query.strip())

        st.caption("Quick picks")
        qp1, qp2, qp3, qp4, qp5, qp6, qp7 = st.columns(7)
        quick = [("OGDC", qp1), ("HBL", qp2), ("MCB", qp3), ("HUBC", qp4),
                 ("PSO", qp5), ("ENGRO", qp6), ("LUCK", qp7)]
        for t, col in quick:
            with col:
                if st.button(t, key=f"home_qp_{t}", use_container_width=True):
                    _go_to_dashboard(t)

    st.markdown("<div style='padding:16px 0'></div>", unsafe_allow_html=True)
    st.markdown(
        "<hr style='border:none;border-top:1px solid #1e2a3a;margin:0'>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='padding:8px 0'></div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("KSE-100", "—", "Live feed pending")
    with m2: st.metric("Top Gainer", "HBL", "+2.4%")
    with m3: st.metric("Top Loser", "PSO", "-1.8%", delta_color="inverse")
    with m4: st.metric("Sentiment", "Neutral", "AI pending")

    st.markdown("<div style='padding:16px 0'></div>", unsafe_allow_html=True)
    st.markdown(
        "<hr style='border:none;border-top:1px solid #1e2a3a;margin:0'>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='padding:8px 0'></div>", unsafe_allow_html=True)

    st.markdown(
        "<p style='font-size:11px;color:#475569;text-transform:uppercase;letter-spacing:1px'>Platform Capabilities</p>",
        unsafe_allow_html=True,
    )

    features = [
        ("🤖", "AI Intelligence", "Causal explanations for stock moves — sector-specific, macro-linked, powered by GPT-4o."),
        ("📊", "Technical Analysis", "Candlestick charts, MA-20/50, Bollinger Bands, and daily returns in one view."),
        ("📰", "News Intelligence", "14-18 parallel queries per ticker. Relevance-scored, sentiment-labelled, deduplicated."),
        ("💼", "Portfolio Tracker", "Live P&L, stop loss alerts, target prices, and allocation chart for your PSX holdings."),
        ("👁", "Watchlist", "Save tickers with price targets. One click opens the full AI workspace."),
        ("🌐", "Market Overview", "Sector heatmaps, breadth stats, macro indicators — SBP rate, PKR/USD, IMF, inflation."),
    ]

    c1, c2, c3 = st.columns(3)
    cols = [c1, c2, c3, c1, c2, c3]
    for (icon, title, text), col in zip(features, cols):
        with col:
            with st.container(border=True):
                st.markdown(f"**{icon} {title}**")
                st.caption(text)

    st.markdown("<div style='padding:16px 0'></div>", unsafe_allow_html=True)
    st.caption("Data from yfinance · News from NewsAPI · Analysis from OpenAI GPT-4o")


# ── Watchlist page ─────────────────────────────────────────────────────────────
def _watchlist_page() -> None:
    st.title("Watchlist")
    st.caption("Saved PSX tickers with price targets. Click Analyse to open the AI workspace.")
    st.divider()

    with st.expander("➕  Add ticker to watchlist"):
        with st.form("add_watchlist_form"):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                new_ticker = st.text_input("Ticker", placeholder="e.g. ENGRO, LUCK")
            with c2:
                target_price = st.text_input("Price Target (PKR)", placeholder="Optional")
            with c3:
                st.write("")
                add_btn = st.form_submit_button("Add", use_container_width=True, type="primary")

        if add_btn and new_ticker.strip():
            wl = st.session_state.get("watchlist", [])
            t  = _resolve_ticker(new_ticker.strip())
            if t not in [w["ticker"] for w in wl]:
                wl.append({"ticker": t, "target": target_price.strip() or "—"})
                st.session_state["watchlist"] = wl
                st.success(f"{t} added to watchlist.")
                st.rerun()
            else:
                st.warning(f"{t} is already in your watchlist.")

    st.divider()

    watchlist = st.session_state.get("watchlist", [])

    if not watchlist:
        st.info("Your watchlist is empty. Add tickers above to start monitoring them.")
        return

    for i, item in enumerate(watchlist):
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1.2, 3, 2, 2])
            with c1:
                st.markdown(f"### {item['ticker']}")
            with c2:
                full_name = PSX_TICKERS.get(item["ticker"], item["ticker"])
                st.markdown(f"**{full_name}**")
            with c3:
                target_display = f"PKR {item['target']}" if item["target"] != "—" else "No target set"
                st.metric("Price Target", target_display)
            with c4:
                b1, b2 = st.columns(2)
                with b1:
                    if st.button("Analyse", key=f"wl_open_{i}", use_container_width=True, type="primary"):
                        _go_to_dashboard(item["ticker"])
                with b2:
                    if st.button("Remove", key=f"wl_rm_{i}", use_container_width=True):
                        watchlist.pop(i)
                        st.session_state["watchlist"] = watchlist
                        st.rerun()

    st.divider()
    st.info("Live price alerts and AI signal notifications are coming in the next phase.", icon="ℹ️")


# ── Main routing ───────────────────────────────────────────────────────────────
_init_state()

page   = st.session_state["page"]
ticker = st.session_state["ticker"]
period = st.session_state["chart_period"]

_render_topbar()
_render_navbar()

if page == "Home":
    _render_homepage()
elif page == "Dashboard":
    dashboard.render(ticker, period)
elif page == "Market Overview":
    market_overview.render()
elif page == "Portfolio":
    portfolio_page.render()
elif page == "Watchlist":
    _watchlist_page()
