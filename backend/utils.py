import yfinance as yf
from duckduckgo_search import DDGS
from datetime import datetime, timedelta

def get_country_flag(country: str, ticker: str = "") -> str:
    if ticker.endswith(".NS") or ticker.endswith(".BO"):
        return "🇮🇳"
    
    if not country:
        return "🌐"
    
    mapping = {
        "United States": "🇺🇸",
        "India": "🇮🇳",
        "China": "🇨🇳",
        "United Kingdom": "🇬🇧",
        "Germany": "🇩🇪",
        "Japan": "🇯🇵",
        "Canada": "🇨🇦"
    }
    return mapping.get(country, "🌐")

def get_stock_data(ticker: str) -> dict:
    """Fetch basic stock info and recent price history."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        info = stock.info
        
        if hist.empty:
             return {"error": "No price history found."}

        current_price = hist['Close'].iloc[-1]
        hist_prices = hist['Close'].tolist()
        
        return {
            "current_price": current_price,
            "historical_prices": hist_prices,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "dividend_yield": info.get("dividendYield", 0),
            "market_name": info.get("exchange", "Unknown"),
            "country_flag": get_country_flag(info.get("country", ""), ticker)
        }
    except Exception as e:
        return {"error": str(e)}

def get_stock_news(ticker: str) -> list:
    """Fetch news articles using DuckDuckGo."""
    try:
        ddgs = DDGS()
        query = f"{ticker} stock news financial"
        results = ddgs.text(query, max_results=5)
        
        news_list = []
        for r in results:
            news_list.append({
                "title": r.get('title'),
                "body": r.get('body'),
                "url": r.get('href')
            })
        return news_list
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []
