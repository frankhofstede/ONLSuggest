
# Tech Spec: Epic 1 - Query Suggestion Engine

**Author:** Winston (Architect)
**Date:** 2025-10-07
**Epic:** Epic 1 - Query Suggestion Engine
**Status:** Draft

---

## Epic Overview

**Epic Goal:** Build the core suggestion generation system that transforms partial Dutch input into full-text questions

**Business Value:** Proves the core value proposition - that citizens can find services through conversational query suggestions without knowing official terminology

**Stories Covered:**
- Story 1.1: Basic Input Field with Character Minimum Validation
- Story 1.2: Real-time Suggestion Generation API Endpoint
- Story 1.3: Question Template Engine for Gemeente/Service Combinations
- Story 1.4: Dutch Language Processing and Natural Question Formation
- Story 1.5: Sub-200ms Performance Optimization
- Story 1.6: Graceful Error Handling and Fallback Messaging

**Dependencies:** None (can start immediately)

**Estimated Effort:** 3-4 weeks

---

## Architecture Context

**From solution-architecture.md:**

**Tech Stack:**
- Backend: FastAPI 0.109.0, Python 3.11+
- Database: PostgreSQL 15+ with native full-text search
- ORM: SQLAlchemy 2.0.25 (async)
- NLP: spaCy 3.7.2 + nl_core_news_sm (Dutch model)
- Caching: functools.lru_cache + Redis 7.2
- Frontend: React 18.2.0, TypeScript 5.3.0, Tailwind CSS 3.4.0
- State: TanStack Query 5.17.0 + React Context API
- Server: Uvicorn 0.27.0

**Performance Target:** <200ms P95 latency for suggestion generation

**Architecture Pattern:** Monolith, Monorepo, SPA, REST API

---

## Story-by-Story Technical Breakdown

### Story 1.1: Basic Input Field with Character Minimum Validation

**Acceptance Criteria:**
- Input field accepts Dutch text input (UTF-8)
- Minimum 2 characters required before suggestions trigger
- Clear visual feedback when minimum not met
- Input field is prominently displayed on page load
- Supports keyboard navigation

**Frontend Implementation:**

**Component: `frontend/src/components/public/SearchBox.tsx`**

```typescript
// Type definitions
interface SearchBoxProps {
  onQueryChange: (query: string) => void;
  placeholder?: string;
  minChars?: number;
}

// State management
- Local state: `query` (string)
- Validation state: `isValid` (boolean)
- Debounced query: `debouncedQuery` (string, 150ms delay)

// Visual feedback
- Gray border when empty
- Red border when 1 char (min not met)
- Blue border when >=2 chars (valid)
- Helper text: "Typ minimaal 2 tekens" when invalid

// Keyboard support
- Tab: Focus input
- Escape: Clear input
- Arrow Down: Focus first suggestion (when list visible)
```

**Technical Details:**

**Debouncing:**
```typescript
// Use custom hook or lodash.debounce
import { debounce } from '../utils/debounce';

const debouncedQuery = useMemo(
  () => debounce((value: string) => {
    if (value.length >= 2) {
      onQueryChange(value);
    }
  }, 150),
  [onQueryChange]
);
```

**UTF-8 Support:**
- React handles UTF-8 automatically
- Test with Dutch characters: ë, ï, ü, é, etc.
- Ensure database and API also use UTF-8 encoding

**Validation Logic:**
```typescript
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const value = e.target.value;
  setQuery(value);

  if (value.length >= 2) {
    setIsValid(true);
    debouncedQuery(value);
  } else {
    setIsValid(false);
  }
};
```

**Accessibility:**
- `aria-label="Zoek naar gemeentediensten"`
- `role="combobox"`
- `aria-expanded={suggestionsVisible}`
- `aria-activedescendant={activeSuggestionId}`

**Dependencies:**
- react-hook-form 7.49.0 (optional, for advanced validation)
- Custom debounce utility

**Testing:**
- Unit test: Verify 2-char minimum
- Unit test: Verify debounce works (150ms delay)
- E2E test: Type "pa" → expect suggestions to appear

---

### Story 1.2: Real-time Suggestion Generation API Endpoint

**Acceptance Criteria:**
- POST endpoint accepts partial query (min 2 chars)
- Returns 3-5 suggested questions in JSON format
- Response time under 200ms (P95)
- Handles concurrent requests gracefully
- Returns error codes for invalid input

**Backend Implementation:**

**API Endpoint: `backend/app/routers/suggestions.py`**

```python
# Endpoint definition
POST /api/suggestions

# Request schema (Pydantic)
class SuggestionRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=100)

    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

# Response schema
class SuggestionItem(BaseModel):
    id: str  # UUID
    question: str
    gemeente: str
    service_id: int
    service_name: str
    confidence: float  # 0.0-1.0

class SuggestionResponse(BaseModel):
    suggestions: List[SuggestionItem]
    query: str
    generated_at: datetime
    cached: bool

# Implementation
@router.post("/api/suggestions", response_model=SuggestionResponse)
@limiter.limit("10/minute")  # Rate limiting
async def generate_suggestions(
    request: Request,
    body: SuggestionRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    try:
        suggestions = await suggestion_service.generate(
            query=body.query,
            db=db,
            redis=redis
        )

        return SuggestionResponse(
            suggestions=suggestions,
            query=body.query,
            generated_at=datetime.utcnow(),
            cached=suggestions.was_cached if hasattr(suggestions, 'was_cached') else False
        )

    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Suggestion generation failed"
        )
```

