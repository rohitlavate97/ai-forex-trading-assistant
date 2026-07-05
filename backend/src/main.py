from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Forex Trading Assistant API",
    description="Backend API for Forex Decision-Support, Technical Analysis, News Intelligence, and Trading Journal",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production via config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Welcome to the AI Forex Trading Assistant API", "status": "active"}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "api": "online",
            "database": "pending",
            "redis": "pending",
            "rabbitmq": "pending",
            "qdrant": "pending",
        },
    }
