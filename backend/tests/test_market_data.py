import json
import time
import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import ValidationError
from src.modules.market_data.validation import TickSchema, validate_price_deviation
from src.modules.market_data.ingestion import MarketDataIngestionService


def test_tick_validation_success():
    """Test that valid ticks satisfy the pydantic TickSchema."""
    tick_data = {
        "symbol": "EUR/USD",
        "price": 1.0854,
        "timestamp": time.time(),
        "bid": 1.0853,
        "ask": 1.0855,
    }
    tick = TickSchema(**tick_data)
    assert tick.symbol == "EUR/USD"
    assert tick.price == 1.0854


def test_tick_validation_failures():
    """Test that invalid values trigger Pydantic validation errors."""
    current_time = time.time()
    
    # 1. Negative price
    with pytest.raises(ValidationError):
        TickSchema(symbol="EUR/USD", price=-1.0, timestamp=current_time)
        
    # 2. Future timestamp (clock drift threshold is 5s)
    with pytest.raises(ValidationError) as exc:
        TickSchema(symbol="EUR/USD", price=1.0854, timestamp=current_time + 10.0)
    assert "Timestamp resides in the future" in str(exc.value)
        
    # 3. Stale timestamp (older than 60s)
    with pytest.raises(ValidationError) as exc:
        TickSchema(symbol="EUR/USD", price=1.0854, timestamp=current_time - 70.0)
    assert "Tick timestamp is too stale" in str(exc.value)


def test_deviation_checks():
    """Test sanity check deviation rule outcomes."""
    # First tick case
    is_valid, _ = validate_price_deviation(1.0850, last_price=None)
    assert is_valid is True
    
    # Acceptable change (e.g. 1.0850 -> 1.0865 is ~0.14% change)
    is_valid, _ = validate_price_deviation(1.0865, last_price=1.0850)
    assert is_valid is True
    
    # Anomalous change (e.g. 1.0850 -> 1.2500 is ~15.2% change, limit is 10.0%)
    is_valid, msg = validate_price_deviation(1.2500, last_price=1.0850)
    assert is_valid is False
    assert "Price deviation" in msg


@pytest.mark.asyncio
async def test_process_message_valid_tick():
    """Test parsing, validating, and saving a valid message inside the ingestion service."""
    # Create mock message
    msg = json.dumps({
        "symbol": "EUR/USD",
        "price": 1.0850,
        "bid": 1.0849,
        "ask": 1.0851,
        "timestamp": time.time(),
    })
    
    service = MarketDataIngestionService()
    
    # Mock Redis client
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=None)  # No previous price
    
    # Patch get_redis utility dependency
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("src.modules.market_data.ingestion.get_redis", AsyncMock(return_value=mock_redis))
        
        await service._process_message(msg)
        
        # Verify tick was saved to Redis
        mock_redis.set.assert_called_once()
        mock_redis.lpush.assert_called_once()
        mock_redis.ltrim.assert_called_once()
        
        # Verify no rejections logged
        mock_redis.incr.assert_not_called()


@pytest.mark.asyncio
async def test_process_message_anomalous_tick():
    """Test that anomalous ticks are rejected and statistics updated."""
    msg = json.dumps({
        "symbol": "EUR/USD",
        "price": 1.5500,  # Spikes from reference 1.0850 (> 40% dev)
        "timestamp": time.time(),
    })
    
    service = MarketDataIngestionService()
    
    # Mock Redis returning last price of 1.0850
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=json.dumps({"symbol": "EUR/USD", "price": 1.0850}))
    
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr("src.modules.market_data.ingestion.get_redis", AsyncMock(return_value=mock_redis))
        
        await service._process_message(msg)
        
        # Tick should be rejected: verify NOT saved
        mock_redis.set.assert_not_called()
        mock_redis.lpush.assert_not_called()
        
        # Verify rejection metrics counter incremented
        mock_redis.incr.assert_called_once_with("metrics:rejected_ticks:EUR/USD")
