"""
services/ai_engine.py
──────────────────────
The PSX Intelligence reasoning engine.

This is NOT a news summariser. It is a financial causation engine.
Given a price movement + news corpus + earnings sensitivity map,
it produces:

  1. The exact causal chain:  Event → Mechanism → Earnings Impact → Price Logic
  2. A plain-English explanation (for learners who don't know economics)
  3. A technical explanation (investor-grade language)
  4. Ranked contributing signals with causal weights
  5. Forward-looking risk flags with time horizons

The earnings sensitivity map (constants.py) is injected into the prompt
so the AI knows exactly which macro variables affect THIS sector's income
statement — and by how much. This is what makes explanations technically
accurate rather than generically plausible.

Design decisions:
  - response_format: json_object → reliable structured output, no parsing failures
  - temperature 0.15 → analytical precision, not creative writing
  - tenacity retry → graceful on transient OpenAI errors
  - Separate plain_english + technical explanations → serves both learners and analysts
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from config.constants import EARNINGS_SENSITIVITY, PSX_TICKERS
from config.settings import get_settings
from services.market_data import AssetSnapshot
from services.news_service import Article

logger = logging.getLogger(__name__)


# ─── Output Models ───────────────────────────────────────────────────────────

@dataclass
class CausalSignal:
    category: str        # MACRO | REGULATORY | SECTOR | COMPANY | SENTIMENT
    signal: str          # One-line description of the signal
    weight: float        # 0-1 causal contribution weight
    direction: str       # BULLISH | BEARISH | MIXED
    mechanism: str       # How this signal translates to price impact
    evidence: str        # Direct quote or paraphrase from article
    source: str = ""     # News source name


@dataclass
class RiskFlag:
    description: str     # What the risk is
    time_horizon: str    # "This week" | "Next quarter" | "Ongoing" etc
    severity: str        # HIGH | MEDIUM | LOW


@dataclass
class AIAnalysis:
    # Core causal output
    primary_cause: str                    # Single sentence: the #1 reason
    causal_chain: str                     # Event → Mechanism → Earnings → Price
    causal_signals: list[CausalSignal]    # All contributing signals, ranked

    # Dual explanations (the key learner feature)
    plain_english: str                    # Zero-jargon explanation
    technical_explanation: str            # Investor-grade language

    # Technical context
    technical_context: str               # Price action framing (move size, volume, trend)

    # Forward risks
    risk_flags: list[RiskFlag]

    # Metadata
    confidence: str                       # HIGH | MEDIUM | LOW
    confidence_reason: str                # Why this confidence level
    sentiment_distribution: dict[str, int]
    articles_analysed: int
    move_is_noise: bool                   # True if move < 0.5% (likely no catalyst)

    error: Optional[str] = None

    @property
    def is_valid(self) -> bool:
        return self.error is None


# ─── System Prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a senior equity research analyst at a Pakistan-focused investment bank,
with 15 years of experience covering KSE-100 stocks.

You serve TWO audiences simultaneously:
  1. Beginners learning the stock market who need plain-English explanations
  2. Sophisticated investors who need technically precise causal analysis

Your job: given a PSX stock's price movement + news articles + the sector's
earnings sensitivity map, explain EXACTLY WHY the stock moved.

CRITICAL RULES:
1. NEVER invent statistics, earnings figures, or events not in the provided data.
   If you cite a number, it must come from the articles or the sensitivity map.
2. Use the CAUSAL HIERARCHY — this determines signal weight priority:
   MACRO (IMF, SBP rate, rupee, inflation, fiscal) 
   > REGULATORY (SECP, OGRA, NEPRA, DRAP, SBP notifications, SROs)
   > SECTOR (industry-wide events, commodity prices, monthly data)
   > COMPANY (earnings, dividends, management, capacity)
   > SENTIMENT (analyst ratings, media tone)
3. If the move is less than 0.5%, set move_is_noise=true and say so clearly.
4. For plain_english: imagine explaining to a university student with no finance background.
   Use real-world analogies. Never use jargon without explaining it first.
5. For technical_explanation: use precise financial language appropriate for
   a Bloomberg terminal user — NIM, EPS revision, multiple compression,
   operating leverage, circular debt, etc.
6. For the causal_chain: write it EXACTLY in this format:
   "[Event] → [How it affects business operations] → [How that changes earnings] → [Why that caused this price move]"
7. Confidence levels:
   HIGH   = specific catalyst directly linked to this stock found in articles
   MEDIUM = sector-level or indirect catalysts found; plausible but not certain
   LOW    = no relevant catalyst found; move may be technical, macro noise, or random
8. Return ONLY valid JSON. No markdown, no explanation outside JSON, no code fences.

JSON SCHEMA — return exactly this structure:
{
  "primary_cause": "<single sentence — the #1 most likely reason for the move>",
  "causal_chain": "<Event → Mechanism → Earnings Impact → Price Logic>",
  "causal_signals": [
    {
      "category": "<MACRO|REGULATORY|SECTOR|COMPANY|SENTIMENT>",
      "signal": "<concise one-line description>",
      "weight": <0.0 to 1.0>,
      "direction": "<BULLISH|BEARISH|MIXED>",
      "mechanism": "<how this signal translates into earnings/price impact>",
      "evidence": "<quote or close paraphrase from article, or 'Inferred from sensitivity map'>",
      "source": "<publication name or 'Analysis'>"
    }
  ],
  "plain_english": "<3-4 sentences explaining WHY the stock moved in simple language a student can understand. Use analogies. No jargon.>",
  "technical_explanation": "<4-6 sentences in investor-grade language connecting macro signals, earnings mechanics, and price action. Use precise financial terminology.>",
  "technical_context": "<2-3 sentences on: move magnitude vs 52-week range, whether volume confirms the move, where price sits in trend>",
  "risk_flags": [
    {
      "description": "<specific, concrete forward risk>",
      "time_horizon": "<This week|Next month|Next quarter|Ongoing>",
      "severity": "<HIGH|MEDIUM|LOW>"
    }
  ],
  "confidence": "<HIGH|MEDIUM|LOW>",
  "confidence_reason": "<one sentence explaining why this confidence level>",
  "move_is_noise": <true|false>
}
"""


