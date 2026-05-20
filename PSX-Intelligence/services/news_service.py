"""
services/news_service.py
─────────────────────────
Multi-query parallel news aggregation for PSX Intelligence.

Pipeline:
  1. Build 14-18 targeted queries (asset + sector + Pakistan macro)
  2. Fetch all queries in parallel via ThreadPoolExecutor
  3. Deduplicate by Jaccard token similarity
  4. Score relevance 0-1 per article (ticker + name + sector keywords)
  5. Label sentiment (domain-tuned PSX vocabulary)
  6. Rank and return top N

Sources prioritised: Dawn, Business Recorder, Reuters, Bloomberg,
ARY Business, Geo Business, The News, Express Tribune, Tribune Business.
"""

from __future__ import annotations

import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from config.constants import (
    MACRO_QUERIES, PSX_TICKERS,
    SECTOR_NEWS_QUERIES, NEWS_LOOKBACK_DAYS,
)
from config.settings import get_settings

logger = logging.getLogger(__name__)


# ─── Data Model ──────────────────────────────────────────────────────────────

@dataclass
class Article:
    title: str
    description: str
    url: str
    source: str
    published_at: str
    relevance_score: float = 0.0
    sentiment: str = "NEUTRAL"
    sentiment_score: float = 0.0
    content: str = ""

    def __post_init__(self):
        self._id = hashlib.md5(self.title.encode()).hexdigest()[:12]

    @property
    def article_id(self) -> str:
        return self._id

    @property
    def short_description(self) -> str:
        desc = self.description or ""
        return desc[:250] + ("…" if len(desc) > 250 else "")

    @property
    def age_label(self) -> str:
        try:
            pub = datetime.fromisoformat(self.published_at.replace("Z", "+00:00"))
            delta = datetime.now(pub.tzinfo) - pub
            if delta.days == 0:
                hours = delta.seconds // 3600
                return f"{hours}h ago" if hours > 0 else "Just now"
            if delta.days == 1:
                return "Yesterday"
            return f"{delta.days}d ago"
        except Exception:
            return self.published_at[:10] if self.published_at else "Unknown"

    @property
    def is_credible_source(self) -> bool:
        credible = {
            "dawn", "business recorder", "reuters", "bloomberg", "the news",
            "express tribune", "geo", "ary", "pakistan today", "profit",
            "brecorder", "daily times", "tribune", "samaa",
        }
        src_lower = self.source.lower()
        return any(c in src_lower for c in credible)


# ─── Sentiment Engine ─────────────────────────────────────────────────────────
# Domain-tuned for PSX — includes Pakistan-specific financial vocabulary

BULLISH_SIGNALS = {
    # Generic positive
    "surge", "rally", "gain", "rise", "profit", "record", "beat", "growth",
    "upgrade", "buy", "bullish", "strong", "positive", "recovery", "boost",
    "dividend", "expansion", "revenue", "earnings", "inflow", "approval",
    "contract", "award", "investment", "outperform", "overweight",
    # Pakistan-specific positive
    "imf tranche", "imf disbursement", "current account surplus", "fx reserves rise",
    "sbp cut", "rate cut", "monetary easing", "rupee stable", "rupee gain",
    "circular debt resolution", "subsidy", "tariff increase approved",
    "psdp release", "budget surplus", "tax collection beat", "remittances rise",
    "export growth", "worker remittance", "foreign investment",
}

BEARISH_SIGNALS = {
    # Generic negative
    "fall", "drop", "decline", "loss", "miss", "weak", "sell", "bearish",
    "downgrade", "negative", "risk", "debt", "default", "concern",
    "pressure", "cut", "restructure", "penalty", "shortage", "ban",
    "sanction", "investigation", "lawsuit", "delay", "halt",
    # Pakistan-specific negative
    "imf condition", "imf demand", "circular debt", "devaluation", "depreciation",
    "rupee fall", "rupee weak", "sbp hike", "rate hike", "inflation surge",
    "cpi high", "fiscal deficit", "current account deficit", "fx reserves fall",
    "political instability", "strike", "protest", "load shedding",
    "gas shortage", "power outage", "super tax", "additional tax",
    "drap freeze", "price freeze", "subsidy removal", "subsidy cut",
    "psdp cut", "austerity", "npl rise", "non-performing", "loan default",
    "fatf grey", "fatf blacklist",
}


def _score_sentiment(text: str) -> tuple[str, float]:
    words = set(text.lower().split())
    # Also check bigrams
    tokens = text.lower().split()
    bigrams = {f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens)-1)}
    all_tokens = words | bigrams

    bull = len(all_tokens & BULLISH_SIGNALS)
    bear = len(all_tokens & BEARISH_SIGNALS)
    total = bull + bear

    if total == 0:
        return "NEUTRAL", 0.0
    score = (bull - bear) / total
    if score > 0.1:
        return "BULLISH", round(score, 3)
    if score < -0.1:
        return "BEARISH", round(score, 3)
    return "NEUTRAL", round(score, 3)


# ─── Relevance Scoring ────────────────────────────────────────────────────────

