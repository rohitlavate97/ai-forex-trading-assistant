import pytest
from httpx import AsyncClient
from typing import AsyncGenerator
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from src.main import app
from src.core.database import Base, get_db
from src.modules.auth.dependencies import get_current_user

# Create in-memory SQLite engine for tests
test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

# Mock User
mock_user = {
    "id": "test-user-id",
    "email": "test@example.com",
    "role": "USER"
}

# Override auth dependency
async def override_get_current_user():
    return mock_user

app.dependency_overrides[get_current_user] = override_get_current_user

@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(test_engine) as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def override_get_db(db_session: AsyncSession):
    async def _override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)

from httpx import AsyncClient, ASGITransport

@pytest.fixture
def client(override_get_db):
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

@pytest.mark.asyncio
async def test_create_journal_entry(client: AsyncClient):
    payload = {
        "currency_pair": "EUR/USD",
        "direction": "LONG",
        "entry_price": 1.0950,
        "notes": "Test entry",
        "tags": ["#test"]
    }
    response = await client.post("/api/v1/journal/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["currency_pair"] == "EUR/USD"
    assert data["direction"] == "LONG"
    assert "id" in data
    assert data["user_id"] == "test-user-id"

@pytest.mark.asyncio
async def test_get_journal_entries(client: AsyncClient):
    # Create an entry first
    payload = {
        "currency_pair": "GBP/USD",
        "direction": "SHORT",
        "entry_price": 1.2500
    }
    await client.post("/api/v1/journal/", json=payload)
    
    response = await client.get("/api/v1/journal/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["currency_pair"] == "GBP/USD"

@pytest.mark.asyncio
async def test_update_journal_entry(client: AsyncClient):
    # Create an entry first
    payload = {
        "currency_pair": "USD/JPY",
        "direction": "LONG",
        "entry_price": 150.00
    }
    create_resp = await client.post("/api/v1/journal/", json=payload)
    entry_id = create_resp.json()["id"]

    update_payload = {
        "exit_price": 151.00,
        "profit_loss": 100.0,
        "notes": "Updated note"
    }
    response = await client.patch(f"/api/v1/journal/{entry_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["exit_price"] == 151.00
    assert data["profit_loss"] == 100.0
    assert data["notes"] == "Updated note"
    assert data["currency_pair"] == "USD/JPY"

@pytest.mark.asyncio
async def test_delete_journal_entry(client: AsyncClient):
    # Create an entry first
    payload = {
        "currency_pair": "USD/CAD",
        "direction": "SHORT",
        "entry_price": 1.3500
    }
    create_resp = await client.post("/api/v1/journal/", json=payload)
    entry_id = create_resp.json()["id"]

    # Delete it
    response = await client.delete(f"/api/v1/journal/{entry_id}")
    assert response.status_code == 204

    # Try to get it
    get_response = await client.get(f"/api/v1/journal/{entry_id}")
    assert get_response.status_code == 404
