import json
import os
import re
from dotenv import load_dotenv
from typing import Dict, TypedDict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from utils import get_stock_data, get_stock_news


class GraphState(TypedDict):
    ticker: str
    prices: Dict[str, Any]
    news: list[Dict[str, str]]
    recommendation: Dict[str, Any]


def _extract_json(content: str) -> dict:
    """Robustly extract a JSON object from an LLM response.

    Handles fenced code blocks, leading prose, trailing text after the JSON,
    and unbalanced surrounding whitespace.
    """
    if not content:
        raise ValueError("Empty LLM response")

    text = content.strip()

    # Strip ```json ... ``` or ``` ... ``` fences if present.
    fence = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()

    # Direct parse.
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # raw_decode tolerates trailing garbage after the first JSON value.
    decoder = json.JSONDecoder()
    for start in range(len(text)):
        ch = text[start]
        if ch not in "{[":
            continue
        try:
            obj, _ = decoder.raw_decode(text[start:])
            return obj
        except json.JSONDecodeError:
            continue

    raise ValueError(f"Could not extract JSON. First 200 chars: {text[:200]!r}")


def _make_llm():
    load_dotenv()
    api_key_gemini = os.environ.get("GEMINI_API_KEY", "")
    api_key_openai = os.environ.get("OPENAI_API_KEY", "")
    if api_key_gemini:
        # response_mime_type makes Gemini emit raw JSON instead of prose+JSON.
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key_gemini,
            generation_config={"response_mime_type": "application/json"},
        )
    if api_key_openai:
        # OpenAI JSON mode for the same reason.
        return ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=api_key_openai,
            model_kwargs={"response_format": {"type": "json_object"}},
        )
    return None


def fetch_data_node(state: GraphState):
    ticker = state["ticker"]
    prices = get_stock_data(ticker)
    news = get_stock_news(ticker)
    return {"prices": prices, "news": news}


def analyze_node(state: GraphState):
    ticker = state["ticker"]
    prices = state.get("prices", {})
    news_items = state.get("news", [])

    news_text = "\n".join([f"- {n['title']}: {n['body']}" for n in news_items if n.get("title")])

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert Wall Street quantitative analyst and long-term investor. "
         "Analyze the provided stock data and news and return a final recommendation. "
         "Respond ONLY with a single valid JSON object — no prose, no code fences. "
         "Schema: {{\"action\": \"Buy\" | \"Hold\" | \"Sell\", \"confidence\": float between 0.0 and 1.0, \"reasoning\": \"string explaining long-term view\"}}"),
        ("user", "Ticker: {ticker}\n\nPrice Data: {prices}\n\nRecent News:\n{news_text}"),
    ])

    llm = _make_llm()
    if llm is None:
        return {"recommendation": {
            "action": "Hold", "confidence": 0.5,
            "reasoning": "No API Key provided to perform analysis."
        }}

    chain = prompt | llm
    last_err = None
    for attempt in range(2):
        try:
            response = chain.invoke({
                "ticker": ticker,
                "prices": json.dumps(prices, default=str),
                "news_text": news_text,
            })
            data = _extract_json(response.content)
            # Normalise required fields
            return {"recommendation": {
                "action": str(data.get("action", "Hold")),
                "confidence": float(data.get("confidence", 0.0)),
                "reasoning": str(data.get("reasoning", "")),
            }}
        except Exception as e:
            last_err = e
            print(f"[analyze {ticker}] attempt {attempt + 1} failed: {e}")

    return {"recommendation": {
        "action": "Hold", "confidence": 0.0,
        "reasoning": f"Analysis failed: {last_err}",
    }}


workflow = StateGraph(GraphState)
workflow.add_node("fetch_data", fetch_data_node)
workflow.add_node("analyze", analyze_node)
workflow.set_entry_point("fetch_data")
workflow.add_edge("fetch_data", "analyze")
workflow.add_edge("analyze", END)
app = workflow.compile()


def run_agent(ticker: str) -> dict:
    initial_state = {"ticker": ticker, "prices": {}, "news": [], "recommendation": {}}
    try:
        result = app.invoke(initial_state)
        return result.get("recommendation", {})
    except Exception as e:
        print(f"Error running agent for {ticker}: {e}")
        return {"action": "Hold", "confidence": 0.0, "reasoning": "Agent workflow failed."}


def generate_basket(market: str, risk_tolerance: str = "Medium") -> dict:
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are an expert global equity analyst and portfolio manager. The user wants a curated basket of top 3-5 high-quality assets (stocks, ETFs, or Mutual Funds) specifically listed in or focused on '{market}' for a long term hold portfolio. "
         "Risk Tolerance: {risk_tolerance}. Adjust the asset selection and weights accordingly (e.g., higher weights to stable large-caps for Low risk, higher weights to growth/mid-caps for High risk). "
         "Always use the correct yfinance ticker suffix for the local exchange (e.g. .NS for NSE India, .BO for BSE India, .L for London, .DE for XETRA, .T for Tokyo, .HK for Hong Kong, .AX for ASX, .TO for TSX, .SA for B3 Brazil) so the symbol resolves on Yahoo Finance. "
         "Special case for 'Indian Mutual Funds': Use Yahoo Finance symbols for Indian Mutual Funds (typically ending in .BO or .NS, e.g., 0P0000XW8F.BO) or well-known Indian ETFs like NIFTYBEES.NS, GOLDBEES.NS, JUNIORBEES.NS. "
         "Respond ONLY with a single valid JSON object — no prose, no code fences. "
         "Schema: {{\"basket\": [{{\"ticker\": \"string\", \"name\": \"string\", \"currency\": \"3-letter ISO code\", \"reasoning\": \"why this is a good hold\", \"percentage_weight\": int}}]}} "
         "Ensure 'percentage_weight' across all items sums to exactly 100."),
        ("user", "Market/Country: {market}\nRisk Tolerance: {risk_tolerance}"),
    ])

    llm = _make_llm()
    if llm is None:
        return {"basket": []}

    chain = prompt | llm
    try:
        response = chain.invoke({"market": market, "risk_tolerance": risk_tolerance})
        return _extract_json(response.content)
    except Exception as e:
        print(f"Error generating basket: {e}")
        return {"basket": []}
