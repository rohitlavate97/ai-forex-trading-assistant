import asyncio
import json
import random
import time
from typing import Optional
import websockets
from loguru import logger
from src.core.config import settings
from src.core.redis import get_redis
from src.modules.market_data.validation import TickSchema, validate_price_deviation


class MarketDataIngestionService:
    """WebSocket Client to ingest live currency ticks, validate them, and cache in Redis."""

    def __init__(self) -> None:
        self.provider = settings.MARKET_DATA_PROVIDER
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.reconnect_base_delay = 1.0
        self.reconnect_max_delay = 60.0
        
        # Configure WebSocket URLs based on provider
        if self.provider == "mock":
            self.ws_url = "ws://localhost:8765"
        elif self.provider == "twelvedata":
            self.ws_url = f"wss://ws.twelvedata.com/v1/quotes?apikey={settings.MARKET_DATA_API_KEY}"
        else:
            # Fallback to local mock server
            self.ws_url = "ws://localhost:8765"

    async def start(self) -> None:
        """Start the ingestion loop as a background task."""
        if self.is_running:
            logger.warning("Market Ingestion Service is already running.")
            return

        self.is_running = True
        self._task = asyncio.create_task(self._connect_loop())
        logger.info(f"Market Ingestion Service started utilizing provider: {self.provider}")

    async def stop(self) -> None:
        """Stop the ingestion background task."""
        if not self.is_running:
            return

        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Market Ingestion Service stopped.")

    async def _connect_loop(self) -> None:
        """Persistent connection loop with exponential backoff and jitter."""
        attempt = 0
        
        while self.is_running:
            try:
                logger.info(f"Connecting to market data feed at: {self.ws_url} (Attempt {attempt + 1})")
                async with websockets.connect(self.ws_url) as ws:
                    attempt = 0  # Reset reconnect counter on successful connect
                    logger.info("Market data feed connection established successfully.")
                    
                    # If Twelve Data, we need to send a subscription message
                    if self.provider == "twelvedata":
                        sub_msg = {
                            "action": "subscribe",
                            "params": {
                                "symbols": "EUR/USD,GBP/USD,USD/JPY,AUD/USD"
                            }
                        }
                        await ws.send(json.dumps(sub_msg))
                        logger.info("Sent subscription request to Twelve Data feed.")
                    
                    # Read messages
                    while self.is_running:
                        message = await ws.recv()
                        await self._process_message(message)
                        
            except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
                logger.warning(f"Market feed connection lost/failed: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in market ingestion loop: {e}")
                
            if self.is_running:
                # Exponential backoff with jitter
                delay = min(
                    self.reconnect_base_delay * (2 ** attempt) + random.uniform(0.1, 1.0),
                    self.reconnect_max_delay
                )
                logger.info(f"Reconnecting to feed in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
                attempt += 1

    async def _process_message(self, raw_message: str) -> None:
        """Parse, validate, check deviation, and save price tick to Redis."""
        try:
            data = json.loads(raw_message)
            
            # Twelve data wrap ticks in an envelope or list sometimes, extract data
            if isinstance(data, dict) and data.get("event") == "heartbeat":
                return
                
            # Parse tick into standard format
            # Twelve data format maps: { 'symbol': 'EUR/USD', 'price': 1.0850, ... }
            # If the format is nested or from Twelve Data, normalize here
            symbol = data.get("symbol")
            price = data.get("price")
            timestamp = data.get("timestamp")
            
            # Skip invalid envelopes
            if not symbol or price is None:
                return
                
            # If Twelve Data timestamp is provided in text format, parse it
            if isinstance(timestamp, str):
                # Standard Twelve Data format: "2026-07-05 12:00:00"
                # Parse or default to current time
                timestamp = time.time()
            elif timestamp is None:
                timestamp = time.time()
                
            raw_tick = {
                "symbol": symbol,
                "price": float(price),
                "timestamp": float(timestamp),
                "bid": float(data.get("bid")) if data.get("bid") is not None else None,
                "ask": float(data.get("ask")) if data.get("ask") is not None else None,
                "high": float(data.get("high")) if data.get("high") is not None else None,
                "low": float(data.get("low")) if data.get("low") is not None else None,
            }
            
            # 1. Pydantic validation
            tick = TickSchema(**raw_tick)
            
            # Get Redis client
            redis = await get_redis()
            
            # 2. Retrieve last price for deviation checks
            price_key = f"price:{tick.symbol}"
            last_price_str = await redis.get(price_key)
            last_price = None
            if last_price_str:
                last_data = json.loads(last_price_str)
                last_price = last_data.get("price")
                
            # 3. Deviation check (reject deviations > 10% to block anomalies)
            is_valid, msg = validate_price_deviation(tick.price, last_price)
            if not is_valid:
                logger.warning(f"Anomalous tick rejected for {tick.symbol}: {msg}")
                # Increment rejection counter in Redis for metrics
                await redis.incr(f"metrics:rejected_ticks:{tick.symbol}")
                return
                
            # 4. Save to Redis
            # Cache active tick
            tick_json = json.dumps(tick.model_dump())
            await redis.set(price_key, tick_json)
            
            # Push to historical list (limit history to last 100 entries)
            history_key = f"history:{tick.symbol}"
            await redis.lpush(history_key, tick_json)
            await redis.ltrim(history_key, 0, 99)
            
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse raw feed message: {raw_message[:200]}")
        except Exception as e:
            logger.error(f"Error processing tick message: {e}")
