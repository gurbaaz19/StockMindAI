from fastapi import FastAPI, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect, Query
from sqlalchemy.orm import Session
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List
import asyncio
import threading

from database import init_db, get_db, Recommendation
from schemas import RecommendationResponse
from agent import run_agent, generate_basket
from utils import get_stock_data, get_price_history, get_exchange_rate

app = FastAPI(title="StockMind AI Recommendation API")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "current_price": rec.current_price,
        "timestamp": rec.timestamp.isoformat() if rec.timestamp else str(datetime.utcnow()),
    }


def broadcast_recommendation(rec: Recommendation):
    payload = _rec_to_dict(rec)
    if main_loop and main_loop.is_running():
        asyncio.run_coroutine_threadsafe(
            manager.broadcast({"type": "new_recommendation", "data": payload}),
            main_loop,
        )


def _build_recommendation(ticker: str) -> Recommendation:
    analysis = run_agent(ticker)
    prices = get_stock_data(ticker)
    return Recommendation(
        ticker=ticker,
        market_name=prices.get("market_name", prices.get("exchange", "Unknown")),
        country_flag=prices.get("country_flag", "🌐"),
        currency=prices.get("currency", "USD"),
        currency_symbol=prices.get("currency_symbol", "$"),
        action=analysis.get("action", "Hold"),
        confidence=analysis.get("confidence", 0.0),
        reasoning=analysis.get("reasoning", "No valid reason provided."),
        current_price=prices.get("current_price", 0.0),
        timestamp=datetime.utcnow(),
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
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
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


@app.get("/api/recommendations", response_model=List[RecommendationResponse])
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
        if rec:
            latest_recs.append(rec)
    return latest_recs


@app.post("/api/analyze/{ticker}")
def analyze_single_ticker(ticker: str, background_tasks: BackgroundTasks):
    def process():
        from database import SessionLocal
        local_db = SessionLocal()
        try:
            new_rec = _build_recommendation(ticker.upper())
            local_db.add(new_rec)
            local_db.commit()
            local_db.refresh(new_rec)
            broadcast_recommendation(new_rec)
        except Exception as e:
            print(f"Error analyzing {ticker}: {e}")
            local_db.rollback()
        finally:
            local_db.close()

    background_tasks.add_task(process)
    return {"message": f"Analysis started for {ticker}"}


@app.get("/api/basket/{country}")
def get_basket(country: str):
    return generate_basket(country)


@app.get("/api/history/{ticker}")
def history(ticker: str, period: str = Query("1mo"), interval: str = Query("1d")):
    return get_price_history(ticker.upper(), period=period, interval=interval)


@app.get("/api/forex/{base}/{quote}")
def forex(base: str, quote: str, period: str = Query("1mo")):
    return get_exchange_rate(base, quote, period=period)
