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


def _make_llm(prefer_openai=False):
    load_dotenv()
    api_key_gemini = os.environ.get("GEMINI_API_KEY", "")
    api_key_openai = os.environ.get("OPENAI_API_KEY", "")
    
    if prefer_openai and api_key_openai:
        return ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=api_key_openai,
            model_kwargs={"response_format": {"type": "json_object"}},
        ), "GPT-4o Mini"
    
    if api_key_gemini:
        return ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key_gemini,
            convert_system_message_to_human=True,
        ), "Gemini 2.0 Flash"
    
    if api_key_openai:
        return ChatOpenAI(
            model="gpt-4o-mini",
            openai_api_key=api_key_openai,
            model_kwargs={"response_format": {"type": "json_object"}},
        ), "GPT-4o Mini"
    return None, None


def _invoke_with_fallback(prompt, inputs):
    """Try Gemini first, then fallback to OpenAI on failure. Returns (response, model_name)."""
    llm_gemini, name_gemini = _make_llm(prefer_openai=False)
    if llm_gemini:
        try:
            chain = prompt | llm_gemini
            return chain.invoke(inputs), name_gemini
        except Exception as e:
            print(f"[agent] Gemini failed or exhausted: {e}. Falling back to OpenAI...")
    
    llm_openai, name_openai = _make_llm(prefer_openai=True)
    if llm_openai:
        chain = prompt | llm_openai
        return chain.invoke(inputs), name_openai
    
    raise ValueError("No LLM available (Check Gemini/OpenAI API Keys)")


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
         "Analyze the provided stock data (including Intrinsic Value, Valuation metrics, and analyst targets), recent news, and price history to return a final recommendation. "
         "CRITICAL: Give significant weight to the 'valuation_verdict' and 'valuation_upside_pct' provided in the price data. If a stock is fundamentally overvalued, justify a Buy recommendation with very strong news/growth catalysts; otherwise, default to Hold or Sell. "
         "Respond ONLY with a single valid JSON object — no prose, no code fences. "
         "Schema: {{\"action\": \"Buy\" | \"Hold\" | \"Sell\", \"confidence\": float between 0.0 and 1.0, \"reasoning\": \"string explaining long-term view, explicitly mentioning valuation and news balance\"}}"),
        ("user", "Ticker: {ticker}\n\nFull Data Snapshot: {prices}\n\nRecent News:\n{news_text}"),
    ])

    try:
        response, model_name = _invoke_with_fallback(prompt, {
            "ticker": ticker,
            "prices": json.dumps(prices, default=str),
            "news_text": news_text,
        })
        data = _extract_json(response.content)
        reasoning = str(data.get("reasoning", ""))
        if model_name:
            reasoning += f"\n\n(Model: {model_name})"
            
        return {"recommendation": {
            "action": str(data.get("action", "Hold")),
            "confidence": float(data.get("confidence", 0.0)),
            "reasoning": reasoning,
            "model_name": model_name
        }}
    except Exception as e:
        print(f"[analyze {ticker}] error: {e}")
        return {"recommendation": {
            "action": "Hold", "confidence": 0.0,
            "reasoning": f"Analysis failed: {e}",
            "model_name": "Error"
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
         "You are an expert global equity analyst and portfolio manager. "
         "CRITICAL for 'Indian Mutual Funds': You MUST ONLY select from the following real Indian Mutual Funds and ETFs, matching them to the risk profile:\n"
         "- NIFTYBEES.NS (Nippon India Nifty 50 ETF) - Low Risk\n"
         "- GOLDBEES.NS (Nippon India Gold ETF) - Low Risk\n"
         "- JUNIORBEES.NS (Nippon India Nifty Next 50 ETF) - Medium Risk\n"
         "- MON100.NS (Motilal Oswal Nasdaq 100 ETF) - High Risk\n"
         "- 0P0000XVUF.BO (HDFC Small Cap Fund) - High Risk\n"
         "- 0P0000YWL1.BO (Parag Parikh Flexi Cap Fund) - Medium Risk\n"
         "- 0P0000XW8F.BO (Quant Small Cap Fund) - High Risk\n"
         "- 0P0000XVWA.BO (SBI Contra Fund) - High Risk\n"
         "- 0P0000XUZE.BO (ICICI Prudential Bluechip Fund) - Low/Medium Risk\n"
         "- 0P0000XWAA.BO (Kotak Emerging Equity Fund) - High Risk\n"
         "DO NOT return individual stocks (like RELIANCE.NS). "
         "For any other market, curated a basket of top 3-5 high-quality assets listed in or focused on '{market}' for a long term hold portfolio. "
         "Risk Tolerance: {risk_tolerance}. Adjust asset selection and weights accordingly. "
         "Always use correct yfinance suffixes (.NS, .BO, .L, .DE, .T, .HK, .AX, .TO, .SA). "
         "Respond ONLY with a single valid JSON object. "
         "Schema: {{\"basket\": [{{\"ticker\": \"string\", \"name\": \"string\", \"currency\": \"3-letter ISO code\", \"reasoning\": \"why this is a good hold\", \"percentage_weight\": int}}]}} "
         "Ensure 'percentage_weight' sums to exactly 100."),
        ("user", "Market: {market}\nRisk Tolerance: {risk_tolerance}"),
    ])

    try:
        response, model_name = _invoke_with_fallback(prompt, {"market": market, "risk_tolerance": risk_tolerance})
        data = _extract_json(response.content)
        basket_items = data.get("basket", [])
        for item in basket_items:
            if "reasoning" in item:
                item["reasoning"] += f"\n\n(Analyzed by {model_name})"
        return {"basket": basket_items}
    except Exception as e:
        print(f"Error generating basket: {e}")
        return {"basket": []}
