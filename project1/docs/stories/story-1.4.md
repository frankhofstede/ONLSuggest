# Story 1.4: Dutch Language Processing and Natural Question Formation

Status: ✅ Completed

## Story

As a **system**,
I want to **understand partial Dutch input and match it to services/gemeentes**,
so that **suggestions feel intelligent and contextually relevant**.

## Acceptance Criteria

1. **AC1**: Handles common Dutch spelling variations
2. **AC2**: Recognizes gemeente names (full and partial)
3. **AC3**: Identifies service keywords in partial input
4. **AC4**: Handles typos gracefully (fuzzy matching)
5. **AC5**: Prioritizes more relevant suggestions first

## Tasks / Subtasks

- [ ] **Task 1**: Add Dutch NLP utilities (AC: #1, #4)
  - [ ] 1.1: Create `backend/app/services/dutch_nlp.py`
  - [ ] 1.2: Initialize spaCy Dutch model (nl_core_news_sm)
  - [ ] 1.3: Add text normalization (lowercase, strip accents option)
  - [ ] 1.4: Add fuzzy matching using Levenshtein distance
  - [ ] 1.5: Add similarity scoring (0.0-1.0)

- [ ] **Task 2**: Implement Dutch stemming/lemmatization (AC: #1, #3)
  - [ ] 2.1: Use spaCy lemmatization for query terms
  - [ ] 2.2: Create lemmatized keywords index for services
  - [ ] 2.3: Match query lemmas against service lemmas
  - [ ] 2.4: Handle common Dutch variants (parkeer → parkeren, etc.)

- [ ] **Task 3**: Enhance search matching (AC: #2, #3, #4)
  - [ ] 3.1: Add fuzzy matching to service name search
  - [ ] 3.2: Add fuzzy matching to gemeente name search
  - [ ] 3.3: Add fuzzy matching to keyword search
  - [ ] 3.4: Set similarity threshold (e.g., 0.8 for typos)
  - [ ] 3.5: Combine exact + fuzzy results

- [ ] **Task 4**: Improve confidence scoring (AC: #5)
  - [ ] 4.1: Add similarity score to confidence calculation
  - [ ] 4.2: Boost exact matches over fuzzy matches
  - [ ] 4.3: Boost lemma matches
  - [ ] 4.4: Add query coverage score (how much of query matched)
  - [ ] 4.5: Update confidence scoring algorithm

- [ ] **Task 5**: Integrate NLP into suggestion service (AC: All)
  - [ ] 5.1: Update `_find_matching_services` with NLP
  - [ ] 5.2: Update `_find_matching_gemeentes` with NLP
  - [ ] 5.3: Update confidence calculation methods
  - [ ] 5.4: Ensure backwards compatibility
  - [ ] 5.5: Maintain performance (<200ms)

- [ ] **Task 6**: Write NLP unit tests (AC: All)
  - [ ] 6.1: Test fuzzy matching with typos
  - [ ] 6.2: Test lemmatization
  - [ ] 6.3: Test spelling variations
  - [ ] 6.4: Test partial gemeente names
  - [ ] 6.5: Test confidence scoring improvements

- [ ] **Task 7**: Integration testing (AC: All)
  - [ ] 7.1: Test "parkeern" → "Parkeervergunning" (typo)
  - [ ] 7.2: Test "paspport" → "Paspoort" (typo)
  - [ ] 7.3: Test "adam" → "Amsterdam" (partial)
  - [ ] 7.4: Test "parkeer" → matches "parkeren" variations
  - [ ] 7.5: Verify relevance ordering

## Dev Notes

### Architecture Patterns and Constraints

**Dutch NLP Design:**
- Use spaCy nl_core_news_sm for lemmatization
- Levenshtein distance for fuzzy matching
- Configurable similarity thresholds
- Maintain sub-200ms performance

**Fuzzy Matching Strategy:**
```python
def fuzzy_match(query: str, target: str, threshold: float = 0.8) -> float:
    """Return similarity score 0.0-1.0, or 0.0 if below threshold."""
    # Use Levenshtein or similar
    # Return normalized similarity
```

**Lemmatization Approach:**
- Lemmatize query at search time
- Pre-lemmatize service keywords in database (future)
- Match lemmas for better recall

**Performance Considerations:**
- Cache spaCy model (load once)
- Limit fuzzy matching to top N candidates
- Keep exact matches fast path
- Profile to ensure <200ms P95

### Testing Standards Summary

**Unit Testing:**
- Framework: pytest
- File location: `backend/tests/services/test_dutch_nlp.py`
- Coverage target: >85% for NLP utilities

**Integration Testing:**
- Test with real typos and variations
- Verify confidence scores improve
- Check performance doesn't degrade

### Project Structure Notes

**Files created:**
- `backend/app/services/dutch_nlp.py` - NLP utilities
- `backend/tests/services/test_dutch_nlp.py` - NLP tests
- Updated: `backend/app/services/suggestion_service.py` - NLP integration

**Dutch Language Features:**
- **Lemmatization**: "parkeervergunning" → "parkeervergunning", "parkeren" → "parkeren"
- **Fuzzy matching**: "paspport" → "paspoort" (1 char difference)
- **Partial matching**: "adam" → "amsterdam"
- **Variants**: Handle "parkeer", "parkeren", "parkeerde", etc.

**Similarity Thresholds:**
- Exact match: 1.0
- Very close (1 char typo): 0.9-0.95
- Close (2 char typos): 0.8-0.9
- Threshold: 0.8 minimum

### References

- [Source: epic-stories.md#Story 1.4] - Dutch NLP specification
- [Source: requirements.txt] - spaCy 3.8.7, nl_core_news_sm model
- [Source: PRD.md#Dutch Language] - Dutch language requirements

## Dev Agent Record

### Context Reference

Story Context XML: `/docs/story-context-1.4.xml`

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

<!-- Will be populated during implementation -->

### Completion Notes List

<!-- Will be populated during implementation -->

### File List

<!-- Files created/modified during implementation:
- backend/app/services/dutch_nlp.py
- backend/app/services/suggestion_service.py
- backend/tests/services/test_dutch_nlp.py
-->
