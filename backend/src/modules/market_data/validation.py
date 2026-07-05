import time
from typing import Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field, field_validator


class TickSchema(BaseModel):
    """Pydantic schema to validate incoming raw tick parameters."""
    symbol: str
    price: float = Field(..., gt=0)
    timestamp: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: float) -> float:
        current_time = time.time()
        # Tick timestamp cannot be in the future (with 5 seconds clock drift allowance)
        if v > current_time + 5.0:
            raise ValueError("Timestamp resides in the future.")
        # Reject ticks older than 1 minute (stale feed protection)
        if current_time - v > 60.0:
            raise ValueError("Tick timestamp is too stale (older than 60s).")
        return v


def validate_price_deviation(
    new_price: float, last_price: Optional[float], max_deviation_pct: float = 10.0
) -> Tuple[bool, str]:
    """
    Sanity check to prevent anomalous feed spikes from entering the database.
    Rejects ticks that deviate from the previous price by more than a threshold.
    """
    if last_price is None or last_price <= 0:
        return True, "No prior reference price. Accepting tick."

    deviation = abs(new_price - last_price) / last_price * 100.0
    if deviation > max_deviation_pct:
        return (
            False,
            f"Price deviation ({deviation:.2f}%) exceeds threshold ({max_deviation_pct}%). "
            f"Ref: {last_price}, New: {new_price}"
        )

    return True, "Price within acceptable bounds."
