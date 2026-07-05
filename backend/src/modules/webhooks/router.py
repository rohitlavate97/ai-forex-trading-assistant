from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Any

from src.modules.webhooks.schemas import WebhookPayload, WebhookResponse
from src.modules.webhooks.service import WebhookService
from src.core.config import settings

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/", response_model=WebhookResponse, status_code=status.HTTP_200_OK)
async def receive_webhook(
    payload: WebhookPayload,
    x_webhook_token: str = Header(None)
):
    """
    Receive and process an external webhook.
    Requires a valid x-webhook-token header that matches the application's secret key.
    """
    # Simple token verification
    if not x_webhook_token or x_webhook_token != settings.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing webhook token"
        )
        
    result = await WebhookService.process_webhook(payload)
    
    return WebhookResponse(
        status=result["status"],
        message=result["message"]
    )
