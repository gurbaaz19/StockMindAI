import re
import math
import yfinance as yf
from duckduckgo_search import DDGS

VALID_PERIODS = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
VALID_INTERVALS = {"1m", "5m", "15m", "30m", "60m", "1h", "1d", "1wk", "1mo"}

# Currency code -> display symbol
CURRENCY_SYMBOL = {
    "USD": "$", "EUR": "€", "GBP": "£", "GBp": "p", "JPY": "¥", "CNY": "¥",
    "INR": "₹", "HKD": "HK$", "AUD": "A$", "NZD": "NZ$", "CAD": "C$",
    "CHF": "CHF", "SGD": "S$", "KRW": "₩", "TWD": "NT$", "BRL": "R$",
    "MXN": "Mex$", "ZAR": "R", "ILS": "₪", "SAR": "﷼", "AED": "د.إ",
    "SEK": "kr", "NOK": "kr", "DKK": "kr", "PLN": "zł", "CZK": "Kč",
    "HUF": "Ft", "TRY": "₺", "RUB": "₽", "THB": "฿", "IDR": "Rp",
    "MYR": "RM", "PHP": "₱", "VND": "₫",
}

COUNTRY_FLAG = {
    "US": "🇺🇸", "United States": "🇺🇸",
    "IN": "🇮🇳", "India": "🇮🇳",
    "GB": "🇬🇧", "United Kingdom": "🇬🇧",
    "DE": "🇩🇪", "Germany": "🇩🇪",
    "FR": "🇫🇷", "France": "🇫🇷",
    "NL": "🇳🇱", "Netherlands": "🇳🇱",
    "IT": "🇮🇹", "Italy": "🇮🇹",
    "ES": "🇪🇸", "Spain": "🇪🇸",
    "CH": "🇨🇭", "Switzerland": "🇨🇭",
    "JP": "🇯🇵", "Japan": "🇯🇵",
    "CN": "🇨🇳", "China": "🇨🇳",
    "HK": "🇭🇰", "Hong Kong": "🇭🇰",
    "KR": "🇰🇷", "South Korea": "🇰🇷",
    "TW": "🇹🇼", "Taiwan": "🇹🇼",
    "AU": "🇦🇺", "Australia": "🇦🇺",
    "NZ": "🇳🇿", "New Zealand": "🇳🇿",
    "CA": "🇨🇦", "Canada": "🇨🇦",
    "BR": "🇧🇷", "Brazil": "🇧🇷",
    "MX": "🇲🇽", "Mexico": "🇲🇽",
    "ZA": "🇿🇦", "South Africa": "🇿🇦",
    "IL": "🇮🇱", "Israel": "🇮🇱",
    "SA": "🇸🇦", "Saudi Arabia": "🇸🇦",
    "AE": "🇦🇪", "United Arab Emirates": "🇦🇪",
    "SE": "🇸🇪", "Sweden": "🇸🇪",
    "NO": "🇳🇴", "Norway": "🇳🇴",
    "DK": "🇩🇰", "Denmark": "🇩🇰",
    "FI": "🇫🇮", "Finland": "🇫🇮",
    "SG": "🇸🇬", "Singapore": "🇸🇬",
    "TR": "🇹🇷", "Turkey": "🇹🇷",
    "RU": "🇷🇺", "Russia": "🇷🇺",
    "TH": "🇹🇭", "Thailand": "🇹🇭",
    "ID": "🇮🇩", "Indonesia": "🇮🇩",
    "MY": "🇲🇾", "Malaysia": "🇲🇾",
    "PH": "🇵🇭", "Philippines": "🇵🇭",
    "VN": "🇻🇳", "Vietnam": "🇻🇳",
}

