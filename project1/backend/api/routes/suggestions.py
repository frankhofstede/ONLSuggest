"""
Suggestions API routes
Epic 1: Query Suggestion Engine
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time

from api.core.config import settings
from api.models.database import db
from api.services.template_engine import template_engine
from api.services.dutch_matcher import DutchMatcher
from api.services.koop_client import KoopAPIClient

router = APIRouter()


# Request/Response models
class SuggestionRequest(BaseModel):
    query: str = Field(..., min_length=2, description="Search query")
    max_results: int = Field(5, ge=1, le=10)


class ServiceInfo(BaseModel):
    id: int
    name: str
    description: str
    category: str


class Suggestion(BaseModel):
    suggestion: str
    confidence: float
    service: ServiceInfo
    gemeente: Optional[str] = None


class SuggestionResponse(BaseModel):
    query: str
    suggestions: List[Suggestion]
    response_time_ms: float
    using_database: bool
    suggestion_engine: str


@router.post("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(request: SuggestionRequest):
    """
    Generate query suggestions based on user input

    Story 1.1: Basic Search Input Processing
    Story 1.2: Dutch NLP Matching
    Story 1.3: Question Template Engine
    """
    start_time = time.time()

    # Validate input
    if not request.query or len(request.query) < settings.QUERY_MIN_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query must be at least {settings.QUERY_MIN_LENGTH} characters"
        )

    # Check which engine to use (template or KOOP)
    suggestion_engine = db.get_setting('suggestion_engine') or 'template'

    # Generate suggestions
    try:
        if suggestion_engine == "koop":
            # Try KOOP API first
            koop_client = KoopAPIClient()
            suggestions = _generate_suggestions_from_koop(
                koop_client,
                request.query,
                request.max_results
            )
        else:
            # Use template engine with database
            suggestions = _generate_suggestions_from_database(
                request.query,
                request.max_results
            )
    except Exception as e:
        # Fallback to database if KOOP fails
        suggestions = _generate_suggestions_from_database(
            request.query,
            request.max_results
        )
        suggestion_engine = "template (fallback)"

    response_time = (time.time() - start_time) * 1000

    return SuggestionResponse(
        query=request.query,
        suggestions=suggestions,
        response_time_ms=round(response_time, 2),
        using_database=True,
        suggestion_engine=suggestion_engine
    )


def _generate_suggestions_from_database(query: str, max_results: int) -> List[Suggestion]:
    """Generate suggestions using template engine + Dutch matcher"""
    # Get all services and gemeentes
    services = db.get_all_services()
    gemeentes = db.get_all_gemeentes()
    associations = db.get_all_associations()

    # Match services using Dutch NLP
    matcher = DutchMatcher()
    matched_services = matcher.match_services(query, services)

    # Enhance with gemeente information
    for match in matched_services:
        service_id = match['service']['id']
        # Find gemeentes offering this service
        service_associations = [a for a in associations if a['service_id'] == service_id]
        if service_associations:
            match['gemeente'] = service_associations[0]['gemeente_name']

    # Generate question templates
    raw_suggestions = template_engine.generate_suggestions(
        query,
        matched_services,
        max_results
    )

    # Convert to Pydantic models
    return [
        Suggestion(
            suggestion=s['suggestion'],
            confidence=s['confidence'],
            service=ServiceInfo(
                id=s['service']['id'],
                name=s['service']['name'],
                description=s['service']['description'],
                category=s['service']['category']
            ),
            gemeente=s.get('gemeente')
        )
        for s in raw_suggestions
    ]


def _generate_suggestions_from_koop(
    koop_client: KoopAPIClient,
    query: str,
    max_results: int
) -> List[Suggestion]:
    """Generate suggestions using KOOP API"""
    koop_results = koop_client.get_suggestions(query, max_results)

    # Convert KOOP results to our format
    suggestions = []
    for result in koop_results:
        suggestions.append(
            Suggestion(
                suggestion=result.get('suggestion', ''),
                confidence=result.get('confidence', 0.5),
                service=ServiceInfo(
                    id=0,  # KOOP doesn't provide IDs
                    name=result.get('service', ''),
                    description=result.get('description', ''),
                    category=result.get('category', 'Algemeen')
                ),
                gemeente=result.get('gemeente')
            )
        )

    return suggestions
