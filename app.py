"""
app.py
───────
PSX Financial Intelligence Workspace
─────────────────────────────────────
Entry point. Run with:  streamlit run app.py

Handles:
  - Page config
  - Global styling (minimal — dark background only)
  - Sidebar navigation and search
  - Session state
  - Routes to: Dashboard | Market Overview | Portfolio
"""

from __future__ import annotations

import streamlit as st

# ── Page config — MUST be the first Streamlit call ───────────────────────────
st.set_page_config(
    page_title="PSX Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports ───────────────────────────────────────────────────────────────────
from config.constants import CHART_PERIODS, SECTOR_MAP
from pages import dashboard, market_overview, portfolio_page

# ── Global dark background (minimal CSS — one rule only) ─────────────────────
st.markdown(
    """
    <style>
    .stApp { background-color: #0a0e1a; }
    section[data-testid="stSidebar"] { background-color: #111827; }
    div[data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #1e293b;
        padding: 12px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:

    st.title("📈 PSX Intelligence")
    st.caption(
        "AI-powered market intelligence\n"
        "for the Pakistan Stock Exchange"
    )

    st.divider()

    # Navigation
    page = st.radio(
        "Navigate",
        ["Dashboard", "Market Overview", "Portfolio"],
        label_visibility="collapsed",
    )

    st.divider()

    # Search — only relevant on Dashboard
    st.subheader("Asset Search")

    search_query = st.text_input(
        "Ticker or company name",
        value=st.session_state.get("last_query", "OGDC"),
        placeholder="e.g. HBL, MEBL, ENGRO",
        label_visibility="collapsed",
    )

    chart_period = st.selectbox(
        "Chart Period",
        CHART_PERIODS,
        index=2,
    )

    analyse_btn = st.button(
        "Run AI Analysis",
        use_container_width=True,
        type="primary",
    )

    st.divider()

    # Quick selects grouped by sector
    st.subheader("Quick Select")

    for sector, tickers in list(SECTOR_MAP.items())[:5]:
        st.caption(sector)
        cols = st.columns(3)
        for idx, ticker in enumerate(tickers[:3]):
            with cols[idx % 3]:
                if st.button(ticker, key=f"qs_{ticker}"):
                    st.session_state["last_query"] = ticker
                    st.rerun()

    st.divider()

    st.caption(
        "Data: yfinance · NewsAPI · OpenAI\n\n"
        "AI engine uses earnings sensitivity maps "
        "to explain WHY stocks move, not just WHAT happened."
    )

# ── Session state ─────────────────────────────────────────────────────────────
if "last_query" not in st.session_state:
    st.session_state["last_query"] = "OGDC"

# Update query on button press or new search
if analyse_btn or search_query != st.session_state["last_query"]:
    st.session_state["last_query"] = search_query

current_query = st.session_state["last_query"]

# ── Page routing ──────────────────────────────────────────────────────────────
try:
    if page == "Dashboard":
        dashboard.render(current_query, chart_period)

    elif page == "Market Overview":
        market_overview.render()

    elif page == "Portfolio":
        portfolio_page.render()

except Exception as e:
    st.error(f"Something went wrong: {e}")
    st.caption("Check your terminal for the full error traceback.")
    raise  # re-raise so terminal shows the full stacktrace

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("PSX Intelligence Workspace")
with col2:
    st.caption("AI-Powered Financial Reasoning Engine")
with col3:
    st.caption("Python · Streamlit · OpenAI · yfinance")