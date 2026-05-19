from __future__ import annotations

import streamlit as st
from components.portfolio import render_portfolio


def render() -> None:

    st.title("My Portfolio")
    st.caption(
        "Track your PSX holdings with live prices and P&L. "
        "Your portfolio is saved in this browser session."
    )

    st.info(
        "📌 Add your holdings below. "
        "Live prices are fetched automatically and "
        "unrealised P&L is calculated per position."
    )

    render_portfolio()

    st.divider()

    st.caption(
        "Coming soon: AI portfolio insights — "
        "the AI engine will analyse your specific holdings "
        "and flag which macro events affect YOUR portfolio directly."
    )