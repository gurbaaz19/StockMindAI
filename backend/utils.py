import re
import math
import requests
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
    "MYR": "RM", "PHP": "₱", "VND": "₫", "PKR": "₨", "BDT": "৳",
    "LKR": "₨", "UAH": "₴", "RON": "lei", "BGN": "лв", "NGN": "₦",
    "KES": "KSh", "GHS": "₵", "KZT": "₸", "MAD": "dh", "QAR": "﷼",
    "KWD": "د.ك", "OMR": "﷼", "BHD": ".د.ب", "EGP": "E£", "ISK": "kr",
    "ARS": "$", "CLP": "$", "COP": "$", "PEN": "S/.", "DZD": "DA",
    "AOA": "Kz", "AMD": "֏", "AZN": "₼", "BAM": "KM", "BBD": "$",
    "BIF": "FBu", "BMD": "$", "BND": "$", "BOB": "Bs.", "BSD": "$",
    "BTN": "Nu.", "BWP": "P", "BYN": "Br", "BZD": "$", "CDF": "FC",
    "CRC": "₡", "CUP": "$", "CVE": "$", "DJF": "Fdj", "DOP": "$",
    "ERN": "Nfk", "ETB": "Br", "FJD": "$", "GEL": "₾", "GIP": "£",
    "GMD": "D", "GNF": "FG", "GTQ": "Q", "GYD": "$", "HNL": "L",
    "HTG": "G", "IQD": "ع.د", "IRR": "﷼", "JMD": "$", "JOD": "د.ا",
    "KGS": "с", "KHR": "៛", "KMF": "CF", "KPW": "₩", "KYD": "$",
    "LAK": "₭", "LBP": "ل.ل", "LRD": "$", "LSL": "L", "LYD": "ل.د",
    "MDL": "L", "MGA": "Ar", "MKD": "ден", "MMK": "K", "MNT": "₮",
    "MOP": "P", "MRU": "UM", "MUR": "₨", "MVR": "Rf", "MWK": "MK",
    "MZN": "MT", "NAD": "$", "NIO": "C$", "NPR": "₨", "PAB": "B/.",
    "PGK": "K", "PYG": "₲", "RWF": "FRw", "SBD": "$", "SCR": "₨",
    "SDG": "ج.س.", "SHP": "£", "SLL": "Le", "SOS": "Sh", "SRD": "$",
    "SSP": "£", "STN": "Db", "SYP": "£", "SZL": "L", "TJS": "ЅМ",
    "TMT": "m", "TND": "د.ت", "TOP": "T$", "TTD": "$", "TZS": "Sh",
    "UGX": "Sh", "UYU": "$", "UZS": "so'm", "VES": "Bs.S", "VUV": "Vt",
    "WST": "T", "YER": "﷼", "ZMW": "ZK", "ZWL": "$",
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
    "DZ": "🇩🇿", "AO": "🇦🇴", "AM": "🇦🇲", "AZ": "🇦🇿", "BA": "🇧🇦",
    "BB": "🇧🇧", "BI": "🇧🇮", "BM": "🇧🇲", "BN": "🇧🇳", "BO": "🇧🇴",
    "BS": "🇧🇸", "BT": "🇧🇹", "BW": "🇧🇼", "BY": "🇧🇾", "BZ": "🇧🇿",
    "CD": "🇨🇩", "CR": "🇨🇷", "CU": "🇨🇺", "CV": "🇨🇻", "DJ": "🇩🇯",
    "DO": "🇩🇴", "ER": "🇪🇷", "ET": "🇪🇹", "FJ": "🇫🇯", "GE": "🇬🇪",
    "GI": "🇬🇮", "GM": "🇬🇲", "GN": "🇬🇳", "GT": "🇬🇹", "GY": "🇬🇾",
    "HN": "🇭🇳", "HT": "🇭🇹", "IQ": "🇮🇶", "IR": "🇮🇷", "JM": "🇯🇲",
    "JO": "🇯🇴", "KG": "🇰🇬", "KH": "🇰🇭", "KM": "🇰🇲", "KP": "🇰🇵",
    "KY": "🇰🇾", "LA": "🇱🇦", "LB": "🇱🇧", "LR": "🇱🇷", "LS": "🇱🇸",
    "LY": "🇱🇾", "MD": "🇲🇩", "MG": "🇲🇬", "MK": "🇲🇰", "MM": "🇲🇲",
    "MN": "🇲🇳", "MO": "🇲🇴", "MR": "🇲🇷", "MU": "🇲🇺", "MV": "🇲🇻",
    "MW": "🇲🇼", "MZ": "🇲🇿", "NA": "🇳🇦", "NI": "🇳🇮", "NP": "🇳🇵",
    "PA": "🇵🇦", "PG": "🇵🇬", "PY": "🇵🇾", "RW": "🇷🇼", "SB": "🇸🇧",
    "SC": "🇸🇨", "SD": "🇸🇩", "SH": "🇸🇭", "SL": "🇸🇱", "SO": "🇸🇴",
    "SR": "🇸🇷", "SS": "🇸🇸", "ST": "🇸🇹", "SY": "🇸🇾", "SZ": "🇸🇿",
    "TJ": "🇹🇯", "TM": "🇹🇲", "TN": "🇹🇳", "TO": "🇹🇴", "TT": "🇹🇹",
    "TZ": "🇹🇿", "UG": "🇺🇬", "UY": "🇺🇾", "UZ": "🇺🇿", "VE": "🇻🇪",
    "VU": "🇻🇺", "WS": "🇼🇸", "YE": "🇾🇪", "ZM": "🇿🇲", "ZW": "🇿🇼",
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


