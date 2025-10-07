"""
Suggestion generation service.
Generates intelligent question suggestions based on partial query input.
"""
import json
import logging
from typing import List, Optional
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.service import Service
from app.models.gemeente import Gemeente
from app.core.redis_client import redis_client
from app.services.question_templates import TemplateEngine, QuestionTemplate
from app.services import dutch_nlp

logger = logging.getLogger(__name__)


class SuggestionService:
    """Service for generating intelligent query suggestions."""

    def __init__(self, db: AsyncSession):
        """
        Initialize suggestion service.

        Args:
            db: Async database session
        """
        self.db = db
        self.template_engine = TemplateEngine()

    async def generate_suggestions(self, query: str) -> List[dict]:
        """
        Generate 3-5 intelligent question suggestions based on query.

        Algorithm:
        1. Check Redis cache for cached suggestions
        2. If cache miss, query services matching query text (ILIKE on name and keywords)
        3. Query gemeentes matching query text (ILIKE on name)
        4. Generate full-text questions combining services + gemeentes
        5. Calculate confidence scores based on match quality
        6. Cache results in Redis (5-minute TTL)
        7. Return top 5 suggestions sorted by confidence

        Args:
            query: Partial query text (min 2 chars)

        Returns:
            List of suggestion dictionaries with confidence scores
        """
        query_lower = query.lower().strip()

        # Try cache first
        cached_suggestions = self._get_cached_suggestions(query_lower)
        if cached_suggestions is not None:
            logger.info(f"Cache hit for query: '{query_lower}'")
            return cached_suggestions

        logger.info(f"Cache miss for query: '{query_lower}'")
        search_pattern = f"%{query_lower}%"

        # Query matching services (limit 20 for performance)
        services = await self._find_matching_services(search_pattern)

        # Query matching gemeentes (limit 8 for performance)
        gemeentes = await self._find_matching_gemeentes(search_pattern)

        # Generate suggestions from matches using template engine
        suggestions = []
        used_templates = []  # Track templates for diversity

        # Strategy 1: Service-specific suggestions (no gemeente)
        for service in services[:5]:
            confidence = self._calculate_service_confidence(query_lower, service)

            # Generate question using template engine
            suggestion_text = self.template_engine.generate_question(
                service=service.name,
                service_category=service.category,
                used_templates=used_templates
            )
            # Track template for diversity
            template = self.template_engine.select_template(
                variables={"service": service.name},
                service_category=service.category,
                used_templates=used_templates
            )
            used_templates.append(template)

            suggestions.append({
                "suggestion": suggestion_text,
                "confidence": confidence,
                "service": {
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "category": service.category
                },
                "gemeente": None
            })

        # Strategy 2: Service + Gemeente combinations
        # Combine top 3 services with top 3 gemeentes
        for service in services[:3]:
            for gemeente in gemeentes[:3]:
                confidence = self._calculate_combined_confidence(
                    query_lower, service, gemeente
                )

                # Generate question using template engine
                suggestion_text = self.template_engine.generate_question(
                    service=service.name,
                    gemeente=gemeente.name,
                    service_category=service.category,
                    used_templates=used_templates
                )
                # Track template for diversity
                template = self.template_engine.select_template(
                    variables={"service": service.name, "gemeente": gemeente.name},
                    service_category=service.category,
                    used_templates=used_templates
                )
                used_templates.append(template)

                suggestions.append({
                    "suggestion": suggestion_text,
                    "confidence": confidence,
                    "service": {
                        "id": service.id,
                        "name": service.name,
                        "description": service.description,
                        "category": service.category
                    },
                    "gemeente": {
                        "id": gemeente.id,
                        "name": gemeente.name,
                        "description": gemeente.description
                    }
                })

        # Strategy 3: Gemeente-specific suggestions (if query matches gemeente)
        if gemeentes:
            for gemeente in gemeentes[:2]:
                confidence = self._calculate_gemeente_confidence(query_lower, gemeente)

                # For gemeente-only, use a simple "Welke diensten" pattern
                # This doesn't fit the template engine well, so keep it simple
                suggestion_text = f"Welke diensten biedt {gemeente.name} aan?"

                suggestions.append({
                    "suggestion": suggestion_text,
                    "confidence": confidence,
                    "service": None,
                    "gemeente": {
                        "id": gemeente.id,
                        "name": gemeente.name,
                        "description": gemeente.description
                    }
                })

        # Sort by confidence (descending) and get top 5
        suggestions.sort(key=lambda x: x["confidence"], reverse=True)
        top_suggestions = suggestions[:5]

        # Cache results
        self._cache_suggestions(query_lower, top_suggestions)

        return top_suggestions

    async def _find_matching_services(self, search_pattern: str) -> List[Service]:
        """
        Find services matching search pattern.

        Searches in:
        - service.name (case-insensitive)
        - service.keywords array (case-insensitive)

        Args:
            search_pattern: SQL ILIKE pattern (e.g., "%park%")

        Returns:
            List of matching Service objects (max 20)
        """
        stmt = (
            select(Service)
            .where(
                or_(
                    func.lower(Service.name).like(search_pattern),
                    # Search in keywords array
                    Service.keywords.any(func.lower(search_pattern.strip("%")))
                )
            )
            .limit(20)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _find_matching_gemeentes(self, search_pattern: str) -> List[Gemeente]:
        """
        Find gemeentes matching search pattern.

        Searches in:
        - gemeente.name (case-insensitive)

        Args:
            search_pattern: SQL ILIKE pattern (e.g., "%amsterdam%")

        Returns:
            List of matching Gemeente objects (max 8)
        """
        stmt = (
            select(Gemeente)
            .where(func.lower(Gemeente.name).like(search_pattern))
            .limit(8)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    def _calculate_service_confidence(self, query: str, service: Service) -> float:
        """
        Calculate confidence score for service-only suggestion with NLP enhancement.

        Scoring logic (enhanced with fuzzy matching):
        - Exact name match: 0.95
        - Name starts with query: 0.85
        - Name contains query: 0.70
        - NLP enhanced match on name: 0.60-0.90 (based on similarity)
        - Keyword exact match: 0.90
        - Keyword starts with query: 0.75
        - Keyword contains query: 0.60
        - NLP enhanced keyword match: 0.55-0.85

        Args:
            query: Lowercase query text
            service: Service object

        Returns:
            Confidence score between 0.0 and 1.0
        """
        service_name_lower = service.name.lower()

        # Check exact name matches first (fastest)
        if query == service_name_lower:
            return 0.95
        elif service_name_lower.startswith(query):
            return 0.85
        elif query in service_name_lower:
            return 0.70

        # Check keyword matches
        best_keyword_score = 0.0
        if service.keywords:
            for keyword in service.keywords:
                keyword_lower = keyword.lower()
                if query == keyword_lower:
                    return 0.90
                elif keyword_lower.startswith(query):
                    best_keyword_score = max(best_keyword_score, 0.75)
                elif query in keyword_lower:
                    best_keyword_score = max(best_keyword_score, 0.60)

        if best_keyword_score > 0:
            return best_keyword_score

        # Use NLP enhanced matching for fuzzy/typo tolerance
        nlp_name_score = dutch_nlp.enhanced_match_score(query, service_name_lower)
        if nlp_name_score >= 0.75:
            # Scale NLP score to 0.60-0.90 range
            return 0.60 + (nlp_name_score - 0.75) * 1.2

        # Check NLP matching on keywords
        if service.keywords:
            best_nlp_keyword_score = 0.0
            for keyword in service.keywords:
                nlp_score = dutch_nlp.enhanced_match_score(query, keyword.lower())
                if nlp_score >= 0.75:
                    # Scale to 0.55-0.85 range
                    scaled_score = 0.55 + (nlp_score - 0.75) * 1.2
                    best_nlp_keyword_score = max(best_nlp_keyword_score, scaled_score)

            if best_nlp_keyword_score > 0:
                return best_nlp_keyword_score

        # Default score for weak matches
        return 0.45

    def _calculate_gemeente_confidence(self, query: str, gemeente: Gemeente) -> float:
        """
        Calculate confidence score for gemeente-only suggestion with NLP enhancement.

        Scoring logic (enhanced with fuzzy/partial matching):
        - Exact name match: 0.90
        - Name starts with query: 0.80
        - Name contains query: 0.65
        - NLP partial match (e.g., "adam" → "amsterdam"): 0.70-0.90

        Args:
            query: Lowercase query text
            gemeente: Gemeente object

        Returns:
            Confidence score between 0.0 and 1.0
        """
        gemeente_name_lower = gemeente.name.lower()

        # Exact matches first
        if query == gemeente_name_lower:
            return 0.90
        elif gemeente_name_lower.startswith(query):
            return 0.80
        elif query in gemeente_name_lower:
            return 0.65

        # Use NLP partial matching for short queries → full names
        nlp_score = dutch_nlp.partial_match_score(query, gemeente_name_lower)
        if nlp_score >= 0.70:
            return nlp_score

        return 0.40

    def _calculate_combined_confidence(
        self, query: str, service: Service, gemeente: Gemeente
    ) -> float:
        """
        Calculate confidence score for combined service + gemeente suggestion.

        Uses weighted average:
        - Service confidence: 70% weight
        - Gemeente confidence: 30% weight
        - Penalty: -0.05 for combined suggestions (less specific)

        Args:
            query: Lowercase query text
            service: Service object
            gemeente: Gemeente object

        Returns:
            Confidence score between 0.0 and 1.0
        """
        service_conf = self._calculate_service_confidence(query, service)
        gemeente_conf = self._calculate_gemeente_confidence(query, gemeente)

        # Weighted average with penalty for combined complexity
        combined = (service_conf * 0.7) + (gemeente_conf * 0.3) - 0.05

        # Clamp to valid range
        return max(0.0, min(1.0, combined))

    def _get_cached_suggestions(self, query: str) -> Optional[List[dict]]:
        """
        Retrieve cached suggestions from Redis.

        Cache key format: suggestions:{lowercase_query}

        Args:
            query: Lowercase query text

        Returns:
            List of cached suggestions or None if cache miss
        """
        cache_key = f"suggestions:{query}"

        try:
            cached_json = redis_client.get(cache_key)
            if cached_json:
                return json.loads(cached_json)
            return None
        except Exception as e:
            logger.warning(f"Redis cache read error: {e}")
            return None

    def _cache_suggestions(self, query: str, suggestions: List[dict]) -> None:
        """
        Cache suggestions in Redis with 5-minute TTL.

        Cache key format: suggestions:{lowercase_query}
        TTL: 300 seconds (5 minutes)

        Args:
            query: Lowercase query text
            suggestions: List of suggestion dictionaries to cache
        """
        cache_key = f"suggestions:{query}"
        ttl = 300  # 5 minutes

        try:
            suggestions_json = json.dumps(suggestions)
            redis_client.setex(cache_key, ttl, suggestions_json)
            logger.info(f"Cached suggestions for query: '{query}'")
        except Exception as e:
            logger.warning(f"Redis cache write error: {e}")
