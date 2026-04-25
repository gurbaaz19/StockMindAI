from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecommendationCreate(BaseModel):
    ticker: str
    market_name: str
    country_flag: str
    currency: str = "USD"
    currency_symbol: str = "$"
    action: str
    confidence: float
    reasoning: str
    current_price: float


class RecommendationResponse(BaseModel):
    id: int
    ticker: str
    market_name: str
    country_flag: str
    currency: str = "USD"
    currency_symbol: str = "$"
    action: str
    confidence: float
    reasoning: str
    current_price: float
    timestamp: datetime

    class Config:
        from_attributes = True


class AgentState(BaseModel):
    ticker: str
    news: list[dict] = []
    prices: dict = {}
    recommendation: Optional[dict] = None
