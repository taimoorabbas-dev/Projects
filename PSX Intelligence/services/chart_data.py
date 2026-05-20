"""
services/chart_data.py
───────────────────────
Plotly figure builders. Dark fintech theme throughout.
"""

from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

BG      = "#080d18"
SURFACE = "#0f1724"
GRID    = "#1a2535"
BORDER  = "#1e2d40"
TEXT    = "#e2e8f0"
DIM     = "#4a6080"
GREEN   = "#00d97e"
RED     = "#ff4d6d"
AMBER   = "#ffb347"
BLUE    = "#4d9fff"
PURPLE  = "#9d7fea"
CYAN    = "#00c8d4"


def _base(title: str = "", height: int = 420) -> dict:
    return dict(
        title=dict(text=title, font=dict(color=TEXT, size=13, family="'JetBrains Mono', monospace")),
        paper_bgcolor=BG, plot_bgcolor=BG,
        font=dict(color=DIM, family="'JetBrains Mono', monospace", size=10),
        xaxis=dict(showgrid=True, gridcolor=GRID, gridwidth=0.4,
                   showline=False, tickfont=dict(color=DIM),
                   rangeslider=dict(visible=False)),
        yaxis=dict(showgrid=True, gridcolor=GRID, gridwidth=0.4,
                   showline=False, tickfont=dict(color=DIM)),
        margin=dict(l=8, r=8, t=40, b=8),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=DIM, size=9)),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=SURFACE, font_size=10,
                        font_family="'JetBrains Mono', monospace"),
        height=height,
    )


def candlestick_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    if df.empty:
        return _empty("No price data — check ticker or network connection")

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.73, 0.27], vertical_spacing=0.02)

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"], name=ticker,
        increasing_line_color=GREEN, decreasing_line_color=RED,
        increasing_fillcolor=GREEN, decreasing_fillcolor=RED,
        line_width=1,
    ), row=1, col=1)

    # Bollinger bands
    if "BB_upper" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_upper"], name="BB Upper",
            line=dict(color=PURPLE, width=0.7, dash="dot"), showlegend=True,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df.index, y=df["BB_lower"], name="BB Lower",
            line=dict(color=PURPLE, width=0.7, dash="dot"),
            fill="tonexty", fillcolor="rgba(157,127,234,0.04)", showlegend=False,
        ), row=1, col=1)

    # Moving averages
    if "MA20" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MA20"], name="MA 20",
            line=dict(color=AMBER, width=1.1),
        ), row=1, col=1)
    if "MA50" in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index, y=df["MA50"], name="MA 50",
            line=dict(color=BLUE, width=1.1),
        ), row=1, col=1)

    # Volume
    colors = [GREEN if c >= o else RED
              for c, o in zip(df["Close"], df["Open"])]
    fig.add_trace(go.Bar(
        x=df.index, y=df["Volume"], name="Volume",
        marker_color=colors, marker_opacity=0.55,
    ), row=2, col=1)

    layout = _base(f"{ticker} — Price & Volume", height=500)
    layout["yaxis2"] = dict(showgrid=True, gridcolor=GRID, gridwidth=0.4,
                             tickfont=dict(color=DIM))
    layout["xaxis2"] = dict(showgrid=True, gridcolor=GRID, gridwidth=0.4,
                             tickfont=dict(color=DIM), rangeslider=dict(visible=False))
    fig.update_layout(**layout)
    return fig


def returns_chart(df: pd.DataFrame, ticker: str) -> go.Figure:
    if df.empty or "DailyReturn" not in df.columns:
        return _empty("No returns data available")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    colors = [GREEN if r >= 0 else RED for r in df["DailyReturn"].fillna(0)]

    fig.add_trace(go.Bar(
        x=df.index, y=df["DailyReturn"], name="Daily Return %",
        marker_color=colors, marker_opacity=0.65,
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=df.index, y=df["CumReturn"], name="Cumulative Return %",
        line=dict(color=CYAN, width=1.3),
    ), secondary_y=True)

    layout = _base(f"{ticker} — Returns Analysis", height=300)
    fig.update_layout(**layout)
    fig.update_yaxes(title_text="Daily %", secondary_y=False, tickfont=dict(color=DIM))
    fig.update_yaxes(title_text="Cumulative %", secondary_y=True, tickfont=dict(color=DIM))
    return fig


def sector_heatmap(data: list[dict]) -> go.Figure:
    valid = [d for d in data if d.get("pct_change") is not None]
    if not valid:
        return _empty("Market data loading…")

    pct_vals = [d["pct_change"] for d in valid]
    text = [f"{d['ticker']}<br>{d['pct_change']:+.2f}%" for d in valid]

    fig = go.Figure(go.Treemap(
        labels=[d["ticker"] for d in valid],
        parents=[d["sector"] for d in valid],
        values=[max(abs(d["pct_change"]), 0.1) for d in valid],
        text=text,
        textinfo="text",
        hovertemplate="<b>%{label}</b><br>%{text}<extra></extra>",
        marker=dict(
            colors=pct_vals,
            colorscale=[[0, RED], [0.5, "#1a2535"], [1, GREEN]],
            cmid=0,
            line=dict(width=1.5, color=BG),
        ),
        textfont=dict(color=TEXT, family="'JetBrains Mono', monospace", size=11),
    ))
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG,
        margin=dict(l=0, r=0, t=0, b=0), height=280,
    )
    return fig


def _empty(msg: str) -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=msg, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color=DIM, size=12),
    )
    fig.update_layout(
        paper_bgcolor=BG, plot_bgcolor=BG, height=300,
        xaxis=dict(visible=False), yaxis=dict(visible=False),
    )
    return fig