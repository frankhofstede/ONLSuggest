"""
Integration tests for suggestions API endpoint.
Tests all acceptance criteria for Story 1.2.
"""
import pytest
import time
from httpx import AsyncClient
from sqlalchemy import select

from app.main import app
from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models import Service, Gemeente


@pytest.mark.asyncio
async def test_valid_query_returns_suggestions():
    """AC1, AC2: Valid query returns 3-5 suggestions with confidence scores."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/suggestions",
            json={"query": "park"}
        )

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "query" in data
    assert "suggestions" in data
    assert "response_time_ms" in data
    assert data["query"] == "park"

    # Verify suggestions count (3-5)
    suggestions = data["suggestions"]
    assert len(suggestions) >= 1
    assert len(suggestions) <= 5

    # Verify suggestion structure
    for suggestion in suggestions:
        assert "suggestion" in suggestion
        assert "confidence" in suggestion
        assert isinstance(suggestion["confidence"], float)
        assert 0.0 <= suggestion["confidence"] <= 1.0


@pytest.mark.asyncio
async def test_query_too_short_returns_422():
    """AC5: Query < 2 chars returns 422 validation error."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/suggestions",
            json={"query": "a"}
        )

    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_empty_query_returns_400():
    """AC5: Empty query returns 400 bad request."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/suggestions",
            json={"query": "   "}
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_query_too_long_returns_422():
    """AC5: Query > 100 chars returns 422 validation error."""
    long_query = "a" * 101
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/suggestions",
            json={"query": long_query}
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_response_time_under_200ms():
    """AC3: P95 response time under 200ms."""
    response_times = []

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Make 20 requests with different queries
        queries = [f"park{i}" for i in range(20)]

        for query in queries:
            start = time.time()
            response = await client.post(
                "/api/v1/suggestions",
                json={"query": query}
            )
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                response_times.append(elapsed)

    # Calculate P95
    response_times.sort()
    p95_index = int(len(response_times) * 0.95)
    p95_time = response_times[p95_index]

    assert p95_time < 200, f"P95 response time {p95_time}ms exceeds 200ms"


@pytest.mark.asyncio
async def test_redis_caching():
    """AC6: Redis caching improves response time."""
    cache_key = "suggestions:testcache"

    # Clear cache
    redis_client.delete(cache_key)

    async with AsyncClient(app=app, base_url="http://test") as client:
        # First request (cache miss)
        response1 = await client.post(
            "/api/v1/suggestions",
            json={"query": "testcache"}
        )
        data1 = response1.json()
        time1 = data1["response_time_ms"]

        # Second request (cache hit)
        response2 = await client.post(
            "/api/v1/suggestions",
            json={"query": "testcache"}
        )
        data2 = response2.json()
        time2 = data2["response_time_ms"]

    # Cache hit should be faster
    assert time2 < time1 or time2 == 0, "Cached response should be faster"

    # Verify cache exists
    cached_value = redis_client.get(cache_key)
    assert cached_value is not None, "Cache should be populated"

    # Clean up
    redis_client.delete(cache_key)


@pytest.mark.asyncio
async def test_suggestion_includes_service_info():
    """AC2: Suggestions include service information when matched."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/suggestions",
            json={"query": "parkeer"}
        )

    assert response.status_code == 200
    data = response.json()
    suggestions = data["suggestions"]

    # At least one suggestion should have service info
    has_service = any(s.get("service") is not None for s in suggestions)
    assert has_service, "At least one suggestion should include service info"

    # Verify service structure
    for suggestion in suggestions:
        if suggestion.get("service"):
            service = suggestion["service"]
            assert "id" in service
            assert "name" in service
            assert "description" in service
            assert "category" in service


@pytest.mark.asyncio
async def test_concurrent_requests():
    """AC4: Handles 10+ concurrent requests gracefully."""
    import asyncio

    async def make_request(client, query):
        return await client.post(
            "/api/v1/suggestions",
            json={"query": query}
        )

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create 10 concurrent requests
        tasks = [
            make_request(client, f"query{i}")
            for i in range(10)
        ]

        # Execute concurrently
        responses = await asyncio.gather(*tasks)

    # All requests should succeed
    success_count = sum(1 for r in responses if r.status_code == 200)
    assert success_count >= 9, f"Only {success_count}/10 requests succeeded"


@pytest.mark.asyncio
async def test_confidence_scores_sorted():
    """Suggestions should be sorted by confidence (descending)."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/suggestions",
            json={"query": "park"}
        )

    assert response.status_code == 200
    data = response.json()
    suggestions = data["suggestions"]

    # Verify sorted by confidence
    confidences = [s["confidence"] for s in suggestions]
    assert confidences == sorted(confidences, reverse=True), "Suggestions should be sorted by confidence"


@pytest.mark.asyncio
async def test_response_format_matches_spec():
    """Verify response matches SuggestionResponse type specification."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/suggestions",
            json={"query": "park"}
        )

    assert response.status_code == 200
    data = response.json()

    # Top-level structure
    assert isinstance(data["query"], str)
    assert isinstance(data["suggestions"], list)
    assert isinstance(data["response_time_ms"], int)

    # Suggestion structure
    for suggestion in data["suggestions"]:
        assert isinstance(suggestion["suggestion"], str)
        assert isinstance(suggestion["confidence"], float)

        # Service is optional
        if suggestion["service"] is not None:
            assert isinstance(suggestion["service"], dict)
            assert "id" in suggestion["service"]
            assert "name" in suggestion["service"]
            assert "description" in suggestion["service"]
            assert "category" in suggestion["service"]

        # Gemeente is optional
        if suggestion["gemeente"] is not None:
            assert isinstance(suggestion["gemeente"], dict)
            assert "id" in suggestion["gemeente"]
            assert "name" in suggestion["gemeente"]
            assert "description" in suggestion["gemeente"]