def _score_relevance(article: Article, ticker: str, full_name: str, sector: str) -> float:
    combined = f"{article.title} {article.description} {article.content}".lower()
    score = 0.0

    # Ticker exact match — highest signal
    if ticker.lower() in combined:
        score += 0.45

    # Company name words (skip short stop words)
    name_words = [w for w in full_name.lower().split() if len(w) > 3]
    if name_words:
        hits = sum(1 for w in name_words if w in combined)
        score += 0.30 * (hits / len(name_words))

    # Sector keywords
    sector_words = [w for w in sector.lower().replace("&", "").split() if len(w) > 3]
    if sector_words:
        hits = sum(1 for w in sector_words if w in combined)
        score += 0.15 * (hits / len(sector_words))

    # Credible source bonus
    if article.is_credible_source:
        score += 0.10

    return round(min(score, 1.0), 3)


# ─── Deduplication ───────────────────────────────────────────────────────────

def _jaccard(a: str, b: str) -> float:
    sa = set(a.lower().split())
    sb = set(b.lower().split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _deduplicate(articles: list[Article], threshold: float = 0.55) -> list[Article]:
    seen: list[Article] = []
    for art in articles:
        if not any(_jaccard(art.title, s.title) > threshold for s in seen):
            seen.append(art)
    return seen


# ─── Query Builder ────────────────────────────────────────────────────────────

def _build_queries(ticker: str, sector: str) -> list[str]:
    queries: set[str] = set()

    # Asset-specific
    queries.add(f"{ticker} Pakistan stock market")
    queries.add(f"{PSX_TICKERS.get(ticker, ticker)} Pakistan")
    queries.add(f"PSX KSE {ticker} shares")

    # Sector queries
    for q in SECTOR_NEWS_QUERIES.get(sector, []):
        queries.add(q)

    # Always: Pakistan macro
    for q in MACRO_QUERIES:
        queries.add(q)

    return list(queries)


# ─── Fetch Engine ─────────────────────────────────────────────────────────────

def _fetch_one(query: str, api_key: str) -> list[Article]:
    try:
        from newsapi import NewsApiClient
        client = NewsApiClient(api_key=api_key)
        from_date = (datetime.utcnow() - timedelta(days=NEWS_LOOKBACK_DAYS)).strftime("%Y-%m-%d")
        resp = client.get_everything(
            q=query,
            from_param=from_date,
            language="en",
            sort_by="relevancy",
            page_size=10,
        )
        results = []
        for raw in (resp.get("articles") or []):
            title = raw.get("title", "") or ""
            if not title or title == "[Removed]":
                continue
            results.append(Article(
                title=title,
                description=raw.get("description", "") or "",
                url=raw.get("url", ""),
                source=raw.get("source", {}).get("name", "Unknown"),
                published_at=raw.get("publishedAt", ""),
                content=raw.get("content", "") or "",
            ))
        return results
    except Exception as exc:
        logger.warning("News fetch failed for '%s': %s", query, exc)
        return []


# ─── Public API ──────────────────────────────────────────────────────────────

def fetch_news(ticker: str, sector: str, max_articles: int = 80) -> list[Article]:
    """
    Main entry. Returns up to max_articles Articles,
    deduplicated, relevance-scored, sentiment-labelled.
    """
    settings = get_settings()
    api_key = settings.NEWS_API_KEY

    if not api_key:
        logger.warning("NEWS_API_KEY not set — returning demo articles")
        return _demo_articles(ticker)

    full_name = PSX_TICKERS.get(ticker, ticker)
    queries = _build_queries(ticker, sector)
    raw_pool: list[Article] = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_fetch_one, q, api_key): q for q in queries}
        for future in as_completed(futures):
            raw_pool.extend(future.result())

    unique = _deduplicate(raw_pool)

    for art in unique:
        art.relevance_score = _score_relevance(art, ticker, full_name, sector)
        art.sentiment, art.sentiment_score = _score_sentiment(
            f"{art.title} {art.description}"
        )

    unique.sort(key=lambda a: (-a.relevance_score, a.published_at))
    return unique[:max_articles]


def _demo_articles(ticker: str) -> list[Article]:
    full_name = PSX_TICKERS.get(ticker, ticker)
    return [
        Article(
            title=f"[Demo] Add NEWS_API_KEY to load real articles for {full_name}",
            description=(
                "This program fetches 14-18 parallel news queries across asset-specific, "
                "sector-level, and Pakistan macro dimensions. Add your free NewsAPI key "
                "to .env to activate real-time news from Dawn, Reuters, Bloomberg, Business Recorder, and more."
            ),
            url="https://newsapi.org",
            source="PSX Intelligence",
            published_at=datetime.utcnow().isoformat(),
            relevance_score=1.0,
            sentiment="NEUTRAL",
        ),
        Article(
            title="[Demo] Dawn Business — Pakistan economy news would appear here",
            description="Real articles from Dawn, Business Recorder, Reuters, Bloomberg, The News, Express Tribune, and more.",
            url="https://dawn.com/business",
            source="Dawn",
            published_at=datetime.utcnow().isoformat(),
            relevance_score=0.9,
            sentiment="NEUTRAL",
        ),
        Article(
            title="[Demo] Business Recorder — KSE-100 market update would appear here",
            description="Pakistan's leading financial newspaper covering PSX, SBP, IMF, and sector-specific news.",
            url="https://brecorder.com",
            source="Business Recorder",
            published_at=datetime.utcnow().isoformat(),
            relevance_score=0.8,
            sentiment="NEUTRAL",
        ),
    ]