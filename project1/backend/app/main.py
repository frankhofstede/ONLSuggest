"""
ONLSuggest FastAPI Application
BMAD-compliant architecture with proper separation of concerns
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import health, suggestions, admin

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Dutch municipality service suggestion API",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(suggestions.router, prefix="/api/v1", tags=["suggestions"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }


# Vercel serverless function handler
handler = app
