"""
Suggestions API routes
Epic 1: Query Suggestion Engine
"""
import time
from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.suggestion import SuggestionRequest, SuggestionResponse
from app.models.database import db
from app.services import template_engine, dutch_matcher, koop_client
from app.core.config import settings

router = APIRouter()


def _generate_suggestions_from_koop(query: str, max_results: int = 5):
    """
    Generate suggestions using KOOP API
    Story 3.2: KOOP API Integration
    """
    try:
        return koop_client.koop_client.get_suggestions(query, max_results)
    except koop_client.KoopAPIError as e:
        raise HTTPException(status_code=500, detail=f"KOOP API error: {str(e)}")


def _generate_suggestions_from_database(query: str, max_results: int = 5):
    """
    Generate suggestions using real database, template engine, and Dutch matcher
    Stories 1.3 + 1.4: Template Engine + Dutch Language Processing
    """
    try:
        # Fetch all data from database
        all_gemeentes = db.get_all_gemeentes()
        all_services = db.get_all_services()
        all_associations = db.get_all_associations()

        # Match query against gemeentes and services
        gemeente_matches = dutch_matcher.dutch_matcher.match_gemeentes(query, all_gemeentes)
        service_matches = dutch_matcher.dutch_matcher.match_services(query, all_services, min_confidence=0.5)

        # Combine matches based on associations
        combined_matches = dutch_matcher.dutch_matcher.combine_matches(
            query=query,
            gemeente_matches=gemeente_matches,
            service_matches=service_matches,
            associations=all_associations,
            max_results=max_results * 2  # Get more candidates
        )

        # Generate question suggestions using template engine
        suggestions = template_engine.template_engine.generate_suggestions(
            query=query,
            matched_services=combined_matches,
            max_results=max_results
        )

        return suggestions

    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return []


def _get_mock_suggestions(query: str, max_results: int):
    """Fallback mock data when database is unavailable"""
    return [
        {
            "suggestion": f"Hoe kan ik {query} regelen?",
            "confidence": 0.75,
            "service": {
                "id": 999,
                "name": f"Algemene informatie over {query}",
                "description": "Algemene vraag",
                "category": "Algemeen"
            },
            "gemeente": None
        }
    ]


@router.post("/suggestions", response_model=SuggestionResponse)
async def get_suggestions(request: SuggestionRequest):
    """
    Generate query suggestions
    Story 1.2: API Endpoint for Suggestions
    """
    start_time = time.time()

    # Validate input
    if not request.query or len(request.query) < settings.QUERY_MIN_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query must be at least {settings.QUERY_MIN_LENGTH} characters"
        )

    # Check which suggestion engine to use
    try:
        suggestion_engine = db.get_setting('suggestion_engine') or 'template'
    except:
        suggestion_engine = "template"  # Fallback

    # Generate suggestions based on selected engine with fallback
    fallback_occurred = False
    fallback_reason = None

    if suggestion_engine == "koop":
        try:
            suggestions = _generate_suggestions_from_koop(request.query, request.max_results)
        except Exception as e:
            # Fallback to template engine on KOOP failure
            print(f"[WARNING] KOOP API failed, falling back to template: {e}")
            suggestion_engine = "template"
            fallback_occurred = True
            fallback_reason = str(e)

            try:
                suggestions = _generate_suggestions_from_database(request.query, request.max_results)
            except:
                suggestions = _get_mock_suggestions(request.query, request.max_results)

    if suggestion_engine == "template":
        try:
            suggestions = _generate_suggestions_from_database(request.query, request.max_results)
        except Exception as e:
            # Fallback to mock data if database unavailable
            print(f"[WARNING] Database error, using mock data: {e}")
            suggestions = _get_mock_suggestions(request.query, request.max_results)

    response_time_ms = (time.time() - start_time) * 1000

    return SuggestionResponse(
        query=request.query,
        suggestions=suggestions,
        response_time_ms=response_time_ms,
        using_database=True,  # Always try to use database
        suggestion_engine=suggestion_engine,
        fallback_occurred=fallback_occurred if fallback_occurred else None,
        fallback_reason=fallback_reason if fallback_reason else None
    )