# Suffix -> (country_code, currency, exchange_label)
SUFFIX_MAP = {
    "NS":  ("IN", "INR", "NSE"),
    "BO":  ("IN", "INR", "BSE"),
    "L":   ("GB", "GBP", "LSE"),
    "DE":  ("DE", "EUR", "XETRA"),
    "F":   ("DE", "EUR", "Frankfurt"),
    "BE":  ("DE", "EUR", "Berlin"),
    "MU":  ("DE", "EUR", "Munich"),
    "PA":  ("FR", "EUR", "Euronext Paris"),
    "AS":  ("NL", "EUR", "Euronext Amsterdam"),
    "BR":  ("BE", "EUR", "Euronext Brussels"),
    "LS":  ("PT", "EUR", "Euronext Lisbon"),
    "MI":  ("IT", "EUR", "Borsa Italiana"),
    "MC":  ("ES", "EUR", "BME"),
    "VI":  ("AT", "EUR", "Vienna"),
    "IR":  ("IE", "EUR", "Euronext Dublin"),
    "AT":  ("GR", "EUR", "Athens"),
    "SW":  ("CH", "CHF", "SIX Swiss"),
    "VX":  ("CH", "CHF", "SIX Swiss"),
    "T":   ("JP", "JPY", "Tokyo"),
    "HK":  ("HK", "HKD", "HKEX"),
    "SS":  ("CN", "CNY", "Shanghai"),
    "SZ":  ("CN", "CNY", "Shenzhen"),
    "KS":  ("KR", "KRW", "KRX"),
    "KQ":  ("KR", "KRW", "KOSDAQ"),
    "TW":  ("TW", "TWD", "TWSE"),
    "TWO": ("TW", "TWD", "TPEx"),
    "AX":  ("AU", "AUD", "ASX"),
    "NZ":  ("NZ", "NZD", "NZX"),
    "TO":  ("CA", "CAD", "TSX"),
    "V":   ("CA", "CAD", "TSX Venture"),
    "CN":  ("CA", "CAD", "CSE"),
    "NE":  ("CA", "CAD", "NEO"),
    "SA":  ("BR", "BRL", "B3"),
    "MX":  ("MX", "MXN", "BMV"),
    "JO":  ("ZA", "ZAR", "JSE"),
    "ST":  ("SE", "SEK", "Stockholm"),
    "HE":  ("FI", "EUR", "Helsinki"),
    "CO":  ("DK", "DKK", "Copenhagen"),
    "OL":  ("NO", "NOK", "Oslo"),
    "IS":  ("IL", "ILS", "TASE"),
    "TA":  ("IL", "ILS", "TASE"),
    "SR":  ("SA", "SAR", "Tadawul"),
    "IC":  ("IS", "ISK", "Iceland"),
    "WA":  ("PL", "PLN", "Warsaw"),
    "PR":  ("CZ", "CZK", "Prague"),
    "BD":  ("HU", "HUF", "Budapest"),
    "IS_TR": ("TR", "TRY", "Borsa Istanbul"),
    "SI":  ("SG", "SGD", "SGX"),
    "BK":  ("TH", "THB", "SET"),
    "JK":  ("ID", "IDR", "IDX"),
    "KL":  ("MY", "MYR", "Bursa Malaysia"),
    "PS":  ("PH", "PHP", "PSE"),
    "VN":  ("VN", "VND", "HOSE"),
}


def _flag(code_or_name: str) -> str:
    if not code_or_name:
        return "🌐"
    return COUNTRY_FLAG.get(code_or_name, "🌐")


def _symbol(currency: str) -> str:
    if not currency:
        return ""
    return CURRENCY_SYMBOL.get(currency, currency + " ")


def resolve_market(ticker: str, info: dict | None = None) -> dict:
    """Resolve country, currency, currency symbol, exchange and flag for a ticker.

    Order of precedence:
      1. Forex pair (EURUSD=X) — derive base/quote from the symbol itself.
      2. Crypto (BTC-USD) — quote currency comes from the suffix.
      3. Suffix table for international exchanges.
      4. Fallback to yfinance `info` (currency + country) — covers bare US tickers.
    """
    info = info or {}
    t = (ticker or "").upper().strip()

    # FX pair: e.g. EURUSD=X, USDJPY=X
    fx = re.match(r"^([A-Z]{3})([A-Z]{3})=X$", t)
    if fx:
        base, quote = fx.group(1), fx.group(2)
        return {
            "country": "FX",
            "country_flag": "💱",
            "currency": quote,
            "currency_symbol": _symbol(quote),
            "exchange": f"FX {base}/{quote}",
        }

    # Crypto: e.g. BTC-USD, ETH-EUR
    crypto = re.match(r"^[A-Z0-9]+-([A-Z]{3})$", t)
    if crypto:
        quote = crypto.group(1)
        return {
            "country": "Crypto",
            "country_flag": "🪙",
            "currency": quote,
            "currency_symbol": _symbol(quote),
            "exchange": "Crypto",
        }

    # Suffix lookup
    if "." in t:
        suffix = t.rsplit(".", 1)[1]
        if suffix in SUFFIX_MAP:
            country, currency, exchange = SUFFIX_MAP[suffix]
            return {
                "country": country,
                "country_flag": _flag(country),
                "currency": currency,
                "currency_symbol": _symbol(currency),
                "exchange": exchange,
            }

    # Fallback to yfinance info (covers US tickers without suffix)
    currency = (info.get("currency") or "USD").upper()
    country = info.get("country") or "United States"
    exchange = info.get("exchange") or "NMS"
    return {
        "country": country,
        "country_flag": _flag(country),
        "currency": currency,
        "currency_symbol": _symbol(currency),
        "exchange": exchange,
    }


