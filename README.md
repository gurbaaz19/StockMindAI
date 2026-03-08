# 📈 StockMind AI: Long-term Stock Recommendation Engine

This project was built simulating a full software development team (Project Manager, Backend Dev, AI/Agent Dev, and Frontend Dev).

## Architecture
- **Backend**: FastAPI (Python), APScheduler (for hourly background refresh), SQLAlchemy (SQLite).
- **AI Agent**: LangGraph orchestrating DuckDuckGo News and Yahoo Finance data, analyzed by Gemini/OpenAI models.
- **Frontend**: React + Vite using stunning Glassmorphic CSS design patterns for a premium look and feel.

## 🚀 Getting Started

### 1. Backend Setup
Navigate to the `backend/` directory:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file (you can copy `.env.example`):
```bash
cp .env.example .env
```
Fill in your `GEMINI_API_KEY` (or `OPENAI_API_KEY`).

Start the API Server:
```bash
uvicorn main:app --reload
```
The server will run on `http://localhost:8000`. By default, it watches `AAPL, MSFT, GOOGL, AMZN, TSLA` and will start polling data.

### 2. Frontend Setup
Open a new terminal and navigate to the `frontend/` directory:
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` to view the modern dashboard.

## Multi-Agent Flow
- **Data Agent Node**: Fetches market capacity, PE Ratio, historical prices, and dividend yields via `yfinance`. Fetches latest news via `duckduckgo-search`.
- **Analysis Node**: Feeds this prompt to the LLM (Gemini or OpenAI) to act as a Wall Street quantitative analyst and provide long-term buy/hold/sell rationale.
- The workflow is orchestrated by `LangGraph` for robust state management.
