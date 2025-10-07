"""
Suggestions API endpoint.
Generates real-time query suggestions for municipal services.
"""
import time
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.suggestion_service import SuggestionService

router = APIRouter()


# Request/Response Models
class SuggestionRequest(BaseModel):
    """Request model for suggestion generation."""
    query: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Partial query text (min 2 characters)",
        examples=["park", "paspoort", "verhuizen"]
    )


class ServiceInfo(BaseModel):
    """Service information in suggestion."""
    id: int
    name: str
    description: str
    category: str


class GemeenteInfo(BaseModel):
    """Gemeente information in suggestion."""
    id: int
    name: str
    description: str


class Suggestion(BaseModel):
    """A single suggestion with metadata."""
    suggestion: str = Field(..., description="Full-text question suggestion")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    service: Optional[ServiceInfo] = None
    gemeente: Optional[GemeenteInfo] = None


class SuggestionResponse(BaseModel):
    """Response model for suggestions."""
    query: str = Field(..., description="Original query text")
    suggestions: List[Suggestion] = Field(..., description="List of generated suggestions (3-5)")
    response_time_ms: int = Field(..., description="Response time in milliseconds")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "park",
                "suggestions": [
                    {
                        "suggestion": "Hoe vraag ik een parkeervergunning aan in Amsterdam?",
                        "confidence": 0.95,
                        "service": {
                            "id": 1,
                            "name": "Parkeervergunning aanvragen",
                            "description": "Aanvragen van een bewonersvergunning voor parkeren in uw wijk",
                            "category": "Verkeer & Vervoer"
                        },
                        "gemeente": {
                            "id": 1,
                            "name": "Amsterdam",
                            "description": "Hoofdstad van Nederland"
                        }
                    }
                ],
                "response_time_ms": 45
            }
        }
    }


@router.post(
    "/suggestions",
    response_model=SuggestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate query suggestions",
    description="Generates 3-5 intelligent question suggestions based on partial query input",
    responses={
        200: {"description": "Suggestions generated successfully"},
        400: {"description": "Bad request - empty query"},
        422: {"description": "Validation error - query too short or too long"},
        500: {"description": "Internal server error"}
    }
)
async def generate_suggestions(
    request: SuggestionRequest,
    db: AsyncSession = Depends(get_db)
) -> SuggestionResponse:
    """
    Generate intelligent query suggestions.

    Args:
        request: Suggestion request with query text
        db: Database session

    Returns:
        SuggestionResponse with 3-5 suggestions

    Raises:
        HTTPException: For validation errors or server errors
    """
    start_time = time.time()

    try:
        # Validate query
        query = request.query.strip()
        if not query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query cannot be empty"
            )

        # Generate suggestions using service
        suggestion_service = SuggestionService(db)
        suggestions = await suggestion_service.generate_suggestions(query)

        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)

        return SuggestionResponse(
            query=query,
            suggestions=suggestions,
            response_time_ms=response_time_ms
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate suggestions: {str(e)}"
        )
