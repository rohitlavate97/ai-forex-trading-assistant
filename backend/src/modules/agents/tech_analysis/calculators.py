import math
from typing import Dict, List, Optional, Tuple, Any


def calculate_sma(prices: List[float], period: int) -> Optional[float]:
    """Calculate Simple Moving Average (SMA)."""
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def calculate_ema(prices: List[float], period: int) -> Optional[float]:
    """Calculate Exponential Moving Average (EMA) using standard multiplier."""
    if len(prices) < period:
        return None
    
    # Base multiplier
    multiplier = 2.0 / (period + 1)
    
    # Start with SMA as initial value
    ema = sum(prices[:period]) / period
    
    # Calculate EMA iteratively
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
        
    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """Calculate Relative Strength Index (RSI) using Wilder's smoothing technique."""
    if len(prices) < period + 1:
        return None

    gains: List[float] = []
    losses: List[float] = []

    # Calculate differences
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i - 1]
        if diff >= 0:
            gains.append(diff)
            losses.append(0.0)
        else:
            gains.append(0.0)
            losses.append(abs(diff))

    # Initial averages
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    if avg_loss == 0:
        return 100.0

    # Wilder's smoothing
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0

    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def calculate_macd(
    prices: List[float], 
    fast_period: int = 12, 
    slow_period: int = 26, 
    signal_period: int = 9
) -> Optional[Tuple[float, float, float]]:
    """
    Calculate MACD Line, Signal Line, and Histogram.
    Returns: Tuple of (macd_line, signal_line, histogram)
    """
    if len(prices) < slow_period + signal_period:
        return None

    # 1. Compute EMA series for Fast and Slow periods
    fast_emas: List[float] = []
    slow_emas: List[float] = []
    
    # Helper to calculate EMA series
    def get_ema_series(data: List[float], p: int) -> List[float]:
        series = []
        mult = 2.0 / (p + 1)
        current_ema = sum(data[:p]) / p
        series.append(current_ema)
        for val in data[p:]:
            current_ema = (val - current_ema) * mult + current_ema
            series.append(current_ema)
        return series

    # Fast EMA starts at index fast_period
    fast_series = get_ema_series(prices, fast_period)
    # Slow EMA starts at index slow_period
    slow_series = get_ema_series(prices, slow_period)
    
    # Align lengths: Slow series is shorter than Fast series.
    # Align them so they represent identical timestamps.
    diff_len = len(fast_series) - len(slow_series)
    aligned_fast = fast_series[diff_len:]
    
    # 2. MACD Line = Fast EMA - Slow EMA
    macd_lines = [f - s for f, s in zip(aligned_fast, slow_series)]
    
    # 3. Signal Line = EMA(macd_lines, signal_period)
    if len(macd_lines) < signal_period:
        return None
        
    signal_mult = 2.0 / (signal_period + 1)
    signal_line = sum(macd_lines[:signal_period]) / signal_period
    
    for val in macd_lines[signal_period:]:
        signal_line = (val - signal_line) * signal_mult + signal_line
        
    macd_line = macd_lines[-1]
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    prices: List[float], period: int = 20, num_std: float = 2.0
) -> Optional[Tuple[float, float, float]]:
    """
    Calculate Bollinger Bands.
    Returns: Tuple of (middle_band, upper_band, lower_band)
    """
    if len(prices) < period:
        return None

    subset = prices[-period:]
    sma = sum(subset) / period
    
    # Standard deviation
    variance = sum((x - sma) ** 2 for x in subset) / period
    std_dev = math.sqrt(variance)
    
    upper = sma + (num_std * std_dev)
    lower = sma - (num_std * std_dev)
    
    return sma, upper, lower


def calculate_atr(
    highs: List[float], lows: List[float], closes: List[float], period: int = 14
) -> Optional[float]:
    """Calculate Average True Range (ATR)."""
    if len(closes) < period + 1 or len(highs) < period or len(lows) < period:
        return None

    # Calculate True Ranges
    tr_values: List[float] = []
    for i in range(1, len(closes)):
        h = highs[i - 1]  # Align lists
        l = lows[i - 1]
        prev_close = closes[i - 1]
        
        tr = max(
            h - l,
            abs(h - prev_close),
            abs(l - prev_close)
        )
        tr_values.append(tr)
        
    # Initial ATR is SMA of True Ranges
    if len(tr_values) < period:
        return None
        
    atr = sum(tr_values[:period]) / period
    
    # Smoothed ATR
    for i in range(period, len(tr_values)):
        atr = (atr * (period - 1) + tr_values[i]) / period
        
    return atr


def calculate_fibonacci_retracement(high: float, low: float) -> Dict[str, float]:
    """
    Calculate Fibonacci Retracement levels between a given high and low.
    Handles both uptrend and downtrend retracements.
    """
    diff = high - low
    levels = [0.0, 0.236, 0.382, 0.500, 0.618, 0.786, 1.0]
    
    # Standard retracements
    results = {}
    for lvl in levels:
        # Assuming uptrend retracement (low is start, high is peak)
        results[f"level_{int(lvl * 1000) / 10}"] = high - (lvl * diff)
        
    return results


def calculate_ichimoku_cloud(
    highs: List[float], lows: List[float], closes: List[float]
) -> Optional[Dict[str, float]]:
    """
    Calculate current Ichimoku Cloud metrics.
    Requires at least 52 periods of high/low/close data.
    """
    if len(closes) < 52 or len(highs) < 52 or len(lows) < 52:
        return None
        
    # Helper to calculate average of highest high and lowest low over N periods
    def get_donchian_middle(h_list: List[float], l_list: List[float], period: int) -> float:
        sub_highs = h_list[-period:]
        sub_lows = l_list[-period:]
        return (max(sub_highs) + min(sub_lows)) / 2.0

    # 1. Tenkan-sen (Conversion Line): 9 periods
    tenkan = get_donchian_middle(highs, lows, 9)
    
    # 2. Kijun-sen (Base Line): 26 periods
    kijun = get_donchian_middle(highs, lows, 26)
    
    # 3. Senkou Span A (Leading Span A): (Conversion + Base)/2 plotted 26 periods ahead
    senkou_a = (tenkan + kijun) / 2.0
    
    # 4. Senkou Span B (Leading Span B): 52 periods high/low plotted 26 periods ahead
    senkou_b = get_donchian_middle(highs, lows, 52)
    
    # 5. Chikou Span (Lagging Span): Close plotted 26 periods behind
    chikou = closes[-1]
    
    return {
        "tenkan_sen": tenkan,
        "kijun_sen": kijun,
        "senkou_span_a": senkou_a,
        "senkou_span_b": senkou_b,
        "chikou_span": chikou,
    }
