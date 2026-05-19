"""
services/market_data.py
────────────────────────
Live and historical PSX market data via yfinance.
Includes volatility tagging, sector classification, heatmap fetch.
All public functions are wrapped with st.cache_data in app.py.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd
import yfinance as yf

from config.constants import (
    PSX_TICKERS, SECTOR_MAP, ALIAS_MAP,
    TICKER_SUFFIX, HEATMAP_TICKERS,
)

logger = logging.getLogger(__name__)


# ─── Data Model ──────────────────────────────────────────────────────────────

@dataclass
class AssetSnapshot:
    ticker: str
    full_name: str
    sector: str
    currency: str
    current_price: Optional[float]
    prev_close: Optional[float]
    open_price: Optional[float]
    day_high: Optional[float]
    day_low: Optional[float]
    volume: Optional[int]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    week_52_high: Optional[float]
    week_52_low: Optional[float]
    pct_change: Optional[float]
    abs_change: Optional[float]
    beta: Optional[float]
    dividend_yield: Optional[float]
    shares_outstanding: Optional[float]
    error: Optional[str] = None
    raw_info: dict = field(default_factory=dict)

    @property
    def is_valid(self) -> bool:
        return self.current_price is not None and self.error is None

    @property
    def movement_label(self) -> str:
        if self.pct_change is None:
            return "FLAT"
        if self.pct_change > 4:
            return "STRONG RALLY"
        if self.pct_change > 1:
            return "GAINING"
        if self.pct_change < -4:
            return "SHARP DECLINE"
        if self.pct_change < -1:
            return "DECLINING"
        return "FLAT / NOISE"

    @property
    def volatility_tag(self) -> str:
        """Flag if today's move is unusual vs 52-week range."""
        if (self.pct_change is None or self.week_52_high is None
                or self.week_52_low is None or self.current_price is None):
            return "NORMAL"
        annual_range = (self.week_52_high or 0) - (self.week_52_low or 0)
        if annual_range == 0:
            return "NORMAL"
        daily_move_fraction = abs(self.abs_change or 0) / annual_range
        if daily_move_fraction > 0.06:
            return "ELEVATED — top 5% of historical daily moves"
        if daily_move_fraction > 0.03:
            return "ABOVE NORMAL"
        return "NORMAL"

    @property
    def position_in_range(self) -> Optional[float]:
        """0.0 = at 52-week low, 1.0 = at 52-week high."""
        if None in (self.current_price, self.week_52_high, self.week_52_low):
            return None
        rng = (self.week_52_high or 0) - (self.week_52_low or 0)
        if rng == 0:
            return 0.5
        return ((self.current_price or 0) - (self.week_52_low or 0)) / rng


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _resolve_ticker(query: str) -> tuple[str, str]:
    """Resolve user search string → (clean_ticker, yfinance_ticker)."""
    q = query.strip()
    q_lower = q.lower()

    # Alias map (handles common names, abbreviations)
    if q_lower in ALIAS_MAP:
        clean = ALIAS_MAP[q_lower]
        yf_ticker = f"{clean}{TICKER_SUFFIX}" if clean != "KSE100" else "^KSE100"
        return clean, yf_ticker

    q_upper = q.upper()

    # Direct ticker match
    if q_upper in PSX_TICKERS:
        return q_upper, f"{q_upper}{TICKER_SUFFIX}"

    # Partial ticker match
    for ticker in PSX_TICKERS:
        if q_upper in ticker:
            return ticker, f"{ticker}{TICKER_SUFFIX}"

    # Partial name match
    for ticker, name in PSX_TICKERS.items():
        if q_upper in name.upper():
            return ticker, f"{ticker}{TICKER_SUFFIX}"

    # Fall back — pass raw to yfinance
    return q_upper, q_upper


def _get_sector(ticker: str) -> str:
    for sector, tickers in SECTOR_MAP.items():
        if ticker in tickers:
            return sector
    return "General Market"


def _safe_float(val) -> Optional[float]:
    try:
        f = float(val)
        return None if (f != f) else f  # NaN check
    except Exception:
        return None


def _safe_int(val) -> Optional[int]:
    try:
        return int(float(val))
    except Exception:
        return None


# ─── Core Fetchers ────────────────────────────────────────────────────────────

