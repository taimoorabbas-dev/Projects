"""
pages/portfolio_page.py
-----------------------
Portfolio tracker with:
  - Live prices via yfinance (.KA suffix for PSX)
  - Unrealised P&L (amount + %)
  - Per-position stop loss & target price
  - Visual progress bar: where is current price between stop and target?
  - Automatic alerts when stop hit or target reached
  - Allocation donut chart
"""

from __future__ import annotations
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

try:
    from config.constants import PSX_TICKERS
except ImportError:
    PSX_TICKERS = {}


# ── Live price fetch ──────────────────────────────────────────────────────────

@st.cache_data(ttl=300)   # cache 5 minutes so we don't hammer yfinance
def _fetch_prices(tickers: tuple[str, ...]) -> dict[str, float | None]:
    """Return {ticker: last_price} for each PSX ticker. Returns None if unavailable."""
    prices: dict[str, float | None] = {}
    for t in tickers:
        try:
            fast = yf.Ticker(f"{t}.KA").fast_info
            p    = float(fast.last_price)
            prices[t] = p if p > 0 else None
        except Exception:
            prices[t] = None
    return prices


# ── Helpers ───────────────────────────────────────────────────────────────────

def _sign(val: float) -> str:
    return f"+{val:,.2f}" if val >= 0 else f"{val:,.2f}"

def _pct(val: float) -> str:
    return f"+{val:.2f}%" if val >= 0 else f"{val:.2f}%"


# ── Main render ───────────────────────────────────────────────────────────────

