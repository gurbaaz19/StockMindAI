from pydantic import BaseModel
from typing import Optional, List
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
    model_name: str = "Unknown"
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
    model_name: str = "Unknown"
    current_price: float
    timestamp: datetime

    class Config:
        from_attributes = True


class BasketCreate(BaseModel):
    name: str
    items: List[dict]


class BasketResponse(BaseModel):
    id: int
    name: str
    items: List[dict]
    timestamp: datetime

    class Config:
        from_attributes = True


class AgentState(BaseModel):
    ticker: str
    news: list[dict] = []
    prices: dict = {}
    recommendation: Optional[dict] = None