**Performance Considerations:**
- **Async I/O:** All database and Redis calls use `await`
- **Connection pooling:** Reuse SQLAlchemy async sessions
- **Rate limiting:** slowapi for 10 requests/minute per IP
- **Timeout:** Set 180ms timeout (safety margin for 200ms P95)

**Error Handling:**
```python
# HTTP 400: Invalid input
if len(query) < 2:
    raise HTTPException(status_code=400, detail="Query must be at least 2 characters")

# HTTP 500: Server error
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Suggestion generation failed")
```

**Concurrent Request Handling:**
- FastAPI uses async workers (Uvicorn)
- PostgreSQL MVCC handles concurrent writes without locks
- Redis provides atomic operations
- Target: 50 concurrent requests (POC)

**Dependencies:**
- FastAPI 0.109.0
- Pydantic 2.5.0
- slowapi 0.1.9 (rate limiting)
- structlog 24.1.0 (logging)

**Testing:**
- Unit test: POST with "parkeren" → expect 3-5 suggestions
- Unit test: POST with "p" → expect 400 error
- Integration test: Database + Redis integration
- Load test: 50 concurrent requests, verify <200ms P95

---

### Story 1.3: Question Template Engine for Gemeente/Service Combinations

**Acceptance Criteria:**
- Template system supports multiple question formats ("Hoe...", "Waar...", "Wat kost...")
- Templates dynamically insert gemeente names and service terms
- Generated questions are grammatically correct Dutch
- Template selection based on query intent/context
- At least 5 different question templates available

**Backend Implementation:**

**Service: `backend/app/services/template_engine.py`**

**Template Data Structure:**

```python
from dataclasses import dataclass
from enum import Enum

class QuestionType(Enum):
    HOW_TO = "how_to"
    COST = "cost"
    WHERE = "where"
    WHEN = "when"
    REQUIREMENTS = "requirements"

@dataclass
class Template:
    type: QuestionType
    pattern: str
    requires_action: bool = True
    requires_article: bool = True

# Template definitions
TEMPLATES = {
    QuestionType.HOW_TO: Template(
        type=QuestionType.HOW_TO,
        pattern="Hoe {action} ik {article} {service} in {gemeente}?",
        requires_action=True,
        requires_article=True
    ),
    QuestionType.COST: Template(
        type=QuestionType.COST,
        pattern="Wat kost {article} {service} in {gemeente}?",
        requires_action=False,
        requires_article=True
    ),
    QuestionType.WHERE: Template(
        type=QuestionType.WHERE,
        pattern="Waar kan ik {article} {service} {action} in {gemeente}?",
        requires_action=True,
        requires_article=True
    ),
    QuestionType.WHEN: Template(
        type=QuestionType.WHEN,
        pattern="Wanneer kan ik {article} {service} {action} in {gemeente}?",
        requires_action=True,
        requires_article=True
    ),
    QuestionType.REQUIREMENTS: Template(
        type=QuestionType.REQUIREMENTS,
        pattern="Wat heb ik nodig voor {article} {service} in {gemeente}?",
        requires_action=False,
        requires_article=True
    )
}
```

**Template Rendering Logic:**