# ─── Prompt Builder ──────────────────────────────────────────────────────────

def _build_prompt(snapshot: AssetSnapshot, articles: list[Article]) -> str:
    sector = snapshot.sector
    sensitivity = EARNINGS_SENSITIVITY.get(sector, {})

    # Sensitivity map block
    sens_block = ""
    if sensitivity:
        sens_block = f"""
=== EARNINGS SENSITIVITY MAP FOR {sector.upper()} ===
Business model: {sensitivity.get('business_model_plain_english', 'N/A')}
Primary revenue driver: {sensitivity.get('primary_revenue_driver', 'N/A')}

Key sensitivities (use these to assess which news events are MOST LIKELY causal):
"""
        for s in sensitivity.get("sensitivities", []):
            sens_block += (
                f"\n  VARIABLE: {s['variable']}\n"
                f"  DIRECTION: {s['direction']}\n"
                f"  MECHANISM: {s['mechanism']}\n"
                f"  MAGNITUDE: {s['magnitude']}\n"
                f"  SIMPLE: {s.get('simple_explanation', '')}\n"
                f"  ---"
            )
        sens_block += f"\n\nKey metrics to watch: {', '.join(sensitivity.get('key_metrics', []))}"
        sens_block += f"\nCredible sources for this sector: {', '.join(sensitivity.get('credible_sources', []))}"

    # Market data block
    pct = snapshot.pct_change
    market_block = f"""
=== STOCK UNDER ANALYSIS ===
Ticker:           {snapshot.ticker}
Full Name:        {snapshot.full_name}
Sector:           {sector}
Exchange:         Pakistan Stock Exchange (KSE-100)

=== TODAY'S MARKET DATA ===
Current Price:    {snapshot.current_price} {snapshot.currency}
Change:           {f"{snapshot.abs_change:+.2f}" if snapshot.abs_change else "N/A"} PKR  ({f"{pct:+.2f}" if pct else "N/A"}%)
Movement Label:   {snapshot.movement_label}
Volatility:       {snapshot.volatility_tag}
Open:             {snapshot.open_price}
Day High:         {snapshot.day_high}
Day Low:          {snapshot.day_low}
Previous Close:   {snapshot.prev_close}
52-Week High:     {snapshot.week_52_high}
52-Week Low:      {snapshot.week_52_low}
Position in Range:{f"{snapshot.position_in_range:.0%}" if snapshot.position_in_range is not None else "N/A"} (0%=52wk low, 100%=52wk high)
Volume:           {f"{snapshot.volume:,}" if snapshot.volume else "N/A"} shares
Market Cap:       {snapshot.market_cap}
P/E Ratio:        {snapshot.pe_ratio}
Beta:             {snapshot.beta}
Dividend Yield:   {snapshot.dividend_yield}
"""

    # Sentiment stats
    bull = sum(1 for a in articles if a.sentiment == "BULLISH")
    bear = sum(1 for a in articles if a.sentiment == "BEARISH")
    neut = len(articles) - bull - bear

    stats_block = f"""
=== NEWS CORPUS STATISTICS ===
Total articles analysed: {len(articles)}
Sentiment distribution: BULLISH={bull} | BEARISH={bear} | NEUTRAL={neut}
Queries run: ~16 parallel queries (asset-specific + sector + Pakistan macro)
"""

    # Article digest (top 40 by relevance)
    top = articles[:40]
    art_block = "\n=== NEWS ARTICLES (ranked by relevance to this stock) ===\n"
    for i, art in enumerate(top, 1):
        credible_tag = "✓ CREDIBLE SOURCE" if art.is_credible_source else ""
        art_block += (
            f"\n[{i}] [{art.sentiment}] {credible_tag}\n"
            f"    SOURCE: {art.source} | {art.age_label}\n"
            f"    HEADLINE: {art.title}\n"
            f"    BODY: {art.short_description}\n"
            f"    RELEVANCE: {art.relevance_score:.0%}\n"
        )

    return (
        market_block + "\n"
        + sens_block + "\n"
        + stats_block + "\n"
        + art_block
        + "\n=== END OF DATA ===\n"
        + "\nNow perform your causal analysis and return the JSON.\n"
    )


