from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from typing import List

from database import init_db, get_db, Recommendation
from schemas import RecommendationResponse, RecommendationCreate
from agent import run_agent, get_stock_data

app = FastAPI(title="StockMind AI Recommendation API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup APScheduler
scheduler = BackgroundScheduler()

# Predefined watch list to analyze hourly
WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "GOLDBEES.NS", "HDFCBANK.NS", "V"]

def background_analysis_job():
    """Scheduled job to re-analyze stocks and cache results."""
    from database import SessionLocal
    db = SessionLocal()
    try:
        for ticker in WATCHLIST:
            # Run LangGraph analysis
            analysis = run_agent(ticker)
            
            # Get current price
            prices = get_stock_data(ticker)
            current_price = prices.get("current_price", 0.0)
            
            # Save to DB
            new_rec = Recommendation(
                ticker=ticker,
                market_name=prices.get("market_name", "Unknown"),
                country_flag=prices.get("country_flag", "🌐"),
                action=analysis.get("action", "Hold"),
                confidence=analysis.get("confidence", 0.0),
                reasoning=analysis.get("reasoning", "No valid reason provided."),
                current_price=current_price,
                timestamp=datetime.utcnow()
            )
            db.add(new_rec)
            db.commit()
    except Exception as e:
        print(f"Error in background job: {e}")
    finally:
        db.close()

import threading

@app.on_event("startup")
def on_startup():
    init_db()
    
    # Start the scheduler to refresh every 1 hour
    scheduler.add_job(background_analysis_job, 'interval', hours=1, id='update_recommendations')
    scheduler.start()
    
    # Trigger immediately in a separate thread so it doesn't block server startup
    threading.Thread(target=background_analysis_job, daemon=True).start()

@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()

@app.get("/api/recommendations", response_model=List[RecommendationResponse])
def get_recommendations(db: Session = Depends(get_db)):
    """Fetch the latest recommendation for each ticker in the watchlist."""
    latest_recs = []
    for ticker in WATCHLIST:
        rec = db.query(Recommendation).filter(Recommendation.ticker == ticker).order_by(Recommendation.timestamp.desc()).first()
        if rec:
            latest_recs.append(rec)
    return latest_recs

@app.post("/api/analyze/{ticker}", response_model=RecommendationResponse)
def analyze_single_ticker(ticker: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger analysis for a single ticker explicitly."""
    # Run immediate rather than schedule to show result in real time
    analysis = run_agent(ticker.upper())
    prices = get_stock_data(ticker.upper())
    
    new_rec = Recommendation(
        ticker=ticker.upper(),
        market_name=prices.get("market_name", "Unknown"),
        country_flag=prices.get("country_flag", "🌐"),
        action=analysis.get("action", "Hold"),
        confidence=analysis.get("confidence", 0.0),
        reasoning=analysis.get("reasoning", "Analysis failed"),
        current_price=prices.get("current_price", 0.0),
    )
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    return new_rec
