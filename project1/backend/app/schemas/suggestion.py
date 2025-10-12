"""
Pydantic schemas for suggestions API
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SuggestionRequest(BaseModel):
    """Request schema for suggestions endpoint"""
    query: str = Field(..., min_length=2, description="Search query (minimum 2 characters)")
    max_results: int = Field(5, ge=1, le=10, description="Maximum number of suggestions")


class ServiceInfo(BaseModel):
    """Service information in suggestion"""
    id: Optional[int] = None
    name: str
    description: str
    category: str


class Suggestion(BaseModel):
    """Single suggestion response"""
    suggestion: str
    confidence: float
    service: ServiceInfo
    gemeente: Optional[str] = None


class SuggestionResponse(BaseModel):
    """Response schema for suggestions endpoint"""
    query: str
    suggestions: List[Suggestion]
    response_time_ms: float
    using_database: bool
    suggestion_engine: str
    fallback_occurred: Optional[bool] = None
    fallback_reason: Optional[str] = None