# ─── OpenAI Call ──────────────────────────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8), reraise=False)
def _call_gpt(user_prompt: str) -> str:
    from openai import OpenAI
    settings = get_settings()
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=1500,
        temperature=0.15,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or ""


# ─── Public API ──────────────────────────────────────────────────────────────

def run_analysis(snapshot: AssetSnapshot, articles: list[Article]) -> AIAnalysis:
    """
    Main entry. Returns AIAnalysis. Never raises — falls back to demo/error.
    """
    settings = get_settings()
    bull = sum(1 for a in articles if a.sentiment == "BULLISH")
    bear = sum(1 for a in articles if a.sentiment == "BEARISH")
    sent_dist = {"BULLISH": bull, "BEARISH": bear, "NEUTRAL": len(articles) - bull - bear}

    if not settings.OPENAI_API_KEY:
        return _demo_analysis(snapshot, articles, sent_dist)

    if not snapshot.is_valid:
        return _error_analysis(
            "Market data unavailable — check ticker symbol.", sent_dist, len(articles)
        )

    try:
        prompt = _build_prompt(snapshot, articles)
        raw = _call_gpt(prompt)
        data = json.loads(raw)

        signals = []
        for s in data.get("causal_signals", []):
            signals.append(CausalSignal(
                category=s.get("category", "MACRO"),
                signal=s.get("signal", ""),
                weight=float(s.get("weight", 0.5)),
                direction=s.get("direction", "MIXED"),
                mechanism=s.get("mechanism", ""),
                evidence=s.get("evidence", ""),
                source=s.get("source", ""),
            ))
        signals.sort(key=lambda x: x.weight, reverse=True)

        risk_flags = []
        for r in data.get("risk_flags", []):
            risk_flags.append(RiskFlag(
                description=r.get("description", ""),
                time_horizon=r.get("time_horizon", "Ongoing"),
                severity=r.get("severity", "MEDIUM"),
            ))

        return AIAnalysis(
            primary_cause=data.get("primary_cause", ""),
            causal_chain=data.get("causal_chain", ""),
            causal_signals=signals,
            plain_english=data.get("plain_english", ""),
            technical_explanation=data.get("technical_explanation", ""),
            technical_context=data.get("technical_context", ""),
            risk_flags=risk_flags,
            confidence=data.get("confidence", "MEDIUM"),
            confidence_reason=data.get("confidence_reason", ""),
            sentiment_distribution=sent_dist,
            articles_analysed=len(articles),
            move_is_noise=data.get("move_is_noise", False),
        )

    except json.JSONDecodeError as e:
        logger.error("AI JSON parse error: %s", e)
        return _error_analysis(f"Response parse error: {e}", sent_dist, len(articles))
    except Exception as e:
        logger.error("AI analysis error: %s", e)
        return _error_analysis(str(e), sent_dist, len(articles))


