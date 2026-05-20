# PSX Intelligence

A Bloomberg-style market intelligence terminal for the Pakistan Stock Exchange (PSX),
built with Python and Streamlit.

Most dashboards show you what happened. This one explains why.

---

## What it does

**Causal Reasoning Engine**
Powered by GPT-4o, the AI doesn't just surface data — it builds causal chains.
SBP rate cut → NIM compression → banking sector EPS impact → price movement.
Specific, market-aware analysis grounded in Pakistan's macro environment.

**Live Market Data**
Real-time PSX ticker data via yfinance. Sector heatmaps showing relative
performance across the market at a glance.

**News Intelligence**
Multi-source news aggregation via NewsAPI pulling from Dawn, Business Recorder,
Reuters, Bloomberg, ARY Business, Geo Business, and Tribune Business.
Every article is scored for relevance and labeled for sentiment using
PSX-specific vocabulary.

**Portfolio Tracker**
Position-level tracking with stop loss and target price per holding.
P&L updated against live market data.

---

## Tech Stack

| Layer | Tools |
|---|---|
| UI | Streamlit |
| Market Data | yfinance |
| News | NewsAPI |
| AI Engine | OpenAI GPT-4o |
| Deployment | Streamlit Cloud |
| Language | Python |

---

## Project Structure
PSX Intelligence/
├── app.py               # Entry point
├── components/          # UI components (dashboard, heatmap, portfolio, news feed)
├── services/            # Data layer (market data, news, AI engine)
├── config/              # Settings and constants
├── utils/               # Helpers
└── views/               # Page-level views

---

*Built as part of an ongoing focus on the intersection of financial markets
and technology. Real market logic, not tutorial projects.*
