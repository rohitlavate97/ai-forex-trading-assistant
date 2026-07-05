from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any
import json
import logging

from src.modules.auth.dependencies import get_current_user
from src.core.database import get_db
from src.modules.chat.schemas import ChatRequest
from src.modules.chat.agent import chat_agent

router = APIRouter(prefix="/chat", tags=["AI Chat"])
logger = logging.getLogger(__name__)


@router.post("/stream")
async def stream_chat(
    request: ChatRequest,
    current_user: Any = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    """
    Stream a response from the AI Chat Agent using Server-Sent Events (SSE).
    """
    # Convert history into a string context or Pydantic AI messages.
    # For simplicity, we just inject the history into the prompt here.
    # In a full implementation, history would be mapped to Pydantic AI's Message instances.
    
    context = ""
    if request.history:
        context = "Previous conversation:\n"
        for msg in request.history:
            context += f"{msg.role}: {msg.content}\n"
        context += "\n"
        
    full_prompt = context + f"User: {request.message}"

    async def event_generator():
        try:
            # Note: For production Pydantic AI, stream() yields async chunks.
            async with chat_agent.run_stream(full_prompt, deps=session) as result:
                async for text in result.stream_text(delta=True):
                    # Send as SSE payload
                    yield f"data: {json.dumps({'text': text})}\n\n"
                    
            # Send completion event
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
