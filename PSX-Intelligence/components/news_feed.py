"""components/news_feed.py — News feed with filters (pure Streamlit)."""
from __future__ import annotations
import streamlit as st
from services.news_service import Article


def render_news_feed(articles: list[Article]) -> None:
    if not articles:
        st.info(
            "No articles loaded. Add your `NEWS_API_KEY` to `.env` for real-time news.",
            icon="📰",
        )
        return

    # Filters
    f1, f2, f3 = st.columns([2, 2, 1])
    with f1:
        sentiment_filter = st.selectbox(
            "Sentiment", ["All", "BULLISH", "BEARISH", "NEUTRAL"],
            key="news_sentiment_filter",
        )
    with f2:
        source_filter = st.selectbox(
            "Source", ["All Sources", "Credible Only"],
            key="news_source_filter",
        )
    with f3:
        show_n = st.selectbox("Show", [10, 20, 30], key="news_count")

    filtered = [
        a for a in articles
        if (sentiment_filter == "All" or a.sentiment == sentiment_filter)
        and (source_filter == "All Sources" or a.is_credible_source)
    ]

    # Stats
    s1, s2, s3, s4 = st.columns(4)
    with s1: st.metric("Showing", len(filtered))
    with s2: st.metric("Bullish", sum(1 for a in filtered if a.sentiment == "BULLISH"))
    with s3: st.metric("Bearish", sum(1 for a in filtered if a.sentiment == "BEARISH"))
    with s4: st.metric("Neutral", sum(1 for a in filtered if a.sentiment == "NEUTRAL"))

    if not filtered:
        st.info("No articles match current filters.")
        return

    st.divider()

    sent_color = {"BULLISH": "green", "BEARISH": "red", "NEUTRAL": "gray"}

    for article in filtered[:show_n]:
        s_c      = sent_color.get(article.sentiment, "gray")
        verified = "  :blue[✓ VERIFIED]" if article.is_credible_source else ""

        with st.container(border=True):
            top, rel = st.columns([5, 1])
            with top:
                st.markdown(
                    f":{s_c}[**{article.sentiment}**]{verified}"
                    f"  ·  :gray[{article.source}]"
                    f"  ·  :gray[{article.age_label}]"
                )
            with rel:
                st.progress(float(article.relevance_score),
                            text=f"{article.relevance_score:.0%}")
            st.markdown(f"**[{article.title}]({article.url})**")
            st.caption(article.short_description)