def render() -> None:
    # Ensure portfolio exists in session state
    if "portfolio" not in st.session_state:
        st.session_state["portfolio"] = [
            {"ticker": "OGDC", "shares": 500,  "avg_cost": 162.50, "stop_loss": 148.0, "target": 185.0},
            {"ticker": "HBL",  "shares": 200,  "avg_cost": 148.75, "stop_loss": 133.0, "target": 168.0},
            {"ticker": "MCB",  "shares": 150,  "avg_cost": 207.00, "stop_loss": 188.0, "target": 232.0},
        ]

    portfolio = st.session_state["portfolio"]

    st.title("Portfolio")
    st.caption(
        "Live prices · Unrealised P&L · Stop loss & target tracking. "
        "Prices refresh every 5 minutes."
    )
    st.divider()

    # ── Add / Update position ─────────────────────────────────────────────────
    with st.expander("➕  Add or update a position"):
        with st.form("add_position_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                new_ticker = st.text_input("Ticker", placeholder="e.g. ENGRO, LUCK")
                new_shares = st.number_input("Shares", min_value=1, value=100, step=1)
            with c2:
                new_cost   = st.number_input("Avg cost (PKR)", min_value=0.01, value=100.0, format="%.2f")
                new_stop   = st.number_input("Stop loss (PKR)", min_value=0.01, value=90.0, format="%.2f")
            with c3:
                new_target = st.number_input("Target price (PKR)", min_value=0.01, value=120.0, format="%.2f")
                st.write("")   # spacer
                add_btn    = st.form_submit_button("Add Position", use_container_width=True, type="primary")

        if add_btn and new_ticker.strip():
            t = new_ticker.strip().upper()
            for pos in portfolio:
                if pos["ticker"] == t:
                    # Weighted average update
                    total         = pos["shares"] + int(new_shares)
                    pos["avg_cost"] = (pos["shares"] * pos["avg_cost"] + int(new_shares) * new_cost) / total
                    pos["shares"]   = total
                    pos["stop_loss"]= float(new_stop)
                    pos["target"]   = float(new_target)
                    st.success(f"{t} position updated.")
                    st.rerun()
                    break
            else:
                portfolio.append({
                    "ticker":    t,
                    "shares":    int(new_shares),
                    "avg_cost":  float(new_cost),
                    "stop_loss": float(new_stop),
                    "target":    float(new_target),
                })
                st.success(f"{t} added to portfolio.")
                st.rerun()

    # ── Fetch live prices ─────────────────────────────────────────────────────
    if portfolio:
        with st.spinner("Fetching live prices…"):
            live = _fetch_prices(tuple(p["ticker"] for p in portfolio))
    else:
        live = {}

    # ── Portfolio totals ──────────────────────────────────────────────────────
    def live_price(pos: dict) -> float:
        """Live price if available, otherwise fall back to avg cost."""
        return live.get(pos["ticker"]) or pos["avg_cost"]

    total_invested = sum(p["shares"] * p["avg_cost"]    for p in portfolio)
    total_current  = sum(p["shares"] * live_price(p)    for p in portfolio)
    total_pnl      = total_current - total_invested
    total_pnl_pct  = (total_pnl / total_invested * 100) if total_invested else 0.0

    # ── Summary metrics ───────────────────────────────────────────────────────
    s1, s2 = st.columns(2)
    s3, s4 = st.columns(2)
    with s1:
        st.metric("Total Invested",  f"PKR {total_invested:,.0f}")
    with s2:
        st.metric("Current Value",   f"PKR {total_current:,.0f}")
    with s3:
        st.metric(
            "Unrealised P&L",
            f"PKR {total_pnl:,.0f}",
            _pct(total_pnl_pct),
            delta_color="normal",
        )
    with s4:
        st.metric("Positions", len(portfolio))

    st.divider()

    # ── Alerts ────────────────────────────────────────────────────────────────
    alerts_shown = False
    for pos in portfolio:
        price = live.get(pos["ticker"])
        if price is None:
            continue
        sl = pos.get("stop_loss", 0)
        tp = pos.get("target", 0)
        t  = pos["ticker"]

        if price <= sl:
            st.error(f"🔴 **{t} — STOP LOSS HIT!**  Price: PKR {price:.2f}  ·  Stop: PKR {sl:.2f}  →  Consider exiting.")
            alerts_shown = True
        elif price >= tp:
            st.success(f"🎯 **{t} — TARGET REACHED!**  Price: PKR {price:.2f}  ·  Target: PKR {tp:.2f}  →  Consider booking profit.")
            alerts_shown = True
        elif sl > 0 and (price - sl) / (sl + 0.01) < 0.05:
            st.warning(f"⚠️ **{t}** approaching stop loss — Price: PKR {price:.2f}  ·  Stop: PKR {sl:.2f}")
            alerts_shown = True

    if alerts_shown:
        st.divider()

    # ── Individual position cards ─────────────────────────────────────────────
    st.markdown("**Holdings**")

    if not portfolio:
        st.info("No positions yet. Add one above.")
        return

    for i, pos in enumerate(portfolio):
        t       = pos["ticker"]
        price   = live_price(pos)
        is_live = live.get(t) is not None

        invested = pos["shares"] * pos["avg_cost"]
        current  = pos["shares"] * price
        pnl      = current - invested
        pnl_pct  = (pnl / invested * 100) if invested else 0.0
        alloc    = (invested / total_invested * 100) if total_invested else 0.0
        name     = PSX_TICKERS.get(t, t)

        sl = pos.get("stop_loss", 0.0)
        tp = pos.get("target",    0.0)

        # Where is current price in the stop→target range?  0 = at stop, 1 = at target
        if tp > sl > 0:
            pos_ratio = max(0.0, min(1.0, (price - sl) / (tp - sl)))
        else:
            pos_ratio = 0.5

        with st.container(border=True):
            # ── Row 1: ticker / name / price metric ──────────────────────────
            r1c1, r1c2, r1c3, r1c4 = st.columns([1, 2.5, 2, 2])

            with r1c1:
                st.markdown(f"**{t}**")
                color = "#22c55e" if pnl_pct >= 0 else "#ef4444"
                arrow = "▲" if pnl_pct >= 0 else "▼"
                st.markdown(f"PKR {price:,.2f}")
                st.markdown(f"<span style='color:{color};font-size:12px'>{arrow} {pnl_pct:+.2f}%</span>", unsafe_allow_html=True)
                if not is_live:
                    st.caption("⚡ cost basis")

            with r1c2:
                st.markdown(f"**{name}**")
                st.caption(f"{pos['shares']:,} shares  ·  Avg cost PKR {pos['avg_cost']:.2f}")
                color = "green" if pnl >= 0 else "red"
                st.markdown(f"P&L: :{color}[PKR {_sign(pnl)}]  :{color}[({_pct(pnl_pct)})]")
                st.caption(f"Allocation: {alloc:.1f}%")

            with r1c3:
                st.markdown("**Stop Loss → Target**")
                st.caption(f"Stop: PKR {sl:.2f}")
                st.progress(pos_ratio)
                st.caption(f"Target: PKR {tp:.2f}")

                # Status badge
                if price <= sl:
                    st.error("STOP LOSS ⚠️")
                elif price >= tp:
                    st.success("TARGET HIT 🎯")
                elif pos_ratio >= 0.75:
                    st.success(f"Near target ({pos_ratio:.0%})")
                elif pos_ratio <= 0.25:
                    st.warning(f"Near stop ({pos_ratio:.0%})")

            with r1c4:
                st.markdown(f"**Invested**")
                st.markdown(f"PKR {invested:,.0f}")
                st.markdown(f"**Current**")
                st.markdown(f"PKR {current:,.0f}")
                if st.button("Analyse →", key=f"port_a_{i}", type="primary", use_container_width=True):
                    st.session_state["ticker"] = t
                    st.session_state["page"]   = "Dashboard"
                    st.rerun()
                if st.button("Remove", key=f"port_r_{i}", use_container_width=True):
                    portfolio.pop(i)
                    st.session_state["portfolio"] = portfolio
                    st.rerun()

    st.divider()

    # ── Allocation donut chart ────────────────────────────────────────────────
    st.markdown("**Portfolio Allocation**")

    labels  = [p["ticker"] for p in portfolio]
    values  = [p["shares"] * p["avg_cost"] for p in portfolio]
    colors  = ["#3b82f6", "#60a5fa", "#93c5fd", "#1d4ed8", "#2563eb", "#1e40af", "#dbeafe"]

    fig = go.Figure(go.Pie(
        labels        = labels,
        values        = values,
        hole          = 0.62,
        marker_colors = colors[:len(portfolio)],
        textinfo      = "label+percent",
        textfont_size = 12,
        hovertemplate = "<b>%{label}</b><br>PKR %{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor = "rgba(0,0,0,0)",
        plot_bgcolor  = "rgba(0,0,0,0)",
        font_color    = "#94a3b8",
        showlegend    = False,
        margin        = dict(t=10, b=10, l=10, r=10),
        height        = 400,
        width         = 700,
    )
    chart_col = st.container()
    with chart_col:
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.caption(
        "* Market value and P&L based on live yfinance prices where available. "
        "Positions showing ⚡ are using cost basis as fallback."
    )