def _valuation_verdict(current_price, target_mean, target_low, target_high):
    """Derive a simple over/under/fair valuation tag from analyst targets.

    Uses the analyst consensus (`targetMeanPrice`) as a proxy for intrinsic value:
      price < 90% of target  → Undervalued
      price > 110% of target → Overvalued
      otherwise              → Fairly Valued
    Falls back to the high/low band when the mean is unavailable.
    """
    if current_price is None or current_price <= 0:
        return {"verdict": "Unknown", "confidence": 0.0, "upside_pct": None}
    target = _safe_float(target_mean)
    if target and target > 0:
        upside = (target - current_price) / current_price
        if upside < -0.10:
            label = "Overvalued"
        elif upside > 0.10:
            label = "Undervalued"
        else:
            label = "Fairly Valued"
        # Confidence proxied by how tight the analyst range is
        lo, hi = _safe_float(target_low), _safe_float(target_high)
        spread_conf = 0.5
        if lo and hi and hi > lo:
            spread = (hi - lo) / target
            spread_conf = max(0.1, min(0.95, 1 - spread))
        return {"verdict": label, "confidence": round(spread_conf, 2), "upside_pct": round(upside * 100, 2)}
    return {"verdict": "Unknown", "confidence": 0.0, "upside_pct": None}