```python
class TemplateEngine:
    def __init__(self):
        self.nlp = spacy.load("nl_core_news_sm")

    @lru_cache(maxsize=500)
    def render(
        self,
        gemeente: str,
        service: str,
        query: str,
        template_type: QuestionType = QuestionType.HOW_TO
    ) -> str:
        """
        Render a question template with proper Dutch grammar.

        Args:
            gemeente: Name of gemeente (e.g., "Amsterdam")
            service: Name of service (e.g., "parkeervergunning")
            query: Original user query (for action inference)
            template_type: Type of question template

        Returns:
            Grammatically correct Dutch question
        """
        template = TEMPLATES[template_type]

        # Determine article (de/het/een)
        article = self._get_article(service)

        # Determine action verb
        action = self._infer_action(query, service) if template.requires_action else ""

        # Render template
        question = template.pattern.format(
            gemeente=gemeente,
            service=service,
            article=article,
            action=action
        )

        return question

    def _get_article(self, noun: str) -> str:
        """Determine Dutch article (de/het/een) for a noun."""
        # Simplified rules (full implementation needs Dutch grammar library)
        # For POC, use heuristics or predefined dictionary

        # Common patterns
        if noun.endswith(('ing', 'heid', 'tie', 'uur')):
            return "de"
        if noun.endswith(('je', 'sel', 'isme')):
            return "het"

        # Default to "een" (indefinite article)
        return "een"

    def _infer_action(self, query: str, service: str) -> str:
        """Infer action verb from query and service context."""
        # Action keywords mapping
        action_keywords = {
            'aanvragen': ['aanvragen', 'aanvraag', 'vraag', 'krijgen'],
            'verlengen': ['verlengen', 'verleng'],
            'betalen': ['betalen', 'betaal', 'kost'],
            'ophalen': ['ophalen', 'halen', 'afhalen'],
            'regelen': ['regelen', 'regel']
        }

        query_lower = query.lower()

        # Check for explicit action keywords
        for action, keywords in action_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return action

        # Default action based on service type
        if 'vergunning' in service.lower():
            return 'aanvragen'
        if 'paspoort' in service.lower() or 'rijbewijs' in service.lower():
            return 'aanvragen'

        # Fallback
        return 'regelen'

    def select_template(
        self,
        query: str,
        service_category: str = None
    ) -> QuestionType:
        """Select appropriate template based on query intent."""
        query_lower = query.lower()

        # Intent detection
        if any(kw in query_lower for kw in ['kost', 'prijs', 'betalen']):
            return QuestionType.COST
        if any(kw in query_lower for kw in ['waar', 'locatie', 'adres']):
            return QuestionType.WHERE
        if any(kw in query_lower for kw in ['wanneer', 'tijd', 'datum']):
            return QuestionType.WHEN
        if any(kw in query_lower for kw in ['nodig', 'document', 'meebrengen']):
            return QuestionType.REQUIREMENTS

        # Default to HOW_TO
        return QuestionType.HOW_TO
```

**Grammar Handling:**

For production, consider integrating:
- **python-dutchlanguage** (if available)
- **Pattern.nl** library for Dutch language processing
- Or maintain predefined dictionary of common service terms with correct articles

**Caching:**
- `@lru_cache(maxsize=500)` on `render()` method
- Cache key: `(gemeente, service, query, template_type)`
- Estimated hit rate: 40-60% (common query variations)

**Dependencies:**
- spaCy 3.7.2
- functools (built-in)

**Testing:**
- Unit test: "parkeren amsterdam" → "Hoe vraag ik een parkeervergunning aan in Amsterdam?"
- Unit test: "kost paspoort" → "Wat kost een paspoort in {gemeente}?"
- Unit test: Verify article selection (de/het/een)
- Unit test: Verify action inference (aanvragen/verlengen/etc.)

---

### Story 1.4: Dutch Language Processing and Natural Question Formation

**Acceptance Criteria:**
- Handles common Dutch spelling variations
- Recognizes gemeente names (full and partial)
- Identifies service keywords in partial input
- Handles typos gracefully (fuzzy matching)
- Prioritizes more relevant suggestions first

**Backend Implementation:**

**Service: `backend/app/services/nlp_processor.py`**

```python
import spacy
from rapidfuzz import fuzz, process
from functools import lru_cache

class DutchNLPProcessor:
    def __init__(self):
        # Load Dutch language model
        self.nlp = spacy.load("nl_core_news_sm")

        # Preload gemeente/service data for fuzzy matching
        self._gemeente_cache = {}
        self._service_cache = {}

    async def initialize(self, db: AsyncSession):
        """Preload data for fast fuzzy matching."""
        # Load all gemeentes
        gemeentes = await db.execute(
            select(Gemeente.id, Gemeente.name)
        )
        self._gemeente_cache = {
            g.id: g.name for g in gemeentes.scalars().all()
        }

        # Load all services
        services = await db.execute(
            select(Service.id, Service.name, Service.keywords)
        )
        self._service_cache = {
            s.id: (s.name, s.keywords) for s in services.scalars().all()
        }

    @lru_cache(maxsize=1000)
    def lemmatize(self, text: str) -> List[str]:
        """
        Extract lemmas (base forms) from Dutch text.

        Args:
            text: User query (e.g., "parkeren amsterdam")

        Returns:
            List of lemmas (e.g., ["parkeren", "amsterdam"])
        """
        doc = self.nlp(text.lower())
        return [token.lemma_ for token in doc if not token.is_stop]

    def fuzzy_match_gemeente(
        self,
        query: str,
        threshold: int = 70
    ) -> List[Tuple[int, str, int]]:
        """
        Fuzzy match query against gemeente names.

        Args:
            query: User query
            threshold: Minimum similarity score (0-100)

        Returns:
            List of (gemeente_id, gemeente_name, score) tuples
        """
        matches = process.extract(
            query,
            self._gemeente_cache.values(),
            scorer=fuzz.partial_ratio,
            limit=5
        )

        # Convert to (id, name, score)
        results = []
        for name, score, _ in matches:
            if score >= threshold:
                gemeente_id = next(
                    id for id, n in self._gemeente_cache.items() if n == name
                )
                results.append((gemeente_id, name, score))

        return results

    def fuzzy_match_service(
        self,
        query: str,
        threshold: int = 60
    ) -> List[Tuple[int, str, int]]:
        """
        Fuzzy match query against service names and keywords.

        Args:
            query: User query
            threshold: Minimum similarity score (0-100)

        Returns:
            List of (service_id, service_name, score) tuples
        """
        lemmas = self.lemmatize(query)
        query_text = " ".join(lemmas)

        # Match against service names
        service_texts = {
            sid: f"{name} {keywords}"
            for sid, (name, keywords) in self._service_cache.items()
        }

        matches = process.extract(
            query_text,
            service_texts.values(),
            scorer=fuzz.token_set_ratio,
            limit=10
        )

        # Convert to (id, name, score)
        results = []
        for matched_text, score, _ in matches:
            if score >= threshold:
                service_id = next(
                    sid for sid, text in service_texts.items() if text == matched_text
                )
                service_name = self._service_cache[service_id][0]
                results.append((service_id, service_name, score))

        return results

    def extract_intent_keywords(self, query: str) -> Dict[str, bool]:
        """
        Extract intent signals from query.

        Returns:
            Dict with intent flags (e.g., {"cost_query": True, "location_query": False})
        """
        query_lower = query.lower()

        return {
            "cost_query": any(kw in query_lower for kw in ['kost', 'prijs', 'betalen']),
            "location_query": any(kw in query_lower for kw in ['waar', 'adres']),
            "time_query": any(kw in query_lower for kw in ['wanneer', 'datum']),
            "requirement_query": any(kw in query_lower for kw in ['nodig', 'meebrengen'])
        }
```

