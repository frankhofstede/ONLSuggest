"""
ONLSuggest FastAPI Application.
Main application entry point with CORS, health checks, and integration test endpoints.
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models import Gemeente, Service
from app.api.v1.router import api_router

# Initialize FastAPI app
app = FastAPI(
    title="ONLSuggest API",
    description="Dutch municipality service suggestion API",
    version="0.1.0",
    debug=settings.debug,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r".*",  # Allow all origins via regex
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - API status message."""
    return {"message": "ONLSuggest API is running"}


@app.get("/health")
async def health():
    """Health check endpoint for monitoring and deployment verification."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "ONLSuggest API"
    }


@app.get("/api/test/db")
async def test_database(db: AsyncSession = Depends(get_db)):
    """
    Database integration test endpoint.
    Returns count of seeded gemeentes and services.
    """
    try:
        # Query gemeentes count
        gemeentes_result = await db.execute(
            select(func.count()).select_from(Gemeente)
        )
        gemeentes_count = gemeentes_result.scalar()

        # Query services count
        services_result = await db.execute(
            select(func.count()).select_from(Service)
        )
        services_count = services_result.scalar()

        return {
            "database": "connected",
            "gemeentes": gemeentes_count,
            "services": services_count,
            "status": "ok"
        }
    except Exception as e:
        return {
            "database": "error",
            "error": str(e),
            "status": "failed"
        }


@app.get("/api/test/redis")
async def test_redis():
    """
    Redis integration test endpoint.
    Tests Redis connection by setting and getting a test value.
    """
    try:
        # Test Redis with set/get
        test_key = "onlsuggest:test:integration"
        test_value = "Hello from ONLSuggest!"

        # Set value with 60 second expiry
        redis_client.setex(test_key, 60, test_value)

        # Get value back
        retrieved_value = redis_client.get(test_key)

        # Clean up
        redis_client.delete(test_key)

        return {
            "redis": "connected",
            "test_value": retrieved_value,
            "status": "ok"
        }
    except Exception as e:
        return {
            "redis": "error",
            "error": str(e),
            "status": "failed"
        }
