"""
components/portfolio.py
────────────────────────
Portfolio tracker — pure Streamlit.

Current state: manual entry portfolio tracker.
Tracks: holdings, average cost, current value, P&L, weight.

Future state (when you build your broker integration):
  - Replace manual entries with live broker API feed
  - Add auto trade open/close signals from AI engine
  - Add real-time P&L updates via WebSocket

Usage:
    from components.portfolio import render_portfolio
    render_portfolio()
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
from services.market_data import fetch_asset_snapshot
from utils.helpers import fmt_price, fmt_pct, pct_color


# ─── Session state key for portfolio holdings ─────────────────────────────────
_KEY = "portfolio_holdings"


def _init_state() -> None:
    """Initialise portfolio in session state if not present."""
    if _KEY not in st.session_state:
        # Pre-loaded with two demo positions so the UI isn't empty on first load
        st.session_state[_KEY] = [
            {
                "ticker":    "OGDC",
                "shares":    500,
                "avg_cost":  158.00,
                "notes":     "Energy sector core position",
            },
            {
                "ticker":    "HBL",
                "shares":    300,
                "avg_cost":  142.50,
                "notes":     "Banking exposure",
            },
        ]


def render_portfolio() -> None:
    """Main portfolio component. Call this from any page."""

    _init_state()
    holdings = st.session_state[_KEY]

    st.subheader("Portfolio Tracker")
    st.caption(
        "Track your PSX holdings. "
        "Live prices fetched from yfinance. "
        "Your data stays in this browser session."
    )

    # ── Add position form ─────────────────────────────────────────────
    with st.expander("➕ Add New Position", expanded=False):
        _render_add_form()

    st.divider()

    # ── Portfolio table ───────────────────────────────────────────────
    if not holdings:
        st.info(
            "No positions yet. "
            "Use the form above to add your first holding."
        )
        return

    _render_portfolio_table(holdings)

    st.divider()

    # ── Remove position ───────────────────────────────────────────────
    with st.expander("🗑 Remove a Position", expanded=False):
        _render_remove_form(holdings)


def _render_add_form() -> None:
    """Form to add a new portfolio position."""

    with st.form("add_position_form", clear_on_submit=True):

        col1, col2, col3 = st.columns(3)

        with col1:
            ticker = st.text_input(
                "Ticker",
                placeholder="e.g. MEBL",
            ).upper().strip()

        with col2:
            shares = st.number_input(
                "Number of Shares",
                min_value=1,
                step=1,
                value=100,
            )

        with col3:
            avg_cost = st.number_input(
                "Average Cost (PKR)",
                min_value=0.01,
                step=0.01,
                format="%.2f",
                value=100.00,
            )

        notes = st.text_input(
            "Notes (optional)",
            placeholder="e.g. Long-term hold, sector hedge…",
        )

        submitted = st.form_submit_button(
            "Add Position",
            use_container_width=True,
        )

        if submitted:
            if not ticker:
                st.error("Please enter a ticker symbol.")
            else:
                # Check if ticker already exists — update instead
                existing = [
                    h for h in st.session_state[_KEY]
                    if h["ticker"] == ticker
                ]
                if existing:
                    st.warning(
                        f"{ticker} already in portfolio. "
                        "Remove it first, then re-add to update."
                    )
                else:
                    st.session_state[_KEY].append({
                        "ticker":   ticker,
                        "shares":   int(shares),
                        "avg_cost": float(avg_cost),
                        "notes":    notes,
                    })
                    st.success(f"Added {ticker} — {int(shares)} shares @ PKR {avg_cost:.2f}")
                    st.rerun()


def _render_portfolio_table(holdings: list[dict]) -> None:
    """Fetch live prices and display full portfolio summary."""

    rows   = []
    errors = []

    for h in holdings:
        snap = fetch_asset_snapshot(h["ticker"])

        if not snap.is_valid:
            errors.append(h["ticker"])
            current_price = h["avg_cost"]   # fallback to cost
            pct_chg = 0.0
        else:
            current_price = snap.current_price or h["avg_cost"]
            pct_chg = snap.pct_change or 0.0

        cost_basis    = h["avg_cost"] * h["shares"]
        current_value = current_price * h["shares"]
        unrealised_pl = current_value - cost_basis
        unrealised_pct = (unrealised_pl / cost_basis * 100) if cost_basis else 0

        rows.append({
            "Ticker":       h["ticker"],
            "Shares":       h["shares"],
            "Avg Cost":     h["avg_cost"],
            "Live Price":   round(current_price, 2),
            "Today %":      round(pct_chg, 2),
            "Cost Basis":   round(cost_basis, 2),
            "Mkt Value":    round(current_value, 2),
            "Unrealised P&L": round(unrealised_pl, 2),
            "Return %":     round(unrealised_pct, 2),
            "Notes":        h.get("notes", ""),
        })

    if errors:
        st.warning(
            f"Could not fetch live prices for: {', '.join(errors)}. "
            "Using cost price as fallback."
        )

    df = pd.DataFrame(rows)

    # ── Portfolio summary metrics ─────────────────────────────────────
    total_cost    = df["Cost Basis"].sum()
    total_value   = df["Mkt Value"].sum()
    total_pl      = total_value - total_cost
    total_return  = (total_pl / total_cost * 100) if total_cost else 0

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Invested", f"PKR {total_cost:,.0f}")
    with m2:
        st.metric("Current Value",  f"PKR {total_value:,.0f}")
    with m3:
        st.metric(
            "Unrealised P&L",
            f"PKR {total_pl:+,.0f}",
            delta=f"{total_return:+.2f}%",
        )
    with m4:
        # Count of positions up vs down today
        up   = sum(1 for r in rows if r["Today %"] > 0)
        down = sum(1 for r in rows if r["Today %"] < 0)
        st.metric("Today", f"🟢 {up} up  🔴 {down} down")

    st.divider()

    # ── Per-position weight column ────────────────────────────────────
    df["Weight %"] = (
        (df["Mkt Value"] / total_value * 100).round(1)
        if total_value > 0
        else 0
    )

    # ── Display table ─────────────────────────────────────────────────
    st.dataframe(
        df[[
            "Ticker", "Shares", "Avg Cost", "Live Price",
            "Today %", "Mkt Value", "Unrealised P&L", "Return %", "Weight %", "Notes"
        ]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Today %": st.column_config.NumberColumn(
                "Today %",
                format="%.2f%%",
            ),
            "Return %": st.column_config.NumberColumn(
                "Return %",
                format="%.2f%%",
            ),
            "Unrealised P&L": st.column_config.NumberColumn(
                "Unrealised P&L",
                format="PKR %.2f",
            ),
            "Mkt Value": st.column_config.NumberColumn(
                "Mkt Value",
                format="PKR %.2f",
            ),
            "Avg Cost": st.column_config.NumberColumn(
                "Avg Cost",
                format="PKR %.2f",
            ),
            "Live Price": st.column_config.NumberColumn(
                "Live Price",
                format="PKR %.2f",
            ),
            "Weight %": st.column_config.ProgressColumn(
                "Weight %",
                min_value=0,
                max_value=100,
                format="%.1f%%",
            ),
        },
    )

    st.caption(
        "💡 Live prices are from yfinance (15-20 min delay). "
        "P&L is unrealised — based on average cost vs current price."
    )


def _render_remove_form(holdings: list[dict]) -> None:
    """Form to remove a position from the portfolio."""

    tickers = [h["ticker"] for h in holdings]

    with st.form("remove_form"):
        to_remove = st.selectbox(
            "Select position to remove",
            tickers,
        )
        confirm = st.form_submit_button(
            "Remove Position",
            use_container_width=True,
        )
        if confirm:
            st.session_state[_KEY] = [
                h for h in st.session_state[_KEY]
                if h["ticker"] != to_remove
            ]
            st.success(f"Removed {to_remove} from portfolio.")
            st.rerun()