def get_stock_data(ticker: str) -> dict:
    """Fetch basic stock info, market metadata, recent price history, and valuation."""
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

        target_mean = info.get("targetMeanPrice")
        target_high = info.get("targetHighPrice")
        target_low = info.get("targetLowPrice")
        valuation = _valuation_verdict(current_price, target_mean, target_low, target_high)

        return {
            "current_price": current_price,
            "historical_prices": history,
            "market_cap": _safe_float(info.get("marketCap")),
            "pe_ratio": _safe_float(info.get("trailingPE")),
            "forward_pe": _safe_float(info.get("forwardPE")),
            "peg_ratio": _safe_float(info.get("pegRatio") or info.get("trailingPegRatio")),
            "price_to_book": _safe_float(info.get("priceToBook")),
            "price_to_sales": _safe_float(info.get("priceToSalesTrailing12Months")),
            "fifty_two_week_high": _safe_float(info.get("fiftyTwoWeekHigh")),
            "fifty_two_week_low": _safe_float(info.get("fiftyTwoWeekLow")),
            "dividend_yield": _safe_float(info.get("dividendYield")) or 0,
            "beta": _safe_float(info.get("beta")),
            # Valuation / "intrinsic value" proxy
            "target_mean_price": _safe_float(target_mean),
            "target_high_price": _safe_float(target_high),
            "target_low_price": _safe_float(target_low),
            "analyst_recommendation_mean": _safe_float(info.get("recommendationMean")),
            "analyst_recommendation_key": info.get("recommendationKey"),
            "number_of_analyst_opinions": _safe_float(info.get("numberOfAnalystOpinions")),
            "valuation_verdict": valuation["verdict"],
            "valuation_upside_pct": valuation["upside_pct"],
            "valuation_confidence": valuation["confidence"],
            # Identity
            "long_name": info.get("longName") or info.get("shortName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
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

    def _fetch_yf(b, q):
        symbol = f"{b}{q}=X"
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        return symbol, hist

    try:
        symbol, hist = _fetch_yf(base, quote)
        inverted = False
        
        # If no data, try the inverse (e.g. USDPKR instead of PKRUSD)
        if hist.empty:
            symbol, hist = _fetch_yf(quote, base)
            inverted = True
            
        if hist.empty:
            return {"error": f"No FX data for {base}/{quote}.", "base": base, "quote": quote}
            
        rate = _safe_float(hist["Close"].iloc[-1])
        if inverted and rate:
            rate = 1.0 / rate
            
        history = []
        for idx, row in hist.iterrows():
            close = _safe_float(row["Close"])
            if close is not None and close > 0:
                history.append({
                    "date": idx.strftime("%Y-%m-%d"),
                    "close": 1.0 / close if inverted else close
                })
                
        return {
            "base": base,
            "quote": quote,
            "symbol": symbol,
            "rate": rate,
            "period": period,
            "history": history,
            "inverted": inverted
        }
    except Exception as e:
        return {"error": str(e), "base": base, "quote": quote}


_YF_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"
_YF_HEADERS = {"User-Agent": "Mozilla/5.0 (StockMind/1.0)"}


def search_tickers(query: str, limit: int = 10) -> list[dict]:
    """Fuzzy ticker search via Yahoo Finance's public autocomplete.

    Returns a list of suggestions, each enriched with country/currency/flag
    derived by the same suffix resolver used elsewhere — so the dropdown
    can render `🇮🇳 HDFCBANK.NS  HDFC Bank Limited  NSE  INR` for typing "hdfc".
    """
    q = (query or "").strip()
    if not q:
        return []
    try:
        params = {
            "q": q,
            "quotesCount": max(1, min(limit, 25)),
            "newsCount": 0,
            "lang": "en-US",
        }
        r = requests.get(_YF_SEARCH_URL, params=params, headers=_YF_HEADERS, timeout=5)
        r.raise_for_status()
        data = r.json() or {}
    except Exception as e:
        print(f"search_tickers error: {e}")
        return []

    out = []
    for quote in data.get("quotes", []):
        sym = quote.get("symbol")
        if not sym:
            continue
        info = {
            "currency": quote.get("currency"),
            "country": quote.get("region"),
            "exchange": quote.get("exchDisp") or quote.get("exchange"),
        }
        market = resolve_market(sym, info)
        out.append({
            "ticker": sym,
            "name": quote.get("longname") or quote.get("shortname") or sym,
            "type": quote.get("quoteType", "EQUITY"),
            "exchange": quote.get("exchDisp") or market["exchange"],
            "country": market["country"],
            "country_flag": market["country_flag"],
            "currency": market["currency"],
            "currency_symbol": market["currency_symbol"],
        })
        if len(out) >= limit:
            break
    return out


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