# ─── Fallbacks ────────────────────────────────────────────────────────────────

def _error_analysis(msg: str, sent_dist: dict, n: int) -> AIAnalysis:
    return AIAnalysis(
        primary_cause="AI analysis unavailable.",
        causal_chain="N/A",
        causal_signals=[],
        plain_english=f"AI analysis could not be completed: {msg}",
        technical_explanation=f"Error: {msg}. Check  in .env.",
        technical_context="",
        risk_flags=[],
        confidence="LOW",
        confidence_reason="Analysis failed",
        sentiment_distribution=sent_dist,
        articles_analysed=n,
        move_is_noise=False,
        error=msg,
    )


def _demo_analysis(snapshot: AssetSnapshot, articles: list[Article], sent_dist: dict) -> AIAnalysis:
    pct = snapshot.pct_change or 0
    direction = "declined" if pct < 0 else "gained"
    ticker = snapshot.ticker
    sector = snapshot.sector
    sensitivity = EARNINGS_SENSITIVITY.get(sector, {})
    primary_driver = sensitivity.get("primary_revenue_driver", "market forces")

    # Build demo signal from sensitivity map
    demo_signals = []
    for s in sensitivity.get("sensitivities", [])[:3]:
        demo_signals.append(CausalSignal(
            category="MACRO",
            signal=f"[Demo] {s['variable']}",
            weight=round(0.9 - demo_signals.__len__() * 0.25, 2),
            direction=s["direction"].split(" ")[0] if s["direction"] else "MIXED",
            mechanism=s["mechanism"][:200] + "…",
            evidence="[Demo] Set OPENAI_API_KEY to see evidence cited from real articles.",
            source="Earnings Sensitivity Map",
        ))

    return AIAnalysis(
        primary_cause=(
            f"{snapshot.full_name} {direction} {abs(pct):.2f}% today. "
            f"Add your OPENAI_API_KEY to .env to generate the AI causal explanation."
        ),
        causal_chain=(
            f"[Demo] Macro event → Affects {primary_driver} → "
            f"Changes forward earnings estimate → Market reprices stock"
        ),
        causal_signals=demo_signals,
        plain_english=(
            f"[Demo Mode] {snapshot.full_name} is a {sector} company. "
            f"Its profits depend primarily on {primary_driver}. "
            f"When relevant news affects those drivers, the stock price adjusts to reflect "
            f"the new expected profitability. "
            f"Add your OpenAI API key to see the full plain-English explanation of today's move."
        ),
        technical_explanation=(
            f"[Demo Mode] {snapshot.full_name} trades at a market-implied earnings multiple "
            f"sensitive to {primary_driver}. "
            f"Today's {abs(pct):.2f}% {'decline' if pct < 0 else 'gain'} represents "
            f"{'a meaningful de-rating' if abs(pct) > 2 else 'noise-level movement'} "
            f"relative to its 52-week range of "
            f"{snapshot.week_52_low}–{snapshot.week_52_high} PKR. "
            f"Add OPENAI_API_KEY to activate full technical causal analysis."
        ),
        technical_context=(
            f"{snapshot.full_name} is currently at {snapshot.current_price} PKR, "
            f"{'down' if pct < 0 else 'up'} {abs(pct):.2f}% from previous close of {snapshot.prev_close} PKR. "
            f"52-week range: {snapshot.week_52_low}–{snapshot.week_52_high} PKR."
        ),
        risk_flags=[
            RiskFlag(
                description="Add OPENAI_API_KEY to generate real forward risk flags from article analysis",
                time_horizon="Ongoing",
                severity="MEDIUM",
            )
        ],
        confidence="LOW",
        confidence_reason="Demo mode — no AI analysis performed",
        sentiment_distribution=sent_dist,
        articles_analysed=len(articles),
        move_is_noise=abs(pct) < 0.5,
    )