from typing import Dict, List, Optional, Any
from loguru import logger
from src.modules.market_data.service import MarketDataService
from src.modules.agents.tech_analysis.calculators import (
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_fibonacci_retracement,
    calculate_ichimoku_cloud,
)


async def get_price_history_lists(symbol: str, limit: int = 60) -> Optional[Dict[str, List[float]]]:
    """
    Helper tool to fetch historical prices for a currency pair from Redis.
    Returns: Dict containing 'closes', 'highs', 'lows', and 'timestamps' list, or None.
    """
    service = MarketDataService()
    history = await service.get_price_history(symbol, limit)
    
    if not history:
        logger.warning(f"No price history found in Redis for symbol: {symbol}")
        return None
        
    # Reverse so the oldest is first, newest is last (required for calculations)
    history.reverse()
    
    closes = [tick["price"] for tick in history]
    # Fallback high/low to price if bid/ask high/low are missing
    highs = [tick.get("high") or tick["price"] for tick in history]
    lows = [tick.get("low") or tick["price"] for tick in history]
    timestamps = [tick["timestamp"] for tick in history]
    
    return {
        "closes": closes,
        "highs": highs,
        "lows": lows,
        "timestamps": timestamps,
    }


async def tool_get_indicators_summary(symbol: str) -> Dict[str, Any]:
    """
    Query and calculate a complete set of technical indicators (RSI, MACD, Bollinger Bands)
    for a given currency pair symbol (e.g. 'EUR/USD').
    """
    # Fetch 60 ticks of history (sufficient for default MACD 26+9 and RSI 14)
    data = await get_price_history_lists(symbol, limit=60)
    if not data:
        return {"error": f"Insufficient price history cached in Redis to compute indicators for {symbol}."}
        
    closes = data["closes"]
    
    rsi = calculate_rsi(closes)
    macd = calculate_macd(closes)
    bb = calculate_bollinger_bands(closes)
    
    result: Dict[str, Any] = {
        "symbol": symbol,
        "current_price": closes[-1],
        "rsi": round(rsi, 2) if rsi is not None else None,
    }
    
    if macd:
        result["macd"] = {
            "macd_line": round(macd[0], 5),
            "signal_line": round(macd[1], 5),
            "histogram": round(macd[2], 5),
        }
    else:
        result["macd"] = None
        
    if bb:
        result["bollinger_bands"] = {
            "middle_band": round(bb[0], 5),
            "upper_band": round(bb[1], 5),
            "lower_band": round(bb[2], 5),
        }
    else:
        result["bollinger_bands"] = None
        
    return result


async def tool_get_advanced_indicators(symbol: str) -> Dict[str, Any]:
    """
    Query and calculate advanced indicators (ATR, Fibonacci Retracement, Ichimoku Cloud)
    for a given currency pair symbol (e.g. 'EUR/USD').
    """
    # Fetch 60 ticks of history (sufficient for Ichimoku 52 and ATR 14)
    data = await get_price_history_lists(symbol, limit=60)
    if not data:
        return {"error": f"Insufficient price history cached in Redis to compute advanced indicators for {symbol}."}
        
    closes = data["closes"]
    highs = data["highs"]
    lows = data["lows"]
    
    atr = calculate_atr(highs, lows, closes)
    ichimoku = calculate_ichimoku_cloud(highs, lows, closes)
    
    # Fibonacci levels based on high/low of the period
    max_high = max(highs)
    min_low = min(lows)
    fib = calculate_fibonacci_retracement(max_high, min_low)
    
    result: Dict[str, Any] = {
        "symbol": symbol,
        "atr": round(atr, 5) if atr is not None else None,
        "fibonacci_retracements": {k: round(v, 5) for k, v in fib.items()},
    }
    
    if ichimoku:
        result["ichimoku_cloud"] = {k: round(v, 5) for k, v in ichimoku.items()}
    else:
        result["ichimoku_cloud"] = None
        
    return result
