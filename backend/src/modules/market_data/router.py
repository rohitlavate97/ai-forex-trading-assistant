from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any
from src.modules.market_data.service import MarketDataService

router = APIRouter(prefix="/market-data", tags=["Market Data"])


@router.get("/price/{symbol:path}")
async def get_live_price(symbol: str):
    """Retrieve the current cached price and Bid/Ask tick details for a currency pair."""
    # Note: symbol:path allows symbol containing slashes like EUR/USD
    service = MarketDataService()
    price_data = await service.get_live_price(symbol)
    if not price_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Price data not available for symbol '{symbol}'. Ensure feed ingestion is active."
        )
    return price_data


@router.get("/history/{symbol:path}")
async def get_price_history(
    symbol: str,
    limit: int = Query(50, ge=1, le=100, description="Number of tick entries to retrieve")
):
    """Retrieve recent price tick history for a given forex symbol."""
    service = MarketDataService()
    return await service.get_price_history(symbol, limit)


@router.get("/metrics/{symbol:path}")
async def get_feed_metrics(symbol: str):
    """Retrieve feed telemetry metrics such as rejected anomalous ticks."""
    service = MarketDataService()
    return await service.get_metrics(symbol)