def fetch_asset_snapshot(query: str) -> AssetSnapshot:
    """Fetch complete market snapshot. Never raises — returns error in dataclass."""
    ticker_clean, yf_ticker = _resolve_ticker(query)
    full_name = PSX_TICKERS.get(ticker_clean, ticker_clean)
    sector = _get_sector(ticker_clean)

    try:
        yf_obj = yf.Ticker(yf_ticker)
        info = yf_obj.info or {}

        current = _safe_float(
            info.get("currentPrice") or info.get("regularMarketPrice")
        )
        prev_close = _safe_float(
            info.get("previousClose") or info.get("regularMarketPreviousClose")
        )
        open_p = _safe_float(info.get("open") or info.get("regularMarketOpen"))
        day_high = _safe_float(info.get("dayHigh") or info.get("regularMarketDayHigh"))
        day_low = _safe_float(info.get("dayLow") or info.get("regularMarketDayLow"))
        volume = _safe_int(info.get("volume") or info.get("regularMarketVolume"))
        market_cap = _safe_float(info.get("marketCap"))
        pe = _safe_float(info.get("trailingPE"))
        w52h = _safe_float(info.get("fiftyTwoWeekHigh"))
        w52l = _safe_float(info.get("fiftyTwoWeekLow"))
        beta = _safe_float(info.get("beta"))
        div_yield = _safe_float(info.get("dividendYield"))
        shares = _safe_float(info.get("sharesOutstanding"))
        currency = info.get("currency", "PKR")
        long_name = info.get("longName") or info.get("shortName") or full_name

        pct_change: Optional[float] = None
        abs_change: Optional[float] = None
        if current is not None and prev_close is not None and prev_close != 0:
            abs_change = current - prev_close
            pct_change = (abs_change / prev_close) * 100

        return AssetSnapshot(
            ticker=ticker_clean,
            full_name=long_name,
            sector=sector,
            currency=currency,
            current_price=current,
            prev_close=prev_close,
            open_price=open_p,
            day_high=day_high,
            day_low=day_low,
            volume=volume,
            market_cap=market_cap,
            pe_ratio=pe,
            week_52_high=w52h,
            week_52_low=w52l,
            pct_change=pct_change,
            abs_change=abs_change,
            beta=beta,
            dividend_yield=div_yield,
            shares_outstanding=shares,
            raw_info=info,
        )

    except Exception as exc:
        logger.error("Snapshot fetch failed for %s: %s", yf_ticker, exc)
        return AssetSnapshot(
            ticker=ticker_clean, full_name=full_name, sector=sector,
            currency="PKR", current_price=None, prev_close=None, open_price=None,
            day_high=None, day_low=None, volume=None, market_cap=None,
            pe_ratio=None, week_52_high=None, week_52_low=None,
            pct_change=None, abs_change=None, beta=None, dividend_yield=None,
            shares_outstanding=None, error=str(exc),
        )


def fetch_price_history(query: str, period: str = "6mo") -> pd.DataFrame:
    """
    Return OHLCV DataFrame with MA-20, MA-50, Bollinger Bands, daily returns.
    Returns empty DataFrame on failure.
    """
    ticker_clean, yf_ticker = _resolve_ticker(query)
    try:
        df = yf.Ticker(yf_ticker).history(period=period, auto_adjust=True)
        if df.empty:
            return pd.DataFrame()

        df.index = pd.to_datetime(df.index)
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.dropna(subset=["Close"], inplace=True)

        # Technical indicators
        df["MA20"] = df["Close"].rolling(20).mean()
        df["MA50"] = df["Close"].rolling(50).mean()
        rolling_std = df["Close"].rolling(20).std()
        df["BB_upper"] = df["MA20"] + 2 * rolling_std
        df["BB_lower"] = df["MA20"] - 2 * rolling_std
        df["DailyReturn"] = df["Close"].pct_change() * 100
        df["CumReturn"] = ((1 + df["DailyReturn"].fillna(0) / 100).cumprod() - 1) * 100

        return df
    except Exception as exc:
        logger.error("Price history failed for %s: %s", yf_ticker, exc)
        return pd.DataFrame()


def fetch_sector_heatmap() -> list[dict]:
    """Fetch % change for KSE-100 blue chips for the heatmap panel."""
    results = []
    for t in HEATMAP_TICKERS:
        snap = fetch_asset_snapshot(t)
        results.append({
            "ticker": t,
            "name": snap.full_name,
            "sector": snap.sector,
            "pct_change": snap.pct_change,
            "price": snap.current_price,
            "volume": snap.volume,
        })
    return results