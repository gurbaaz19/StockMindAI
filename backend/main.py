from fastapi import FastAPI, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List
import asyncio
import threading

from database import init_db, get_db, Recommendation, Basket
from schemas import RecommendationResponse, BasketCreate, BasketResponse
from agent import run_agent, generate_basket
from utils import get_stock_data, get_price_history, get_exchange_rate, search_tickers

import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="StockMind AI Recommendation API")

from fastapi.middleware.cors import CORSMiddleware
frontend_url = os.getenv("FRONTEND_URL", "https://stock-mind-ai.vercel.app")
# Robust CORS: allow localhost, the specific frontend URL, and variations with/without trailing slashes
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    frontend_url.rstrip("/"),
    frontend_url.rstrip("/") + "/",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.disconnect(connection)


manager = ConnectionManager()
main_loop = None


def _format_utc_ts(dt: datetime | None) -> str:
    if not dt:
        dt = datetime.now(timezone.utc)
    ts = dt.isoformat()
    if not ts.endswith('Z'):
        ts += 'Z'
    return ts


def _rec_to_dict(rec: Recommendation) -> dict:
    return {
        "id": rec.id,
        "ticker": rec.ticker,
        "market_name": rec.market_name,
        "country_flag": rec.country_flag,
        "currency": rec.currency or "USD",
        "currency_symbol": rec.currency_symbol or "$",
        "action": rec.action,
        "confidence": rec.confidence,
        "reasoning": rec.reasoning,
        "model_name": rec.model_name or "Unknown",
        "current_price": rec.current_price,
        "timestamp": _format_utc_ts(rec.timestamp),
    }


def broadcast_recommendation(rec: Recommendation):
    payload = _rec_to_dict(rec)
    if main_loop and main_loop.is_running():
        asyncio.run_coroutine_threadsafe(
            manager.broadcast({"type": "new_recommendation", "data": payload}),
            main_loop,
        )


def _has_valid_data(prices: dict) -> bool:
    if not prices or prices.get("error"):
        return False
    price = prices.get("current_price")
    return price is not None and price > 0


def _build_recommendation(ticker: str) -> Recommendation:
    prices = get_stock_data(ticker)
    if not _has_valid_data(prices):
        raise ValueError(f"No asset data found for '{ticker}'")
    analysis = run_agent(ticker)
    return Recommendation(
        ticker=ticker,
        market_name=prices.get("market_name", prices.get("exchange", "Unknown")),
        country_flag=prices.get("country_flag", "🌐"),
        currency=prices.get("currency", "USD"),
        currency_symbol=prices.get("currency_symbol", "$"),
        action=analysis.get("action", "Hold"),
        confidence=analysis.get("confidence", 0.0),
        reasoning=analysis.get("reasoning", "No valid reason provided."),
        model_name=analysis.get("model_name", "Unknown"),
        current_price=prices.get("current_price", 0.0),
        timestamp=datetime.now(timezone.utc),
    )


scheduler = BackgroundScheduler()
WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "GOLDBEES.NS", "HDFCBANK.NS", "V"]


def background_analysis_job():
    from database import SessionLocal
    db = SessionLocal()
    try:
        for ticker in WATCHLIST:
            try:
                new_rec = _build_recommendation(ticker)
                db.add(new_rec)
                db.commit()
                db.refresh(new_rec)
                broadcast_recommendation(new_rec)
            except ValueError as e:
                print(f"[watchlist] skipping {ticker}: {e}")
                db.rollback()
            except Exception as e:
                print(f"[watchlist] error processing {ticker}: {e}")
                db.rollback()
    finally:
        db.close()


@app.on_event("startup")
def on_startup():
    global main_loop
    main_loop = asyncio.get_running_loop()
    init_db()

    scheduler.add_job(background_analysis_job, 'interval', hours=1, id='update_recommendations')
    scheduler.start()
    threading.Thread(target=background_analysis_job, daemon=True).start()


@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/recommendations")
def get_recommendations(db: Session = Depends(get_db)):
    latest_recs = []
    unique_tickers = db.query(Recommendation.ticker).distinct().all()
    for (t,) in unique_tickers:
        rec = (
            db.query(Recommendation)
            .filter(Recommendation.ticker == t)
            .order_by(Recommendation.timestamp.desc())
            .first()
        )
        if rec and (rec.current_price or 0) > 0:
            latest_recs.append(_rec_to_dict(rec))
    return latest_recs