def _safe_float(v):
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def get_stock_data(ticker: str) -> dict:
    """Fetch basic stock info, market metadata, and recent price history."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        try:
            info = stock.info or {}
        except Exception:
            info = {}

        market = resolve_market(ticker, info)

        if hist.empty:
            return {"error": "No price history found.", **market}

        current_price = _safe_float(hist["Close"].iloc[-1]) or 0.0
        history = [
            {"date": idx.strftime("%Y-%m-%d"), "close": _safe_float(row["Close"])}
            for idx, row in hist.iterrows()
            if _safe_float(row["Close"]) is not None
        ]

        return {
            "current_price": current_price,
            "historical_prices": history,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "dividend_yield": info.get("dividendYield", 0),
            "market_name": market["exchange"],
            **market,
        }
    except Exception as e:
        return {"error": str(e), **resolve_market(ticker, {})}


def get_price_history(ticker: str, period: str = "1mo", interval: str = "1d") -> dict:
    """Return OHLCV history for a ticker. Period/interval are validated."""
    if period not in VALID_PERIODS:
        return {"error": f"Invalid period '{period}'. Allowed: {sorted(VALID_PERIODS)}"}
    if interval not in VALID_INTERVALS:
        return {"error": f"Invalid interval '{interval}'."}
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)
        if hist.empty:
            return {"error": "No price history found.", "ticker": ticker, "history": []}
        try:
            info = stock.info or {}
        except Exception:
            info = {}
        market = resolve_market(ticker, info)
        rows = []
        for idx, row in hist.iterrows():
            close = _safe_float(row["Close"])
            if close is None:
                continue
            rows.append({
                "date": idx.strftime("%Y-%m-%d %H:%M") if interval.endswith(("m", "h")) else idx.strftime("%Y-%m-%d"),
                "open": _safe_float(row["Open"]),
                "high": _safe_float(row["High"]),
                "low": _safe_float(row["Low"]),
                "close": close,
                "volume": _safe_float(row["Volume"]),
            })
        return {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "history": rows,
            **market,
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker, "history": []}


def get_exchange_rate(base: str, quote: str, period: str = "1mo") -> dict:
    """Return the latest FX rate plus history for base->quote."""
    base = (base or "").upper().strip()
    quote = (quote or "").upper().strip()
    if not (re.match(r"^[A-Z]{3}$", base) and re.match(r"^[A-Z]{3}$", quote)):
        return {"error": "Currencies must be 3-letter ISO codes."}
    if base == quote:
        return {
            "base": base, "quote": quote, "rate": 1.0,
            "history": [], "period": period,
        }
    if period not in VALID_PERIODS:
        return {"error": f"Invalid period '{period}'."}
    try:
        symbol = f"{base}{quote}=X"
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        if hist.empty:
            return {"error": f"No FX data for {symbol}.", "base": base, "quote": quote}
        rate = _safe_float(hist["Close"].iloc[-1])
        history = [
            {"date": idx.strftime("%Y-%m-%d"), "close": _safe_float(row["Close"])}
            for idx, row in hist.iterrows()
            if _safe_float(row["Close"]) is not None
        ]
        return {
            "base": base,
            "quote": quote,
            "symbol": symbol,
            "rate": rate,
            "period": period,
            "history": history,
        }
    except Exception as e:
        return {"error": str(e), "base": base, "quote": quote}


def get_stock_news(ticker: str) -> list:
    """Fetch news articles using DuckDuckGo."""
    try:
        ddgs = DDGS()
        query = f"{ticker} stock news financial"
        results = ddgs.text(query, max_results=5)
        return [
            {"title": r.get("title"), "body": r.get("body"), "url": r.get("href")}
            for r in results
        ]
    except Exception as e:
        print(f"Error fetching news for {ticker}: {e}")
        return []
