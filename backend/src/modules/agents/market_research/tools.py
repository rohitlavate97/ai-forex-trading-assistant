from typing import Dict, Any, Optional
from pydantic_ai import RunContext

from src.modules.market_data.service import MarketDataService


async def get_currency_overview(
    ctx: RunContext[None], symbol: str
) -> Dict[str, Any]:
    """
    Fetch the current live price overview for a currency pair, including bid and ask.

    Args:
        ctx: RunContext (no specific dependency required).
        symbol: Currency pair symbol (e.g., "EUR/USD").
    """
    service = MarketDataService()
    live_price = await service.get_live_price(symbol)
    
    if not live_price:
        return {"error": f"No live price data available for {symbol}"}
        
    return {
        "symbol": symbol,
        "price": live_price.get("price"),
        "bid": live_price.get("bid"),
        "ask": live_price.get("ask"),
        "timestamp": live_price.get("timestamp")
    }


async def get_volatility_summary(
    ctx: RunContext[None], symbol: str, limit: int = 50
) -> Dict[str, Any]:
    """
    Calculate the recent volatility for a currency pair based on its tick history.
    Returns the high, low, average price, and price variance (spread between high and low).

    Args:
        ctx: RunContext (no specific dependency required).
        symbol: Currency pair symbol (e.g., "EUR/USD").
        limit: Number of recent ticks to evaluate (max 100).
    """
    service = MarketDataService()
    history = await service.get_price_history(symbol, limit=limit)
    
    if not history:
        return {"error": f"No history available to calculate volatility for {symbol}"}
        
    prices = [tick["price"] for tick in history if "price" in tick]
    
    if not prices:
        return {"error": f"No valid price ticks found for {symbol}"}
        
    high = max(prices)
    low = min(prices)
    avg = sum(prices) / len(prices)
    variance = high - low
    
    return {
        "symbol": symbol,
        "high": high,
        "low": low,
        "average": avg,
        "variance_pips": variance * 10000, # Assuming standard forex pip multiplier for display
        "ticks_analyzed": len(prices)
    }


async def get_trend_summary(
    ctx: RunContext[None], symbol: str, limit: int = 50
) -> Dict[str, Any]:
    """
    Evaluate the short-term price trend for a currency pair.
    Compares the oldest available tick in the window to the newest to determine direction.

    Args:
        ctx: RunContext (no specific dependency required).
        symbol: Currency pair symbol (e.g., "EUR/USD").
        limit: Number of recent ticks to evaluate.
    """
    service = MarketDataService()
    history = await service.get_price_history(symbol, limit=limit)
    
    if not history or len(history) < 2:
        return {"error": f"Insufficient history to calculate trend for {symbol}"}
        
    # history is typically newest first if lrange pushes to head, or oldest first.
    # Assuming standard chronological order in the mock provider (newest at index 0 or -1).
    # Let's sort by timestamp to be safe.
    sorted_history = sorted(history, key=lambda x: x.get("timestamp", 0))
    
    oldest_price = sorted_history[0].get("price", 0.0)
    newest_price = sorted_history[-1].get("price", 0.0)
    
    if newest_price > oldest_price:
        trend = "bullish"
    elif newest_price < oldest_price:
        trend = "bearish"
    else:
        trend = "neutral"
        
    return {
        "symbol": symbol,
        "trend": trend,
        "start_price": oldest_price,
        "end_price": newest_price,
        "price_change": newest_price - oldest_price,
        "ticks_analyzed": len(sorted_history)
    }
