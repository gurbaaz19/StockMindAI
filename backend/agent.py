import json
import os
from dotenv import load_dotenv
from typing import Dict, TypedDict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage, HumanMessage

from schemas import AgentState
from utils import get_stock_data, get_stock_news

class GraphState(TypedDict):
    ticker: str
    prices: Dict[str, Any]
    news: list[Dict[str, str]]
    recommendation: Dict[str, Any]

def fetch_data_node(state: GraphState):
    """Fetches market data and news for the ticker."""
    ticker = state["ticker"]
    prices = get_stock_data(ticker)
    news = get_stock_news(ticker)
    return {"prices": prices, "news": news}

def analyze_node(state: GraphState):
    """Analyzes the collected data using Gemini or OpenAI."""
    ticker = state["ticker"]
    prices = state.get("prices", {})
    news_items = state.get("news", [])
    
    # Format news
    news_text = "\n".join([f"- {n['title']}: {n['body']}" for n in news_items])
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert Wall Street quantitative analyst and long-term investor. "
                   "Analyze the provided stock data and news and return a final recommendation in JSON format. "
                   "The JSON must have this strict schema: "
                   "{{\"action\": \"Buy\" | \"Hold\" | \"Sell\", \"confidence\": float (0.0 to 1.0), \"reasoning\": \"string explaining long-term view\"}}"),
        ("user", "Ticker: {ticker}\n\nPrice Data: {prices}\n\nRecent News:\n{news_text}")
    ])
    
    load_dotenv()
    api_key_gemini = os.environ.get("GEMINI_API_KEY", "")
    api_key_openai = os.environ.get("OPENAI_API_KEY", "")
    
    llm = None
    if api_key_gemini:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key_gemini)
    elif api_key_openai:
         llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key_openai)
    else:
        # Fallback dummy if no key provided just to not crash the server tests
        return {"recommendation": {"action": "Hold", "confidence": 0.5, "reasoning": "No API Key provided to perform analysis."}}

    chain = prompt | llm
    try:
        response = chain.invoke({
            "ticker": ticker,
            "prices": json.dumps(prices),
            "news_text": news_text
        })
        
        # Parse JSON
        content = response.content
        # sometimes LLM replies with ```json ... ``` blocks
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        data = json.loads(content)
        return {"recommendation": data}
    except Exception as e:
        print(f"Error during analysis: {e}")
        return {"recommendation": {"action": "Hold", "confidence": 0.0, "reasoning": f"Analysis failed: {str(e)}" }}

# Build the Graph
workflow = StateGraph(GraphState)

workflow.add_node("fetch_data", fetch_data_node)
workflow.add_node("analyze", analyze_node)

workflow.set_entry_point("fetch_data")
workflow.add_edge("fetch_data", "analyze")
workflow.add_edge("analyze", END)

app = workflow.compile()

def run_agent(ticker: str) -> dict:
    """Entry point to run the LangGraph workflow."""
    initial_state = {"ticker": ticker, "prices": {}, "news": [], "recommendation": {}}
    try:
        result = app.invoke(initial_state)
        return result.get("recommendation", {})
    except Exception as e:
        print(f"Error running agent for {ticker}: {e}")
        return {"action": "Hold", "confidence": 0.0, "reasoning": "Agent workflow failed."}
