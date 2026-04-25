# 📈 StockMind AI: Long-term Stock Recommendation Engine

AI-powered stock analysis for **global markets** — US, India, UK, Europe, Japan, Hong Kong, Australia, Canada, crypto, and more. Built with a full-stack architecture featuring a multi-agent AI backend and a modern React frontend.

## Features

- **AI Analysis & Resiliency** — LangGraph orchestrates multi-source data analyzed by Gemini 2.0 Flash with an **automatic fallback to OpenAI (GPT-4o Mini)** if quota limits are reached.
- **Searchable FX Converter** — Live exchange rates with a **fuzzy-search selector** supporting **150+ global currencies** with flags. Includes reciprocal rate logic for minor pairs and historical charts.
- **Risk-Based AI Baskets** — Generate curated portfolios based on **Risk Tolerance** (Low, Medium, High). Assets are assigned specific percentage weights and visual allocation bars.
- **Indian Mutual Funds** — Dedicated tab for discovering high-quality **Indian Mutual Funds and ETFs** using real exchange symbols (e.g., `0P0000XW8F.BO`, `NIFTYBEES.NS`).
- **Interactive Dashboard** — Batch **"Analyze All"** feature and individual **"Analyze Again"** buttons. All timestamps are automatically converted to your **local system time**.
- **Click-to-Analyze** — Click any stock or fund inside a saved basket to immediately open its detailed valuation modal and live charts.
- **Model Transparency** — Every recommendation explicitly states which AI model (Gemini or OpenAI) performed the analysis.
- **Global Market Support** — Resolves correct flags, symbols, and exchanges for tickers like `.NS`, `.L`, `.DE`, `.T`, `.HK`, `.AX`, `.TO`, `.SA`, etc.
- **Real-time Updates** — WebSockets push new analyses instantly to the UI as they complete.

## Architecture

- **Backend**: FastAPI · APScheduler · SQLAlchemy (SQLite) · yfinance · LangGraph
- **AI Agent**: Stateful graph execution with cross-provider LLM fallback logic.
- **Frontend**: React 19 + Vite · Recharts · Glassmorphic UI · Searchable Comboboxes

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

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

## Supported Ticker Formats

| Example | Exchange | Currency |
| ------- | -------- | -------- |
| `AAPL`, `MSFT` | NYSE / NASDAQ | USD $ |
| `RELIANCE.NS`, `HDFCBANK.NS` | NSE India | INR ₹ |
| `0P0000XW8F.BO` | Indian Mutual Fund | INR ₹ |
| `BARC.L` | London Stock Exchange | GBP £ |
| `BTC-USD`, `ETH-USD` | Crypto | USD $ |

## API Endpoints

| Method | Path | Description |
| ------ | ---- | ----------- |
| `GET` | `/api/recommendations` | Latest recommendations with model attribution |
| `POST` | `/api/analyze?ticker=AAPL` | Trigger live analysis for any ticker |
| `GET` | `/api/asset?ticker=AAPL` | Full snapshot with valuation & intrinsic value proxy |
| `GET` | `/api/history/{ticker}?period=1mo` | OHLCV price history |
| `GET` | `/api/forex/{base}/{quote}?period=1mo` | FX rate + history (handles inverse pairs) |
| `GET` | `/api/basket/{market}?risk=Medium` | AI-curated weighted basket |
| `GET` | `/api/baskets` | List all saved portfolios |
| `WS` | `/ws` | Real-time push for new recommendations |

Valid `period` values: `1d 5d 1mo 3mo 6mo 1y 2y 5y 10y ytd max`
