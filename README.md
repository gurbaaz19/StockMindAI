# 📈 StockMind AI: Long-term Stock Recommendation Engine

AI-powered stock analysis for **global markets** — US, India, UK, Europe, Japan, Hong Kong, Australia, Canada, crypto, and more. Built with a full-stack architecture featuring a multi-agent AI backend and a modern React frontend.

## Features

- **AI analysis** — LangGraph orchestrates DuckDuckGo News + Yahoo Finance data, analyzed by Gemini 2.5 Flash or GPT-4 to produce Buy/Hold/Sell recommendations with confidence scores.
- **Searchable FX Converter** — Live exchange rates with a **searchable selector** supporting **150+ global currencies** with flags. Includes historical rate charts with 1M to 5Y period selection.
- **Risk-Based AI Baskets** — Generate curated portfolios of 3–5 top assets based on **Risk Tolerance** (Low, Medium, High). Assets are assigned specific percentage weights tailored to the risk profile.
- **Indian Mutual Funds** — Dedicated tab for discovering and analyzing high-quality **Indian Mutual Funds and ETFs** (NIFTYBEES, GOLDBEES, etc.) using local exchange symbols.
- **Saved Baskets & Dashboard** — Name and save any curated basket to your dashboard. The dashboard provides a visual breakdown of your saved portfolios with **percentage allocation progress bars**.
- **Global market support** — Resolves the correct country flag, currency symbol, and exchange for almost any global ticker suffix (`.NS`, `.L`, `.DE`, `.T`, `.HK`, `.AX`, `.TO`, `.SA`, etc.).
- **Price history charts** — Interactive Recharts line chart inside each asset modal with 1M / 3M / 6M / 1Y / 5Y period selector.
- **Real-time WebSocket** updates push new analyses to all connected clients the moment they complete.
- **Hourly background refresh** for a configurable watchlist via APScheduler.

## Architecture

- **Backend**: FastAPI · APScheduler · SQLAlchemy (SQLite) · yfinance · LangGraph
- **AI Agent**: LangGraph stateful execution of data fetching and LLM analysis nodes.
- **Frontend**: React 19 + Vite · Recharts · Glassmorphic CSS · Lucide Icons

## 🚀 Getting Started

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill in your Gemini/OpenAI API keys
uvicorn main:app --reload
```

Runs on `http://localhost:8000`. On startup it immediately analyzes the default watchlist:
`AAPL, MSFT, GOOGL, AMZN, TSLA, GOLDBEES.NS, HDFCBANK.NS, V`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Supported Ticker Formats

| Example | Exchange | Currency |
| ------- | -------- | -------- |
| `AAPL`, `MSFT` | NYSE / NASDAQ | USD $ |
| `RELIANCE.NS`, `HDFCBANK.NS` | NSE India | INR ₹ |
| `0P0000XW8F.BO` | Indian Mutual Fund | INR ₹ |
| `BARC.L` | London Stock Exchange | GBP £ |
| `SAP.DE` | XETRA Germany | EUR € |
| `7203.T` | Tokyo | JPY ¥ |
| `0700.HK` | HKEX | HKD HK$ |
| `BTC-USD`, `ETH-USD` | Crypto | USD $ |

## API Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/api/recommendations` | Latest recommendation per tracked ticker |
| `POST` | `/api/analyze/{ticker}` | Trigger analysis for any ticker |
| `GET` | `/api/asset?ticker=AAPL` | Full snapshot with valuation & intrinsic value proxy |
| `GET` | `/api/history/{ticker}?period=1mo` | OHLCV price history |
| `GET` | `/api/forex/{base}/{quote}?period=1mo` | FX rate + history |
| `GET` | `/api/basket/{market}?risk=Medium` | AI-curated weighted basket |
| `GET` | `/api/baskets` | List all saved baskets |
| `POST` | `/api/baskets` | Save a new named basket |
| `WS` | `/ws` | Real-time push for new recommendations |

Valid `period` values: `1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max`

## Multi-Agent Flow

1. **Data Node** — fetches market cap, P/E, 1-month price history, dividend yield via `yfinance`; recent news via DuckDuckGo.
2. **Analysis Node** — feeds structured data to the LLM (Gemini 2.5 Flash or GPT-4) acting as a Wall Street quant analyst.
3. **Persistence & Broadcast** — Result is persisted to SQLite and broadcast over WebSocket for instant UI updates.

Orchestrated by **LangGraph** for robust stateful graph execution.
