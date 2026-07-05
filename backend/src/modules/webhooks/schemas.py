from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class WebhookPayload(BaseModel):
    source: str = Field(..., description="The source of the webhook, e.g., 'tradingview'")
    type: str = Field(..., description="Type of alert, e.g., 'buy_signal', 'price_alert'")
    data: Dict[str, Any] = Field(..., description="The actual payload data from the source")
    timestamp: Optional[str] = Field(None, description="Timestamp of the event")

class WebhookResponse(BaseModel):
    status: str = Field(..., example="success")
    message: str = Field(..., example="Webhook received and processed")
