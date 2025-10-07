# Story 0.5: Backend Integration Testing & Environment Validation

Status: Ready for Review

## Story

As a **developer**,
I want to **create a minimal FastAPI application and verify full-stack integration**,
so that **I can confirm the development environment is fully functional before starting Epic 1**.

## Acceptance Criteria

1. **AC1**: Basic FastAPI application created with root and health endpoints
2. **AC2**: CORS middleware configured for frontend (http://localhost:5173)
3. **AC3**: Database integration test endpoint created and verified
4. **AC4**: Redis integration test endpoint created and verified
5. **AC5**: Frontend can successfully call backend APIs
6. **AC6**: Week 1 completion report generated showing all green checkmarks

## Tasks / Subtasks

- [ ] **Task 1**: Create basic FastAPI application (AC: #1, #2)
  - [ ] 1.1: Create `backend/app/main.py`
  - [ ] 1.2: Initialize FastAPI app with title and debug settings from config
  - [ ] 1.3: Add CORS middleware allowing http://localhost:5173
  - [ ] 1.4: Create GET / endpoint returning {"message": "ONLSuggest API is running"}
  - [ ] 1.5: Create GET /health endpoint returning {"status": "healthy", "version": "0.1.0"}
  - [ ] 1.6: Start server: `uvicorn app.main:app --reload`
  - [ ] 1.7: Test root: `curl http://localhost:8000/` (should return message)
  - [ ] 1.8: Test health: `curl http://localhost:8000/health` (should return status)
  - [ ] 1.9: Visit http://localhost:8000/docs (verify Swagger UI)

- [ ] **Task 2**: Create database integration test endpoint (AC: #3)
  - [ ] 2.1: Import get_db dependency, AsyncSession, models
  - [ ] 2.2: Create GET /api/test/db endpoint with db dependency
  - [ ] 2.3: Query count of gemeentes and services using func.count()
  - [ ] 2.4: Return {"database": "connected", "gemeentes": count, "services": count}
  - [ ] 2.5: Test endpoint: `curl http://localhost:8000/api/test/db`
  - [ ] 2.6: Verify response shows gemeentes=8, services=10

- [ ] **Task 3**: Create Redis integration test endpoint (AC: #4)
  - [ ] 3.1: Create `backend/app/core/redis_client.py` with get_redis() function
  - [ ] 3.2: Initialize redis client from settings.redis_url
  - [ ] 3.3: Create GET /api/test/redis endpoint
  - [ ] 3.4: Test Redis by setting and getting a test key
  - [ ] 3.5: Return {"redis": "connected", "test_value": value}
  - [ ] 3.6: Test endpoint: `curl http://localhost:8000/api/test/redis`
  - [ ] 3.7: Verify response shows test_value

- [ ] **Task 4**: Frontend-backend integration test (AC: #5)
  - [ ] 4.1: Ensure backend is running (`uvicorn app.main:app --reload`)
  - [ ] 4.2: In new terminal, start frontend: `cd frontend && npm run dev`
  - [ ] 4.3: Update `frontend/src/App.tsx` to test API calls
  - [ ] 4.4: Use useEffect to fetch /health and /api/test/db on mount
  - [ ] 4.5: Display results with Tailwind styling
  - [ ] 4.6: Visit http://localhost:5173
  - [ ] 4.7: Verify page shows API health and database stats
  - [ ] 4.8: Check browser console for errors (should be none)

- [ ] **Task 5**: Create and run Week 1 completion report (AC: #6)
  - [ ] 5.1: Create `backend/scripts/week1_report.py`
  - [ ] 5.2: Check database connection and query counts
  - [ ] 5.3: Check Redis connection
  - [ ] 5.4: Check installed dependencies (fastapi, sqlalchemy, spacy versions)
  - [ ] 5.5: Check Dutch NLP model loads
  - [ ] 5.6: Print formatted report with ✅ checkmarks
  - [ ] 5.7: Run report: `cd backend && python scripts/week1_report.py`
  - [ ] 5.8: Verify all items show ✅ (green checkmarks)
  - [ ] 5.9: Save screenshot or output to docs/

## Dev Notes

### Architecture Patterns and Constraints

**FastAPI Minimal Setup:**
- Single main.py file
- CORS configured for local development
- Automatic OpenAPI docs at /docs
- Health check endpoint for monitoring

**Integration Test Endpoints:**
- GET /api/test/db - Verify PostgreSQL connection and seeded data
- GET /api/test/redis - Verify Redis connection and operations
- These are temporary test endpoints (will be removed before production)

**CORS Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Frontend Test Component:**
Simple App.tsx that:
1. Calls backend /health endpoint
2. Calls backend /api/test/db endpoint
3. Displays results in styled cards
4. Shows loading/error states

### Week 1 Completion Report

**Checks Performed:**
1. ✅ Database Setup - PostgreSQL accessible, 8 gemeentes, 10 services
2. ✅ Redis Connected - Can set/get values
3. ✅ Backend Dependencies - FastAPI, SQLAlchemy, spaCy versions
4. ✅ Dutch NLP Model - nl_core_news_sm loads successfully
5. ✅ Frontend Setup - Vite dev server runs, can call backend

**Expected Output:**
```
==========================================================
📊 Week 1 Environment Setup - Completion Report
==========================================================

✅ Database Setup
   - Gemeentes: 8
   - Services: 10
   - Associations: 80
   - Admin users: 1

✅ Redis Connected
   - Status: Working (complete)

✅ Backend Dependencies
   - FastAPI: 0.109.0
   - SQLAlchemy: 2.0.25
   - spaCy: 3.7.2
   - bcrypt: 4.1.2

✅ Dutch NLP Model
   - Model: nl_core_news_sm loaded

==========================================================
🎉 Week 1 Setup Complete - Ready for Epic 1 Development!
==========================================================
```

### Testing Standards Summary

- Integration tests verify end-to-end connectivity
- Health check endpoint enables monitoring
- Report script provides automated verification
- No unit tests yet (will be added in Story 1.1)

### Project Structure Notes

**Files created:**
- backend/app/main.py
- backend/app/core/redis_client.py
- backend/scripts/week1_report.py
- frontend/src/App.tsx (updated)

**Environment after Story 0.5:**
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:5173
- ✅ PostgreSQL with 8 gemeentes, 10 services, 80 associations
- ✅ Redis caching operational
- ✅ Full-stack integration verified

### References

- [Source: week-1-setup-checklist.md#Day 5] - Integration testing instructions
- [Source: solution-architecture.md#Architecture Pattern] - Monolith, REST API
- [Source: tech-spec-epic-1.md#API Contracts] - Endpoint patterns
- [Source: PRD.md#NFR004] - Graceful degradation requirement

## Dev Agent Record

### Context Reference

Story Context XML: `/docs/story-context-0.5.xml`

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

<!-- Will be populated during implementation -->

### Completion Notes List

**Implementation Summary:**
- All 5 tasks completed successfully
- Basic FastAPI application created with root, health, database test, and Redis test endpoints
- CORS middleware configured for frontend (http://localhost:5173)
- Database integration verified (8 gemeentes, 10 services, 80 associations)
- Redis integration verified (set/get operations working)
- Frontend-backend integration tested with styled dashboard
- Week 1 completion report generated - all checks passed ✅

**Key Implementation Details:**
- FastAPI 0.109.0 with auto-reload enabled
- CORS configured with allow_credentials=True
- Database test endpoint queries gemeentes and services counts
- Redis test endpoint performs set/get/delete operations
- Frontend displays API health, database stats, and Redis status in Tailwind-styled cards
- Week 1 report validates all environment components programmatically

**Week 1 Report Results:**
- ✅ Database Setup: 8 gemeentes, 10 services, 80 associations, 1 admin user
- ✅ Redis Connected: Working with set/get operations
- ✅ Backend Dependencies: FastAPI 0.109.0, SQLAlchemy 2.0.25, spaCy 3.8.7, bcrypt 4.1.2
- ✅ Dutch NLP Model: nl_core_news_sm loaded successfully

**Files Created:**
- backend/app/main.py (113 lines - FastAPI app with 4 endpoints)
- backend/app/core/redis_client.py (21 lines - Redis client configuration)
- backend/scripts/week1_report.py (167 lines - Environment validation report)
- frontend/src/App.tsx (152 lines - Integration test dashboard)

**Environment Status:**
- Backend running on http://localhost:8000 with Swagger docs at /docs
- Frontend running on http://localhost:5173 with full-stack integration test UI
- PostgreSQL database with seeded data
- Redis cache operational
- Full-stack communication verified

### File List

**Files created during implementation:**
- backend/app/main.py (113 lines)
- backend/app/core/redis_client.py (21 lines)
- backend/scripts/week1_report.py (167 lines)
- frontend/src/App.tsx (152 lines - updated with integration test dashboard)
