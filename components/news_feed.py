"""components/news_feed.py — Streamlit-native news intelligence feed."""

from __future__ import annotations

import streamlit as st

from services.news_service import Article


def render_news_feed(
    articles: list[Article]
) -> None:

    if not articles:

        st.info(
            "No articles loaded. Add NEWS_API_KEY to .env to enable live news."
        )

        return

    # ─────────────────────────────────────────────
    # Filters
    # ─────────────────────────────────────────────

    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:

        sentiment_filter = st.selectbox(
            "Sentiment Filter",
            [
                "All",
                "BULLISH",
                "BEARISH",
                "NEUTRAL"
            ]
        )

    with col2:

        source_filter = st.selectbox(
            "Source Filter",
            [
                "All Sources",
                "Credible Only"
            ]
        )

    with col3:

        show_n = st.selectbox(
            "Articles",
            [10, 20, 30]
        )

    # ─────────────────────────────────────────────
    # Apply Filters
    # ─────────────────────────────────────────────

    filtered = []

    for article in articles:

        sentiment_match = (
            sentiment_filter == "All"
            or article.sentiment == sentiment_filter
        )

        source_match = (
            source_filter == "All Sources"
            or article.is_credible_source
        )

        if sentiment_match and source_match:

            filtered.append(article)

    # ─────────────────────────────────────────────
    # Stats Summary
    # ─────────────────────────────────────────────

    bull = sum(
        1 for a in filtered
        if a.sentiment == "BULLISH"
    )

    bear = sum(
        1 for a in filtered
        if a.sentiment == "BEARISH"
    )

    neut = sum(
        1 for a in filtered
        if a.sentiment == "NEUTRAL"
    )

    stat1, stat2, stat3, stat4 = st.columns(4)

    stat1.metric(
        "Filtered",
        len(filtered)
    )

    stat2.metric(
        "Bullish",
        bull
    )

    stat3.metric(
        "Bearish",
        bear
    )

    stat4.metric(
        "Neutral",
        neut
    )

    st.divider()

    # ─────────────────────────────────────────────
    # Empty State
    # ─────────────────────────────────────────────

    if not filtered:

        st.warning(
            "No articles match current filters."
        )

        return

    # ─────────────────────────────────────────────
    # Article Feed
    # ─────────────────────────────────────────────

    for article in filtered[:show_n]:

        render_article(article)


def render_article(
    article: Article
) -> None:

    relevance_pct = int(
        article.relevance_score * 100
    )

    with st.container(border=True):

        top_left, top_right = st.columns([5, 1])

        with top_left:

            st.markdown(
                f"#### [{article.title}]({article.url})"
            )

        with top_right:

            st.metric(
                "Relevance",
                f"{relevance_pct}%"
            )

        meta1, meta2, meta3 = st.columns(3)

        with meta1:

            st.caption(
                f"Source: {article.source}"
            )

        with meta2:

            st.caption(
                f"Sentiment: {article.sentiment}"
            )

        with meta3:

            st.caption(
                f"{article.age_label}"
            )

        if article.is_credible_source:

            st.success(
                "Credible Source"
            )

        if article.description:

            st.write(
                article.short_description
            )

        st.progress(
            article.relevance_score
        )

        st.divider()