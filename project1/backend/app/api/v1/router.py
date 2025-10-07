"""API v1 router configuration."""
from fastapi import APIRouter

from app.api.v1.endpoints import suggestions

# Create v1 API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(
    suggestions.router,
    tags=["suggestions"]
)
