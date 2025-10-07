# Story 0.1: Repository Structure & Python Backend Foundation

Status: Ready for Review

## Story

As a **developer**,
I want to **set up the project repository structure and Python backend environment**,
so that **I have a working foundation to develop ONLSuggest features**.

## Acceptance Criteria

1. **AC1**: Project directory structure created with backend/ and frontend/ folders per monorepo design
2. **AC2**: Python 3.11+ virtual environment created and activated
3. **AC3**: All backend dependencies installed (FastAPI, SQLAlchemy, asyncpg, spaCy, Redis, etc.)
4. **AC4**: Dutch NLP model (nl_core_news_sm) downloaded and verified
5. **AC5**: Development tools installed (pytest, black, flake8, mypy)
6. **AC6**: .gitignore configured to exclude .env, .venv, __pycache__

## Tasks / Subtasks

- [x] **Task 1**: Create monorepo directory structure (AC: #1)
  - [x] 1.1: Navigate to project root `/Users/koop/PycharmProjects/ONLSuggest/project1`
  - [x] 1.2: Create backend directories: `backend/app/{models,schemas,routers,services,middleware,core,utils}`
  - [x] 1.3: Create backend test directories: `backend/tests/{unit,integration}`
  - [x] 1.4: Create backend scripts directory: `backend/scripts`
  - [x] 1.5: Create frontend directories (placeholder): `frontend/src`, `frontend/tests`
  - [x] 1.6: Verify structure with `tree -L 3 -d`

- [x] **Task 2**: Set up Python virtual environment (AC: #2)
  - [x] 2.1: Verify Python 3.11+ installed: `python3 --version`
  - [x] 2.2: Create virtual environment: `cd backend && python3 -m venv .venv`
  - [x] 2.3: Activate virtual environment: `source .venv/bin/activate`
  - [x] 2.4: Verify activation (`.venv` prefix in terminal, `which python`)

- [x] **Task 3**: Install backend production dependencies (AC: #3)
  - [x] 3.1: Create `backend/requirements.txt` with 22 packages (FastAPI, uvicorn, SQLAlchemy, asyncpg, psycopg2-binary, alembic, redis, spaCy, rapidfuzz, bcrypt, slowapi, structlog, pydantic, pydantic-settings, python-jose)
  - [x] 3.2: Upgrade pip: `pip install --upgrade pip`
  - [x] 3.3: Install dependencies: `pip install -r requirements.txt`
  - [x] 3.4: Verify installations: `pip list | grep fastapi`, `pip list | grep spacy`

- [x] **Task 4**: Download and verify Dutch NLP model (AC: #4)
  - [x] 4.1: Download model: `python -m spacy download nl_core_news_sm`
  - [x] 4.2: Verify model loads: `python -c "import spacy; nlp = spacy.load('nl_core_news_sm'); print('Dutch model loaded successfully')"`

- [x] **Task 5**: Install development dependencies (AC: #5)
  - [x] 5.1: Create `backend/requirements-dev.txt` (pytest, pytest-asyncio, pytest-cov, black, flake8, mypy, locust)
  - [x] 5.2: Install dev dependencies: `pip install -r requirements-dev.txt`
  - [x] 5.3: Verify black installed: `black --version`

- [x] **Task 6**: Configure .gitignore (AC: #6)
  - [x] 6.1: Add `.env` to backend/.gitignore
  - [x] 6.2: Add `.venv/` to backend/.gitignore
  - [x] 6.3: Add `__pycache__/` and `*.pyc` to backend/.gitignore
  - [x] 6.4: Verify git ignores these files

## Dev Notes

### Architecture Patterns and Constraints

**Monorepo Structure (from solution-architecture.md):**
```
onlsuggest/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── middleware/
│   │   ├── core/
│   │   └── utils/
│   ├── alembic/
│   ├── tests/
│   ├── scripts/
│   └── requirements.txt
├── frontend/ (will be set up in Story 0.4)
└── docs/
```

**Python Version:** 3.11+ (required for FastAPI 0.109.0 and SQLAlchemy 2.0.25 async features)

**Key Dependencies (Installed):**
- FastAPI 0.109.0 - Async web framework
- SQLAlchemy 2.0.25 - Async ORM
- asyncpg 0.29.0 - PostgreSQL async driver
- psycopg2-binary 2.9.9 - PostgreSQL driver for Alembic
- spaCy 3.8.7 + nl_core_news_sm 3.8.0 - Dutch NLP (upgraded for Python 3.12 compatibility)
- Pydantic 2.11.10 - Request/response validation (upgraded for spaCy 3.8.7)
- Redis 5.0.1 - Cache client
- bcrypt 4.1.2 - Password hashing

### Testing Standards Summary

- **Framework:** pytest with pytest-asyncio for async tests
- **Coverage:** pytest-cov targeting >80%
- **Code formatting:** black (PEP 8)
- **Linting:** flake8
- **Type checking:** mypy
- **Load testing:** locust

### Project Structure Notes

**Alignment with unified project structure:**
- All paths match proposed source tree in solution-architecture.md
- Backend follows FastAPI best practices (routers, services, models separation)
- Tests organized by type (unit vs integration)

**No code conflicts:** Greenfield project, no existing code to integrate

### References

- [Source: week-1-setup-checklist.md#Day 1] - Complete setup instructions with commands
- [Source: solution-architecture.md#Proposed Source Tree] - Monorepo structure specification
- [Source: solution-architecture.md#Technology Stack Summary] - All 22 dependencies with versions
- [Source: tech-spec-epic-1.md#Dependencies to Install] - Installation commands

## Dev Agent Record

### Context Reference

Story Context XML: `/docs/story-context-0.1.xml`

### Agent Model Used

claude-sonnet-4-5-20250929

### Debug Log References

**Dependency Version Adjustments:**
- **spaCy**: Upgraded from 3.7.2 to 3.8.7 for Python 3.12 compatibility
- **Pydantic**: Initially downgraded to 1.10.13 then upgraded to 2.11.10 to match spaCy 3.8.7 requirements
- **typer**: Upgraded from 0.9.4 to 0.19.2 to resolve CLI compatibility issues
- **weasel**: Upgraded from 0.3.4 to 0.4.1 for typer compatibility
- **pytest-cov**: Corrected version from 0.21.1 (invalid) to 4.1.0
- **Dutch NLP model**: Downloaded nl_core_news_sm v3.8.0 (~13MB)

**Rationale:** Python 3.12.9 requires newer package versions than originally specified in solution-architecture.md. All upgrades maintain API compatibility.

### Completion Notes List

**Implementation Summary:**
All 6 tasks completed successfully with all subtasks verified. The ONLSuggest backend foundation is ready for development:

- ✅ Monorepo structure created following FastAPI best practices
- ✅ Python 3.12.9 virtual environment activated (exceeds 3.11+ requirement)
- ✅ All production dependencies installed with version compatibility fixes
- ✅ Dutch NLP model (nl_core_news_sm v3.8.0) downloaded and verified
- ✅ Development tools (pytest, black, flake8, mypy, locust) installed
- ✅ Git configuration secured with comprehensive .gitignore

**All 10 validation tests passed:**
- T1-T10: Directory structure, venv activation, Python version, package installations, NLP model loading, and git ignore rules all verified

**Next Steps:**
Story 0.1 is complete and ready for review. Once approved, development can proceed with Story 0.2 (Database Setup) and subsequent stories.

### File List

**Created Files:**
- backend/requirements.txt (production dependencies)
- backend/requirements-dev.txt (development dependencies)
- backend/.gitignore (git ignore rules)

**Created Directories:**
- backend/app/{models,schemas,routers,services,middleware,core,utils}
- backend/tests/{unit,integration}
- backend/scripts/
- frontend/{src,tests}
- backend/.venv/ (virtual environment)

## Change Log

**2025-10-07 - Story 0.1 Implementation**
- Created complete monorepo directory structure for backend and frontend
- Set up Python 3.12.9 virtual environment
- Installed all production and development dependencies with Python 3.12 compatibility fixes
- Downloaded and verified Dutch NLP model (nl_core_news_sm v3.8.0)
- Configured comprehensive .gitignore for Python projects
- Validated all acceptance criteria with 10 automated tests