**Fuzzy Matching Strategy:**

**Library:** rapidfuzz (faster than fuzzywuzzy)

**Scoring Algorithms:**
- `fuzz.partial_ratio`: For gemeente matching (handles partial names like "ams" → "Amsterdam")
- `fuzz.token_set_ratio`: For service matching (handles word order variations)

**Thresholds:**
- Gemeente: 70% (stricter, to avoid false positives)
- Service: 60% (more lenient, to handle typos)

**Performance:**
- rapidfuzz is C-optimized (very fast)
- Preloaded caches avoid database queries
- Lemmatization cached with @lru_cache

**Spelling Variation Handling:**

Common Dutch variations:
- "parkeren" / "parkeer" / "parkeerplaats" → lemmatize to "parkeren"
- "paspoort" / "pasport" (typo) → fuzzy match to "paspoort"
- "gemeente" / "gemeentes" → lemmatize handles plural

**Dependencies:**
- spaCy 3.7.2
- nl_core_news_sm (Dutch model)
- rapidfuzz 3.5.2
- functools (built-in)

**Testing:**
- Unit test: "parkeren" → lemma "parkeren"
- Unit test: "ams" → fuzzy match to "Amsterdam" (score >= 70)
- Unit test: "pasport" (typo) → fuzzy match to "paspoort"
- Unit test: "parkeerplaats" → lemma "parkeerplaats" (stem to "parkeer")

---

### Story 1.5: Sub-200ms Performance Optimization

**Acceptance Criteria:**
- P95 response time under 200ms
- P99 response time under 350ms
- No visible loading indicators needed
- Performance tested with 50 gemeentes, 100 services
- Performance holds under 10 concurrent users

**Backend Implementation:**

**Service: `backend/app/services/suggestion_service.py`**

**Algorithm with Performance Breakdown:**

