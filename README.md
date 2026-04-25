# 📈 StockMind AI: Long-term Stock Recommendation Engine

AI-powered stock analysis for **global markets** — US, India, UK, Europe, Japan, Hong Kong, Australia, Canada, crypto, and more. Built simulating a full software development team (PM, Backend Dev, AI/Agent Dev, Frontend Dev).

## Features

- **AI analysis** — LangGraph + Gemini/OpenAI produces Buy/Hold/Sell recommendations with confidence scores and detailed reasoning.
- **Global market support** — resolves the correct country flag, currency symbol, and exchange for 50+ suffixes (`.NS`, `.L`, `.DE`, `.T`, `.HK`, `.AX`, `.TO`, `.SA`, and more) plus bare US tickers and crypto pairs like `BTC-USD`.
- **Price history charts** — interactive Recharts line chart inside each asset modal with 1M / 3M / 6M / 1Y / 5Y period selector.
- **FX Converter** — live exchange rates via Yahoo Finance with a 1-month rate history chart. Supports 30+ currency pairs.
- **Curated AI baskets** — ask the LLM for a country-specific portfolio of 3–5 top stocks/ETFs.
- **Real-time WebSocket** updates push new analyses to all connected clients the moment they complete.
- **Hourly background refresh** for a configurable watchlist via APScheduler.

## Architecture

- **Backend**: FastAPI · APScheduler · SQLAlchemy (SQLite) · yfinance · LangGraph
- **AI Agent**: LangGraph orchestrating DuckDuckGo News + Yahoo Finance, analyzed by Gemini or OpenAI
- **Frontend**: React 19 + Vite · Recharts · Glassmorphic CSS

## 🚀 Getting Started

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill in your API key
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
| `AAPL`, `MSFT` | NYSE / NASDAQ | USD |
| `RELIANCE.NS`, `HDFCBANK.NS` | NSE India | INR ₹ |
| `BARC.L` | London Stock Exchange | GBP £ |
| `SAP.DE` | XETRA Germany | EUR € |
| `7203.T` | Tokyo | JPY ¥ |
| `0700.HK` | HKEX | HKD HK$ |
| `BHP.AX` | ASX Australia | AUD A$ |
| `RY.TO` | TSX Canada | CAD C$ |
| `VALE3.SA` | B3 Brazil | BRL R$ |
| `BTC-USD`, `ETH-USD` | Crypto | USD |

## API Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/api/recommendations` | Latest recommendation per tracked ticker |
| `POST` | `/api/analyze/{ticker}` | Trigger analysis for any ticker |
| `GET` | `/api/history/{ticker}?period=1mo` | OHLCV price history |
| `GET` | `/api/forex/{base}/{quote}?period=1mo` | FX rate + history |
| `GET` | `/api/basket/{country}` | AI-curated country basket |
| `WS` | `/ws` | Real-time push for new recommendations |

Valid `period` values: `1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max`

## Multi-Agent Flow

1. **Data Node** — fetches market cap, P/E, 1-month price history, dividend yield via `yfinance`; recent news via DuckDuckGo.
2. **Analysis Node** — feeds structured data to the LLM (Gemini 2.5 Flash or GPT-4) acting as a Wall Street quant analyst.
3. Result is persisted to SQLite and broadcast over WebSocket.

Orchestrated by **LangGraph** for robust stateful graph execution.
