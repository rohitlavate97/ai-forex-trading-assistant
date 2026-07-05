import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from src.core.config import settings
from src.core.database import async_session_maker
from src.core.redis import init_redis, close_redis, get_redis
from src.modules.auth.router import router as auth_router
from src.modules.market_data.router import router as market_data_router
from src.modules.economic_calendar.router import router as calendar_router
from src.modules.news_intelligence.router import router as news_router
from src.modules.market_data.ingestion import MarketDataIngestionService

# Ingestion service container
ingestion_service = MarketDataIngestionService()
mock_server_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global mock_server_task
    # 1. Initialize Redis connection pool
    await init_redis()
    
    # 2. Spawn mock WebSockets server if running in mock development mode
    if settings.MARKET_DATA_PROVIDER == "mock" and settings.ENV == "development":
        from src.modules.market_data.mock_provider import start_mock_websocket_server
        # Run mock server on port 8765 in background
        mock_server_task = asyncio.create_task(start_mock_websocket_server())
        # Give server a brief window to start up
        await asyncio.sleep(0.5)
        
    # 3. Spin up the Market Data Ingestion WebSocket Client
    await ingestion_service.start()
    
    yield
    
    # Shutdown steps:
    await ingestion_service.stop()
    
    if mock_server_task:
        mock_server_task.cancel()
        try:
            await mock_server_task
        except asyncio.CancelledError:
            pass
            
    await close_redis()


app = FastAPI(
    title="AI Forex Trading Assistant API",
    description="Backend API for Forex Decision-Support, Technical Analysis, News Intelligence, and Trading Journal",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.ALLOWED_HOSTS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(market_data_router, prefix=settings.API_V1_PREFIX)
app.include_router(calendar_router, prefix=settings.API_V1_PREFIX)
app.include_router(news_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Forex Trading Assistant API", "status": "active"}


@app.get("/health")
async def health_check():
    # Verify Database connection status
    db_status = "offline"
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
            db_status = "online"
    except Exception:
        db_status = "offline"
        
    # Verify Redis status
    redis_status = "offline"
    try:
        redis = await get_redis()
        ping_ok = await redis.ping()
        if ping_ok:
            redis_status = "online"
    except Exception:
        redis_status = "offline"

    return {
        "status": "healthy" if db_status == "online" and redis_status == "online" else "degraded",
        "services": {
            "api": "online",
            "database": db_status,
            "redis": redis_status,
            "rabbitmq": "pending",
            "qdrant": "pending",
        },
    }