```python
import asyncio
from datetime import datetime
import hashlib
import json

class SuggestionService:
    def __init__(self, nlp_processor, template_engine, db, redis):
        self.nlp = nlp_processor
        self.templates = template_engine
        self.db = db
        self.redis = redis

    async def generate(
        self,
        query: str,
        limit: int = 5
    ) -> List[SuggestionItem]:
        """
        Generate 3-5 suggestions from partial query.
        Target: <200ms P95 latency

        Performance breakdown:
        1. Validation: 1-2ms
        2. Cache check: 2-5ms
        3. NLP processing: 10-20ms
        4. Fuzzy matching: 20-40ms
        5. Association lookup: 5-10ms (cached)
        6. Scoring: 10-20ms
        7. Template rendering: 20-40ms
        8. Cache write: 2-5ms
        Total: 70-160ms
        """
        start_time = datetime.now()

        # Step 1: Validation (1-2ms)
        if len(query) < 2:
            raise ValueError("Query must be at least 2 characters")

        normalized_query = query.lower().strip()

        # Step 2: Cache check (2-5ms)
        cache_key = f"suggestion:{hashlib.md5(normalized_query.encode()).hexdigest()}"
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # Step 3: NLP processing (10-20ms)
        lemmas = self.nlp.lemmatize(normalized_query)

        # Step 4: Fuzzy matching (20-40ms) - Run in parallel
        gemeente_matches, service_matches = await asyncio.gather(
            self._match_gemeentes(normalized_query),
            self._match_services(normalized_query, lemmas)
        )

        # Step 5: Association lookup (5-10ms, cached)
        candidates = await self._build_candidates(
            gemeente_matches,
            service_matches,
            normalized_query
        )

        # Step 6: Relevance scoring (10-20ms)
        scored_candidates = self._score_candidates(
            candidates,
            normalized_query,
            lemmas
        )

        # Step 7: Template rendering (20-40ms)
        top_candidates = sorted(scored_candidates, reverse=True)[:limit]
        suggestions = await self._render_suggestions(
            top_candidates,
            normalized_query
        )

        # Step 8: Cache result (2-5ms)
        await self.redis.setex(
            cache_key,
            300,  # 5 minutes TTL
            json.dumps([s.dict() for s in suggestions])
        )

        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        logger.info(f"Suggestion generation took {elapsed:.2f}ms")

        return suggestions

    async def _match_gemeentes(self, query: str) -> List[Tuple]:
        """Fuzzy match gemeentes (threshold 70%)."""
        return self.nlp.fuzzy_match_gemeente(query, threshold=70)

    async def _match_services(
        self,
        query: str,
        lemmas: List[str]
    ) -> List[Tuple]:
        """Fuzzy match services (threshold 60%)."""
        return self.nlp.fuzzy_match_service(query, threshold=60)

    @lru_cache(maxsize=1000)
    async def _get_associations(self, gemeente_id: int) -> List[int]:
        """
        Get service IDs for a gemeente (cached).

        Cache hit rate: ~80% (gemeentes are stable)
        """
        result = await self.db.execute(
            select(Association.service_id)
            .where(Association.gemeente_id == gemeente_id)
        )
        return [row[0] for row in result.all()]

    async def _build_candidates(
        self,
        gemeente_matches: List[Tuple],
        service_matches: List[Tuple],
        query: str
    ) -> List[Candidate]:
        """
        Build candidate suggestions from matches.

        Returns:
            List of (gemeente, service, combined_score) tuples
        """
        candidates = []

        for gem_id, gem_name, gem_score in gemeente_matches:
            # Get services for this gemeente
            service_ids = await self._get_associations(gem_id)

            for svc_id, svc_name, svc_score in service_matches:
                if svc_id in service_ids:
                    # Valid gemeente-service combination
                    combined_score = (gem_score + svc_score) / 2
                    candidates.append(
                        Candidate(
                            gemeente_id=gem_id,
                            gemeente_name=gem_name,
                            service_id=svc_id,
                            service_name=svc_name,
                            score=combined_score
                        )
                    )

        return candidates

    def _score_candidates(
        self,
        candidates: List[Candidate],
        query: str,
        lemmas: List[str]
    ) -> List[Tuple[float, Candidate]]:
        """
        Re-rank candidates with additional signals.

        Scoring factors:
        - Fuzzy match score (60%)
        - Keyword overlap (20%)
        - Popularity (20%, from Redis analytics)
        """
        scored = []

        for candidate in candidates:
            # Base score from fuzzy matching
            base_score = candidate.score

            # Keyword overlap boost
            service_keywords = candidate.service_name.lower().split()
            overlap = len(set(lemmas) & set(service_keywords))
            keyword_boost = overlap * 10  # +10 points per matching keyword

            # Popularity boost (TODO: implement analytics)
            popularity_boost = 0

            final_score = base_score + keyword_boost + popularity_boost
            scored.append((final_score, candidate))

        return scored

    async def _render_suggestions(
        self,
        scored_candidates: List[Tuple[float, Candidate]],
        query: str
    ) -> List[SuggestionItem]:
        """
        Render final suggestions using templates.
        """
        suggestions = []

        for score, candidate in scored_candidates:
            # Select template based on query intent
            template_type = self.templates.select_template(query)

            # Render question
            question = self.templates.render(
                gemeente=candidate.gemeente_name,
                service=candidate.service_name,
                query=query,
                template_type=template_type
            )

            suggestions.append(
                SuggestionItem(
                    id=str(uuid.uuid4()),
                    question=question,
                    gemeente=candidate.gemeente_name,
                    service_id=candidate.service_id,
                    service_name=candidate.service_name,
                    confidence=min(score / 100, 1.0)  # Normalize to 0-1
                )
            )

        return suggestions
```

**Performance Optimization Strategies:**

**1. Database Optimization:**
```sql
-- Indexes (already in schema)
CREATE INDEX idx_gemeentes_name ON gemeentes(name);
CREATE INDEX idx_services_name ON services(name);
CREATE INDEX idx_associations_gemeente ON gemeente_service_associations(gemeente_id);

-- FTS5 for Dutch full-text search
CREATE VIRTUAL TABLE services_fts USING fts5(...);
```

**2. In-Memory Caching:**
```python
# LRU cache for hot data
@lru_cache(maxsize=1000)
def get_associations(gemeente_id: int):
    # Cache hit rate: ~80%
    # Lookup time: <1ms
    ...
```

**3. Redis Caching:**
```python
# Cache suggestion results
cache_key = f"suggestion:{query_hash}"
ttl = 300  # 5 minutes

# Cache hit rate target: 60%
# Lookup time: 2-5ms
```

