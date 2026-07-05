import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.modules.auth.dependencies import get_current_user

# Setup test client and override dependency
client = TestClient(app)

async def override_get_current_user():
    return {"id": "123", "username": "testuser"}

app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.mark.asyncio
@patch("src.modules.chat.router.chat_agent.run_stream")
async def test_chat_stream_endpoint(mock_run_stream):
    # Mock the stream result
    mock_result = MagicMock()
    
    # Mock stream_text to yield chunks
    async def mock_stream_text(delta=False):
        yield "Hello, "
        yield "this is a "
        yield "streaming response."
        
    mock_result.stream_text = mock_stream_text
    
    # Mock the async context manager returned by run_stream
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_result
    
    # Patch the agent's run_stream method
    mock_run_stream.return_value = mock_cm
    
    # Make request to the stream endpoint
    response = client.post(
        "/api/v1/chat/stream",
        json={"message": "Tell me about EUR/USD"}
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
    
    content = response.content.decode("utf-8")
    assert "data: {\"text\": \"Hello, \"}" in content
    assert "data: {\"text\": \"this is a \"}" in content
    assert "data: {\"text\": \"streaming response.\"}" in content
    assert "data: [DONE]" in content
