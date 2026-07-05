import asyncio
import json
import random
import time
from typing import Set, Dict, Tuple, Any
import websockets
from loguru import logger

# Base prices for mock forex pairs
BASE_PRICES: Dict[str, float] = {
    "EUR/USD": 1.08500,
    "GBP/USD": 1.27200,
    "USD/JPY": 155.400,
    "AUD/USD": 0.66500,
}

# Spreads in pips (1 pip = 0.0001 for most, 0.01 for JPY)
SPREADS: Dict[str, float] = {
    "EUR/USD": 0.00012,  # 1.2 pips
    "GBP/USD": 0.00018,  # 1.8 pips
    "USD/JPY": 0.015,    # 1.5 pips
    "AUD/USD": 0.00015,  # 1.5 pips
}

# Active client connections
connected_clients: Set[websockets.WebSocketServerProtocol] = set()


def generate_mock_tick(symbol: str, current_price: float) -> Tuple[float, Dict[str, Any]]:
    """Generate a random walk price tick for a given currency pair."""
    # Pip size definition
    pip = 0.01 if "JPY" in symbol else 0.0001
    
    # Random walk: change price by [-3, +3] pips
    change_pips = random.uniform(-3, 3)
    new_price = current_price + (change_pips * pip)
    
    # Ensure positive
    new_price = max(new_price, 0.0001)
    
    # Bid/Ask calculations
    spread = SPREADS[symbol]
    bid = new_price - (spread / 2.0)
    ask = new_price + (spread / 2.0)
    
    tick = {
        "symbol": symbol,
        "price": round(new_price, 5),
        "bid": round(bid, 5),
        "ask": round(ask, 5),
        "timestamp": time.time(),
        "high": round(new_price + (pip * 10), 5),
        "low": round(new_price - (pip * 10), 5),
    }
    return new_price, tick


async def broadcast_ticks_loop() -> None:
    """Continuously broadcast mock ticks to all connected clients."""
    prices = {symbol: base for symbol, base in BASE_PRICES.items()}
    logger.info("Starting mock price broadcast loop...")
    
    while True:
        try:
            if not connected_clients:
                await asyncio.sleep(1.0)
                continue
                
            # Pick a random currency pair to tick
            symbol = random.choice(list(BASE_PRICES.keys()))
            new_price, tick = generate_mock_tick(symbol, prices[symbol])
            prices[symbol] = new_price
            
            # Serialize payload
            message = json.dumps(tick)
            
            # Broadcast to all clients
            inactive_clients = set()
            for client in connected_clients:
                try:
                    await client.send(message)
                except websockets.exceptions.ConnectionClosed:
                    inactive_clients.add(client)
            
            # Clean up disconnected clients
            if inactive_clients:
                connected_clients.difference_update(inactive_clients)
                logger.info(f"Cleaned up {len(inactive_clients)} disconnected clients.")
                
            # Tick speed: random interval between 200ms and 800ms
            await asyncio.sleep(random.uniform(0.2, 0.8))
            
        except Exception as e:
            logger.error(f"Error in mock broadcast loop: {e}")
            await asyncio.sleep(1.0)


async def handler(websocket: websockets.WebSocketServerProtocol) -> None:
    """Websocket connection handler registering new clients."""
    logger.info(f"New client connected to mock feed from: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        # Keep connection open
        await websocket.wait_closed()
    finally:
        connected_clients.discard(websocket)
        logger.info(f"Client disconnected: {websocket.remote_address}")


async def start_mock_websocket_server(host: str = "0.0.0.0", port: int = 8765) -> None:
    """Spin up the mock websocket server and start broadcasting."""
    logger.info(f"Initializing Mock WebSockets Server on ws://{host}:{port}")
    async with websockets.serve(handler, host, port):
        # Run broadcast loop concurrently
        await broadcast_ticks_loop()