**4. Async I/O:**
```python
# Parallel execution
gemeente_matches, service_matches = await asyncio.gather(
    match_gemeentes(query),
    match_services(query)
)
```

**5. Connection Pooling:**
```python
# SQLAlchemy async engine
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
```

**Performance Testing:**

**Load Testing Script:** `backend/tests/load_test_suggestions.py`

```python
import asyncio
import aiohttp
import time

async def test_suggestion_latency():
    """Test P95/P99 latency with 50 concurrent requests."""
    queries = ["parkeren", "paspoort", "rijbewijs", "afval", ...]
    latencies = []

    async with aiohttp.ClientSession() as session:
        for _ in range(50):
            tasks = [
                session.post("/api/suggestions", json={"query": q})
                for q in queries
            ]

            start = time.time()
            responses = await asyncio.gather(*tasks)
            end = time.time()

            for r in responses:
                latencies.append((end - start) * 1000 / len(tasks))

    # Calculate percentiles
    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f"P95: {p95:.2f}ms")
    print(f"P99: {p99:.2f}ms")

    assert p95 < 200, f"P95 latency {p95:.2f}ms exceeds 200ms target"
```

**Dependencies:**
- asyncio (built-in)
- Redis (aioredis 2.0.1)
- SQLAlchemy async (2.0.25)
- rapidfuzz 3.5.2

**Monitoring:**

```python
# Structured logging for performance tracking
logger.info(
    "suggestion_generated",
    query=query,
    latency_ms=elapsed,
    cache_hit=cached is not None,
    num_suggestions=len(suggestions)
)
```

**Testing:**
- Load test: 50 concurrent requests → P95 < 200ms
- Stress test: 100 gemeentes, 200 services → verify performance holds
- Cache test: Verify 60%+ cache hit rate for common queries

---

### Story 1.6: Graceful Error Handling and Fallback Messaging

**Acceptance Criteria:**
- Network errors show friendly Dutch message
- No suggestions found shows helpful guidance
- System errors don't break the interface
- Users can retry without refreshing page
- Error messages in Dutch

**Frontend Implementation:**

**Component: `frontend/src/components/public/SuggestionList.tsx`**

```typescript
interface SuggestionListProps {
  query: string;
  onSuggestionClick: (suggestion: Suggestion) => void;
}

const SuggestionList: React.FC<SuggestionListProps> = ({ query, onSuggestionClick }) => {
  const { data, error, isLoading, refetch } = useSuggestions(query);

  // Loading state (should rarely be visible if <200ms)
  if (isLoading) {
    return (
      <div className="text-gray-500 text-sm p-4">
        Suggesties laden...
      </div>
    );
  }

  // Error states
  if (error) {
    if (error.response?.status === 400) {
      // Invalid query (too short)
      return (
        <div className="text-gray-600 text-sm p-4">
          Typ minimaal 2 tekens om suggesties te zien.
        </div>
      );
    }

    if (error.response?.status === 500) {
      // Server error
      return (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800 font-medium mb-2">
            Er is iets misgegaan
          </p>
          <p className="text-red-700 text-sm mb-3">
            We konden geen suggesties genereren. Probeer het opnieuw.
          </p>
          <button
            onClick={() => refetch()}
            className="text-red-800 underline text-sm"
          >
            Opnieuw proberen
          </button>
        </div>
      );
    }

    // Network error (no response)
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <p className="text-yellow-800 font-medium mb-2">
          Verbindingsprobleem
        </p>
        <p className="text-yellow-700 text-sm mb-3">
          Controleer je internetverbinding en probeer het opnieuw.
        </p>
        <button
          onClick={() => refetch()}
          className="text-yellow-800 underline text-sm"
        >
          Opnieuw proberen
        </button>
      </div>
    );
  }

  // No suggestions found
  if (data?.suggestions.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-blue-800 font-medium mb-2">
          Geen suggesties gevonden
        </p>
        <p className="text-blue-700 text-sm">
          Probeer andere zoektermen of typ een gemeentenaam.
        </p>
      </div>
    );
  }

  // Success: render suggestions
  return (
    <div className="space-y-2">
      {data.suggestions.map((suggestion) => (
        <SuggestionItem
          key={suggestion.id}
          suggestion={suggestion}
          onClick={onSuggestionClick}
        />
      ))}
    </div>
  );
};
```

**Backend Error Handling:**