@app.post("/api/analyze")
def analyze_single_ticker(ticker: str = Query(...), background_tasks: BackgroundTasks = None):
    """Validate the ticker has data first, then queue the LLM analysis."""
    sym = ticker.upper().strip()
    prices = get_stock_data(sym)
    if not _has_valid_data(prices):
        raise HTTPException(
            status_code=404,
            detail=f"No asset found for '{sym}'. Try the search dropdown for the correct symbol (e.g. RELIANCE.NS, BARC.L).",
        )

    def process(prefetched_prices: dict):
        from database import SessionLocal
        local_db = SessionLocal()
        try:
            analysis = run_agent(sym)
            new_rec = Recommendation(
                ticker=sym,
                market_name=prefetched_prices.get("market_name", "Unknown"),
                country_flag=prefetched_prices.get("country_flag", "🌐"),
                currency=prefetched_prices.get("currency", "USD"),
                currency_symbol=prefetched_prices.get("currency_symbol", "$"),
                action=analysis.get("action", "Hold"),
                confidence=analysis.get("confidence", 0.0),
                reasoning=analysis.get("reasoning", "No valid reason provided."),
                model_name=analysis.get("model_name", "Unknown"),
                current_price=prefetched_prices.get("current_price", 0.0),
                timestamp=datetime.now(timezone.utc),
            )
            local_db.add(new_rec)
            local_db.commit()
            local_db.refresh(new_rec)
            broadcast_recommendation(new_rec)
        except Exception as e:
            print(f"Error analyzing {sym}: {e}")
            local_db.rollback()
        finally:
            local_db.close()

    background_tasks.add_task(process, prices)
    return {
        "message": f"Analysis started for {sym}",
        "ticker": sym,
        "market_name": prices.get("market_name"),
        "country_flag": prices.get("country_flag"),
        "currency": prices.get("currency"),
        "currency_symbol": prices.get("currency_symbol"),
        "current_price": prices.get("current_price"),
    }


@app.get("/api/basket/{country}")
def get_basket(country: str, risk: str = Query("Medium")):
    return generate_basket(country, risk_tolerance=risk)


@app.get("/api/baskets", response_model=List[BasketResponse])
@app.get("/api/baskets/", response_model=List[BasketResponse], include_in_schema=False)
def get_baskets(db: Session = Depends(get_db)):
    import json
    baskets = db.query(Basket).all()
    results = []
    for b in baskets:
        try:
            items = json.loads(b.data) if b.data else []
            if not isinstance(items, list):
                items = []
        except:
            items = []
        
        # Fallback to tickers if data is empty (legacy)
        if not items and b.tickers:
            items = [{"ticker": t.strip()} for t in b.tickers.split(",") if t.strip()]
        
        results.append(
            BasketResponse(
                id=b.id,
                name=b.name,
                items=items,
                timestamp=_format_utc_ts(b.timestamp)
            )
        )
    return results


@app.post("/api/baskets", response_model=BasketResponse)
@app.post("/api/baskets/", response_model=BasketResponse, include_in_schema=False)
def create_basket(basket: BasketCreate, db: Session = Depends(get_db)):
    import json
    print(f"[API] Saving basket: {basket.name} with {len(basket.items)} items")
    db_basket = Basket(
        name=basket.name,
        tickers=",".join([i.get("ticker", "").upper().strip() for i in basket.items]),
        data=json.dumps(basket.items),
        timestamp=datetime.now(timezone.utc)
    )
    db.add(db_basket)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[API] Error saving basket: {e}")
        raise HTTPException(status_code=400, detail="Basket name might already exist or data is malformed.")
    db.refresh(db_basket)
    return BasketResponse(
        id=db_basket.id,
        name=db_basket.name,
        items=basket.items,
        timestamp=_format_utc_ts(db_basket.timestamp)
    )


@app.delete("/api/baskets/{name}")
@app.delete("/api/baskets/{name}/", include_in_schema=False)
def delete_basket(name: str, db: Session = Depends(get_db)):
    deleted = db.query(Basket).filter(Basket.name == name).delete()
    db.commit()
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"Basket '{name}' not found")
    return {"deleted": deleted, "name": name}


@app.get("/api/history/{ticker}")
def history(ticker: str, period: str = Query("1mo"), interval: str = Query("1d")):
    data = get_price_history(ticker.upper(), period=period, interval=interval)
    if data.get("error") and not data.get("history"):
        raise HTTPException(status_code=404, detail=data["error"])
    return data


@app.get("/api/forex/{base}/{quote}")
def forex(base: str, quote: str, period: str = Query("1mo")):
    data = get_exchange_rate(base, quote, period=period)
    if data.get("error"):
        raise HTTPException(status_code=400, detail=data["error"])
    return data


@app.get("/api/search")
def search(q: str = Query(..., min_length=1, max_length=64), limit: int = Query(10, ge=1, le=20)):
    return {"query": q, "results": search_tickers(q, limit=limit)}


@app.get("/api/asset")
def asset(ticker: str = Query(...)):
    """Full snapshot incl. valuation fields (target price, P/B, verdict, etc)."""
    sym = ticker.upper().strip()
    data = get_stock_data(sym)
    if not _has_valid_data(data):
        # Return 200 with error instead of 404 to allow UI to handle it gracefully
        return {"ticker": sym, "error": f"No data found for {sym}"}
    return {"ticker": sym, **data}


@app.delete("/api/recommendations/{ticker}")
def delete_recommendation(ticker: str, db: Session = Depends(get_db)):
    """Delete every stored recommendation for a ticker."""
    sym = ticker.upper().strip()
    deleted = db.query(Recommendation).filter(Recommendation.ticker == sym).delete()
    db.commit()
    if deleted == 0:
        raise HTTPException(status_code=404, detail=f"No entries for '{sym}'")
    if main_loop and main_loop.is_running():
        asyncio.run_coroutine_threadsafe(
            manager.broadcast({"type": "delete_recommendation", "data": {"ticker": sym}}),
            main_loop,
        )
    return {"deleted": deleted, "ticker": sym}
