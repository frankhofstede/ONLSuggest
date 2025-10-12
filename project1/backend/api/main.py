"""
ONLSuggest FastAPI Application
BMAD-compliant architecture with proper separation of concerns
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import suggestions, admin, health

# Create FastAPI application
app = FastAPI(
    title="ONLSuggest API",
    description="Dutch government service discovery through intelligent query suggestions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(suggestions.router, prefix="/api", tags=["suggestions"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ONLSuggest API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Vercel serverless function handler
handler = app