**Global Exception Handler: `backend/app/main.py`**

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors (400)."""
    logger.warning(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Invalid request",
            "errors": exc.errors(),
            "fallback_message": "Typ minimaal 2 tekens om suggesties te zien."
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions (500)."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "fallback_message": "Er is iets misgegaan. Probeer het opnieuw."
        }
    )

# Database errors
@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    """Handle database errors."""
    logger.error(f"Database error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Database unavailable",
            "fallback_message": "De service is tijdelijk niet beschikbaar. Probeer het later opnieuw."
        }
    )
```

**Retry Strategy (Frontend):**

**React Query Configuration: `frontend/src/api/client.ts`**

```typescript
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,  // Retry failed requests 2 times
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 3000),
      staleTime: 5 * 60 * 1000,  // 5 minutes
      cacheTime: 10 * 60 * 1000,  // 10 minutes
    },
  },
});
```

**Logging for Debugging:**

```python
# Backend: Structured error logging
logger.error(
    "suggestion_generation_failed",
    query=query,
    error=str(exc),
    traceback=traceback.format_exc()
)

# Frontend: Error tracking (optional for POC)
import * as Sentry from "@sentry/react";

Sentry.captureException(error, {
  tags: { component: "SuggestionList", query },
});
```

**Dependencies:**
- React Query 5.17.0 (retry logic)
- axios 1.6.0 (HTTP errors)

**Testing:**
- Unit test: Network error → show "Verbindingsprobleem" message
- Unit test: 500 error → show "Er is iets misgegaan" message
- Unit test: No suggestions → show "Geen suggesties gevonden"
- E2E test: Disconnect network, verify retry works

---

## Data Model

**Tables Used in Epic 1:**

```sql
-- Gemeentes (read-only for Epic 1)
CREATE TABLE gemeentes (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Services (read-only for Epic 1)
CREATE TABLE services (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    keywords TEXT NULL,
    category VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Associations (read-only for Epic 1)
CREATE TABLE gemeente_service_associations (
    id INTEGER PRIMARY KEY,
    gemeente_id INTEGER NOT NULL REFERENCES gemeentes(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(gemeente_id, service_id)
);

-- PostgreSQL full-text search for Dutch
ALTER TABLE services ADD COLUMN search_vector tsvector;
CREATE INDEX idx_services_search ON services USING GIN(search_vector);

-- Trigger to update search_vector automatically
CREATE FUNCTION services_search_vector_trigger() RETURNS trigger AS $$
BEGIN
  NEW.search_vector :=
    setweight(to_tsvector('dutch', COALESCE(NEW.name, '')), 'A') ||
    setweight(to_tsvector('dutch', COALESCE(NEW.description, '')), 'B') ||
    setweight(to_tsvector('dutch', COALESCE(NEW.keywords, '')), 'C');
  RETURN NEW;
END
$$ LANGUAGE plpgsql;

CREATE TRIGGER services_search_update
  BEFORE INSERT OR UPDATE ON services
  FOR EACH ROW EXECUTE FUNCTION services_search_vector_trigger();
```

**Sample Data for Testing:**

```python
# Seed data: backend/scripts/seed_data.py
gemeentes = [
    {"id": 1, "name": "Amsterdam", "description": "Capital city"},
    {"id": 2, "name": "Rotterdam", "description": "Port city"},
    {"id": 3, "name": "Utrecht", "description": "Central Netherlands"},
]

services = [
    {
        "id": 1,
        "name": "Parkeervergunning",
        "description": "Vergunning voor parkeren in de stad",
        "keywords": "parkeren,bewonersvergunning,auto,parkeerplaats",
        "category": "Verkeer"
    },
    {
        "id": 2,
        "name": "Paspoort aanvragen",
        "description": "Nieuwe paspoort aanvragen of verlengen",
        "keywords": "paspoort,identiteitsbewijs,reisdocument",
        "category": "Burgerzaken"
    },
]

associations = [
    {"gemeente_id": 1, "service_id": 1},  # Amsterdam - Parkeervergunning
    {"gemeente_id": 1, "service_id": 2},  # Amsterdam - Paspoort
    {"gemeente_id": 2, "service_id": 1},  # Rotterdam - Parkeervergunning
]
```

---

## API Contracts

**POST /api/suggestions**

Request:
```json
{
  "query": "parkeren amsterdam"
}
```

Response (200 OK):
```json
{
  "suggestions": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "question": "Hoe vraag ik een parkeervergunning aan in Amsterdam?",
      "gemeente": "Amsterdam",
      "service_id": 1,
      "service_name": "Parkeervergunning",
      "confidence": 0.95
    },
    {
      "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
      "question": "Wat kost een parkeervergunning in Amsterdam?",
      "gemeente": "Amsterdam",
      "service_id": 1,
      "service_name": "Parkeervergunning",
      "confidence": 0.87
    }
  ],
  "query": "parkeren amsterdam",
  "generated_at": "2025-10-07T14:30:00Z",
  "cached": false
}
```

Response (400 Bad Request):
```json
{
  "detail": "Query must be at least 2 characters",
  "fallback_message": "Typ minimaal 2 tekens om suggesties te zien."
}
```

Response (500 Internal Server Error):
```json
{
  "detail": "Suggestion generation failed",
  "fallback_message": "Er is iets misgegaan. Probeer het opnieuw."
}
```

**GET /api/services/{id}**

Response (200 OK):
```json
{
  "id": 1,
  "name": "Parkeervergunning",
  "description": "Vergunning voor parkeren in de stad",
  "category": "Verkeer",
  "gemeentes": [
    {"id": 1, "name": "Amsterdam"},
    {"id": 2, "name": "Rotterdam"}
  ],
  "how_to_apply": "Stap 1: Vul het online formulier in...",
  "requirements": ["ID-bewijs", "Bewijs van woonadres"],
  "cost": "€50 per jaar",
  "processing_time": "2 weken"
}
```

---

## Testing Strategy

**Unit Tests:**

**Backend:**
- `tests/test_nlp_processor.py`
  - Test lemmatization
  - Test fuzzy matching (gemeente, service)
  - Test intent extraction

- `tests/test_template_engine.py`
  - Test template rendering
  - Test article selection
  - Test action inference
  - Test template selection

- `tests/test_suggestion_service.py`
  - Test suggestion generation logic
  - Test scoring algorithm
  - Test caching

**Frontend:**
- `tests/components/SearchBox.test.tsx`
  - Test 2-char minimum validation
  - Test debouncing
  - Test keyboard navigation

- `tests/components/SuggestionList.test.tsx`
  - Test suggestion rendering
  - Test error states
  - Test retry logic

**Integration Tests:**

- `tests/test_suggestions_api.py`
  - Test POST /api/suggestions endpoint
  - Test cache integration (Redis)
  - Test database integration (PostgreSQL)

**Performance Tests:**

- `tests/load_test_suggestions.py`
  - Test P95/P99 latency
  - Test 50 concurrent requests
  - Test cache hit rate

**E2E Tests:**

- `tests/e2e/test_suggestion_flow.py`
  - User types "parkeren amsterdam"
  - Verify suggestions appear
  - User clicks suggestion
  - Verify service detail displayed

---

## Deployment Notes

**Environment Variables:**

```bash
# .env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/onlsuggest
REDIS_URL=redis://localhost:6379
SPACY_MODEL=nl_core_news_sm
CACHE_TTL=300
LOG_LEVEL=INFO
```

**Dependencies to Install:**

Backend:
```bash
pip install fastapi==0.109.0
pip install uvicorn==0.27.0
pip install sqlalchemy==2.0.25
pip install asyncpg==0.29.0
pip install alembic==1.13.0
pip install redis==5.0.1
pip install spacy==3.7.2
pip install rapidfuzz==3.5.2
pip install bcrypt==4.1.2
pip install slowapi==0.1.9
pip install structlog==24.1.0
pip install psycopg2-binary==2.9.9  # For Alembic migrations

# Download Dutch model
python -m spacy download nl_core_news_sm
```

Frontend:
```bash
npm install react@18.2.0 react-dom@18.2.0
npm install @tanstack/react-query@5.17.0
npm install react-router-dom@6.21.0
npm install axios@1.6.0
npm install react-hook-form@7.49.0
npm install tailwindcss@3.4.0
```

**Database Migrations:**

```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

**Seed Data:**

```bash
# Run seed script
python backend/scripts/seed_data.py
```

---

## Success Criteria

**Definition of Done for Epic 1:**

- ✅ All 6 stories completed and tested
- ✅ SearchBox component accepts Dutch input with 2-char minimum
- ✅ POST /api/suggestions returns 3-5 Dutch questions
- ✅ Template engine generates grammatically correct questions
- ✅ Dutch NLP handles fuzzy matching and lemmatization
- ✅ P95 latency < 200ms (verified by load tests)
- ✅ Error handling shows Dutch fallback messages
- ✅ Integration tests pass
- ✅ E2E test: User can type query and see suggestions

**Performance Acceptance:**

- P95 latency: <200ms ✅
- P99 latency: <350ms ✅
- Cache hit rate: >60% ✅
- Concurrent users: 50 ✅

**Quality Gates:**

- Unit test coverage: >80%
- Integration tests: All passing
- Load tests: P95 < 200ms
- E2E test: Full user journey working

---

## Open Questions / Risks

**Risks:**

1. **Dutch grammar complexity:** Article selection (de/het) is complex. Mitigation: Use predefined dictionary for common services.

2. **spaCy model accuracy:** nl_core_news_sm is a small model. Mitigation: Test with real queries, consider upgrading to nl_core_news_md if needed.

3. **Cache invalidation:** When admin updates data, caches need clearing. Mitigation: Manual cache flush endpoint, or short TTL (5 minutes).

**Open Questions:**

1. Should we support multi-word gemeente names ("'s-Gravenhage")? → Yes, UTF-8 encoding handles this.

2. How to handle ambiguous queries (e.g., "vergunning")? → Return top 5 most popular services.

3. Should suggestions be ranked by popularity? → Yes, track query analytics in Redis (future enhancement).

---

## Next Steps

**After completing Epic 1:**

1. Generate tech-spec-epic-2.md (Admin Data Management)
2. Integrate Epic 1 + Epic 2
3. End-to-end testing
4. Deployment to Render

**Immediate action:**

- Set up development environment
- Install dependencies
- Create database schema
- Download nl_core_news_sm model
- Implement Story 1.1 (SearchBox component)

---

**End of Tech Spec: Epic 1 - Query Suggestion Engine**
