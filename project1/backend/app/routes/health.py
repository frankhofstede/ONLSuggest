"""
Health check routes
"""
from fastapi import APIRouter
import sys

from app.core.config import settings
from app.models.database import db

router = APIRouter()


@router.get("/api/health")
async def health_check():
    """
    Health check endpoint
    Returns system status and database availability
    """
    db_available = False
    db_error = None
    try:
        stats = db.get_stats()
        db_available = True
    except Exception as e:
        db_error = str(e)

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "service": settings.PROJECT_NAME,
        "database": {
            "available": db_available,
            "error": db_error
        },
        "environment": {
            "python_version": sys.version.split()[0]
        }
    }
