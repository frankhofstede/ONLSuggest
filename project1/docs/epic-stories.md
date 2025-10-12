# ONLSuggest-v1 - Epic Breakdown

**Author:** Frank
**Date:** 2025-10-06 (Updated: 2025-10-10)
**Project Level:** Level 2 (Small complete system)
**Target Scale:** 18 stories, 3 epics, 6-12 week delivery (MVP complete + Epic 3)

---

## Epic Overview

This project consists of 3 core epics that enable citizens to discover municipal services through intelligent query suggestions:

1. **Query Suggestion Engine** - The core AI/algorithm that transforms partial user input into natural, full-text Dutch questions
2. **Admin Data Management** - Simple interface for manually curating the gemeente and service data that powers suggestions
3. **KOOP Suggester API Integration** - Enterprise-grade government API integration with feature toggle for A/B testing and gradual migration

Epics 1 and 2 form the foundation POC that validates the question-based suggestion approach. Epic 3 adds government API integration while preserving the template engine as fallback, enabling safe testing and deployment of external services.

---

## Epic Details

### Epic 1: Query Suggestion Engine

**Epic Goal**: Build the core suggestion generation system that transforms partial input into full-text questions

**Business Value**: Proves the core value proposition - that citizens can find services through conversational query suggestions without knowing official terminology

**Dependencies**: None (can start immediately)

**Estimated Effort**: 3-4 weeks

---

#### Story 1.1: Basic Input Field with Character Minimum Validation

**As a** citizen
**I want to** type my query into a simple search box
**So that** I can start finding municipal services

**Acceptance Criteria**:
- Input field accepts Dutch text input (UTF-8)
- Minimum 2 characters required before suggestions trigger
- Clear visual feedback when minimum not met
- Input field is prominently displayed on page load
- Supports keyboard navigation

**Technical Notes**:
- Consider debouncing for performance (100-150ms)
- UTF-8 character support for Dutch special characters (ë, ï, etc.)

---

#### Story 1.2: Real-time Suggestion Generation API Endpoint

**As a** frontend application
**I want to** call an API with partial query text
**So that** I can receive generated question suggestions

**Acceptance Criteria**:
- POST endpoint accepts partial query (min 2 chars)
- Returns 3-5 suggested questions in JSON format
- Response time under 200ms (P95)
- Handles concurrent requests gracefully
- Returns error codes for invalid input

**Technical Notes**:
- Consider caching strategy for common queries
- Rate limiting may be needed for POC testing

---

#### Story 1.3: Question Template Engine for Gemeente/Service Combinations

**As a** suggestion engine
**I want to** combine query fragments with gemeente/service data using templates
**So that** I generate natural-sounding Dutch questions

**Acceptance Criteria**:
- Template system supports multiple question formats ("Hoe...", "Waar...", "Wat kost...")
- Templates dynamically insert gemeente names and service terms
- Generated questions are grammatically correct Dutch
- Template selection based on query intent/context
- At least 5 different question templates available

**Technical Notes**:
- Templates should handle singular/plural, verb conjugation
- Consider NLP library for Dutch language processing

---

#### Story 1.4: Dutch Language Processing and Natural Question Formation

**As a** system
**I want to** understand partial Dutch input and match it to services/gemeentes
**So that** suggestions feel intelligent and contextually relevant

**Acceptance Criteria**:
- Handles common Dutch spelling variations
- Recognizes gemeente names (full and partial)
- Identifies service keywords in partial input
- Handles typos gracefully (fuzzy matching)
- Prioritizes more relevant suggestions first

**Technical Notes**:
- Dutch stemming/lemmatization
- Similarity scoring algorithm
- May need Dutch stop words list

---

#### Story 1.5: Sub-200ms Performance Optimization

**As a** user
**I want** suggestions to appear instantly
**So that** I believe they are pre-generated (not AI-generated)

**Acceptance Criteria**:
- P95 response time under 200ms
- P99 response time under 350ms
- No visible loading indicators needed
- Performance tested with 50 gemeentes, 100 services
- Performance holds under 10 concurrent users

**Technical Notes**:
- Profiling and optimization required
- Consider in-memory caching
- Database query optimization
- Connection pooling

---

#### Story 1.6: Graceful Error Handling and Fallback Messaging

**As a** user
**I want** helpful feedback when suggestions fail
**So that** I'm not stuck with a broken interface

**Acceptance Criteria**:
- Network errors show friendly Dutch message
- No suggestions found shows helpful guidance
- System errors don't break the interface
- Users can retry without refreshing page
- Error messages in Dutch

**Technical Notes**:
- Circuit breaker pattern consideration
- Logging for debugging

---

### Epic 2: Admin Data Management

**Epic Goal**: Enable manual curation of gemeentes and services through simple admin interface

**Business Value**: Allows rapid dataset iteration without developer involvement, keeping POC flexible and testable

**Dependencies**: None (can develop in parallel with Epic 1)

**Estimated Effort**: 2-3 weeks

---

#### Story 2.1: Admin Authentication (Basic Auth)

**As an** admin user
**I want to** log in to the admin interface
**So that** only authorized users can manage data

**Acceptance Criteria**:
- Basic authentication mechanism (username/password)
- Login page with Dutch labels
- Session management (stays logged in)
- Logout functionality
- Password stored securely (hashed)

**Technical Notes**:
- Basic auth sufficient for POC
- Consider environment variable for initial admin credentials

---

#### Story 2.2: Gemeente CRUD Operations

**As an** admin user
**I want to** create, view, edit, and delete gemeente entries
**So that** I can maintain accurate municipality data

**Acceptance Criteria**:
- List view shows all gemeentes
- Create form with required fields (name, optional metadata)
- Edit form pre-populates existing data
- Delete with confirmation prompt
- Validation prevents empty names
- Success/error feedback in Dutch

**Technical Notes**:
- Consider soft delete vs hard delete
- Audit log might be useful

---

#### Story 2.3: Service CRUD Operations

**As an** admin user
**I want to** create, view, edit, and delete service entries
**So that** I can maintain accurate service catalog

**Acceptance Criteria**:
- List view shows all services
- Create form with fields (name, description, keywords)
- Edit form pre-populates existing data
- Delete with confirmation prompt
- Validation prevents duplicates
- Success/error feedback in Dutch

**Technical Notes**:
- Service keywords important for matching
- Consider categorization/tags

---

#### Story 2.4: Gemeente-Service Association Management

**As an** admin user
**I want to** link services to specific gemeentes
**So that** suggestions only show relevant gemeente/service combinations

**Acceptance Criteria**:
- Interface to associate multiple services with a gemeente
- Interface to associate multiple gemeentes with a service
- View existing associations
- Remove associations
- Prevent duplicate associations

**Technical Notes**:
- Many-to-many relationship
- UI could be checkboxes or multiselect

---

#### Story 2.5: Data Validation and Duplicate Prevention

**As an** admin user
**I want** the system to prevent invalid or duplicate data
**So that** the dataset stays clean and functional

**Acceptance Criteria**:
- Cannot create duplicate gemeente names
- Cannot create duplicate service names
- Required fields enforced
- Character limits enforced
- Clear validation error messages in Dutch

**Technical Notes**:
- Case-insensitive duplicate checking
- Frontend + backend validation

---

#### Story 2.6: Basic Admin Dashboard with Data Overview

**As an** admin user
**I want to** see summary statistics of my data
**So that** I understand the current state of the dataset

**Acceptance Criteria**:
- Shows count of gemeentes
- Shows count of services
- Shows count of associations
- Shows recent activity (last 10 changes)
- Link to each CRUD interface

**Technical Notes**:
- Simple summary queries
- Consider caching for dashboard stats

---

### Epic 3: KOOP Suggester API Integration

**Epic Goal**: Integrate external KOOP Suggester API as an alternative suggestion engine with admin-controlled feature toggle

**Business Value**: Validates enterprise-grade government API integration while maintaining current template engine as fallback, enabling A/B testing and gradual migration strategy

**Dependencies**:
- Epic 1 complete (existing suggestion system)
- Epic 2 complete (admin interface)
- KOOP API production-ready and accessible

**Estimated Effort**: 2-4 weeks

**Strategic Context**: This epic replaces the custom template engine (Epic 1) with the government-provided KOOP Suggester API, adding category-based filtering, URL-based question examples, and AI-generated document summaries. The feature flag approach allows safe deployment, testing, and potential rollback while preserving the MVP investment.

---

#### Story 3.1: Admin Feature Toggle for Suggestion Engine Selection

**As an** admin user
**I want to** toggle between template engine and KOOP API suggestion engines
**So that** I can control which suggestion system is active without code deployment

**Acceptance Criteria**:
- Admin settings page shows "Suggestion Engine" toggle (Template Engine / KOOP API)
- Current selection persists in database
- Toggle takes effect immediately for all users
- Shows current engine status on admin dashboard
- Default: Template Engine (safe fallback)

**Technical Notes**:
- Add `suggestion_engine` field to settings table or config
- Frontend reads engine selection on page load
- Consider adding "Test KOOP API Connection" button

---

#### Story 3.2: KOOP API Proxy Endpoint

**As a** frontend application
**I want to** call a backend proxy that communicates with KOOP Suggester API
**So that** API keys and external calls are hidden from client

**Acceptance Criteria**:
- New backend endpoint: `POST /api/v1/suggestions/koop`
- Transforms request format: `{query, max_results}` → `{text, max_items}`
- Adds optional `categories` and `prev_uris` support
- Transforms KOOP response → frontend Suggestion interface
- Returns error with graceful message if KOOP API fails
- Automatic fallback to template engine on KOOP failure

**Technical Notes**:
- KOOP API URL: `https://onl-suggester.koop-innovatielab-tst.test5.s15m.nl/v1/suggest`
- Handle DNS/network failures gracefully
- Log all KOOP API calls for debugging
- Maintain <200ms response time requirement

---

#### Story 3.3: Category-Based Suggestion Display

**As a** user
**I want to** see suggestions grouped by category ("Dienst", "Wegwijzer Overheid")
**So that** I can understand what type of information each suggestion provides

**Acceptance Criteria**:
- Suggestions display category badge/label
- Categories visually distinct (color/icon)
- Can filter suggestions by category (optional)
- Categories returned from KOOP API mapped correctly
- Template engine suggestions marked as "Dienst" (backward compatibility)

**Technical Notes**:
- Update Suggestion TypeScript interface to include `category?: string`
- CSS styling for category badges
- KOOP API returns categories in response - validate format

---

#### Story 3.4: URL-Based Question Examples

**As a** user
**I want to** access pre-configured example queries via URL parameters
**So that** I can share specific searches or access curated examples

**Acceptance Criteria**:
- URL parameter `?q=<query>` pre-fills search box
- Search triggers automatically on page load if `?q=` present
- URL parameter `?example=<id>` loads predefined example queries
- Examples configurable in admin interface
- Browser back button clears pre-filled query

**Technical Notes**:
- React Router or vanilla URL param parsing
- Admin CRUD for managing example queries
- Examples table: `{id, label, query_text, category?}`

---

#### Story 3.5: AI Document Summary with Streaming Display

**As a** user
**I want to** click a suggestion and see an AI-generated document summary
**So that** I can preview content before visiting the full page

**Acceptance Criteria**:
- Clicking suggestion shows summary panel/modal
- Summary displays incrementally (streaming effect)
- Shows document title from suggestion metadata
- "View Full Document" link opens actual service page
- Close button returns to suggestions
- Loading state while summary generates

**Technical Notes**:
- KOOP API likely returns document URI + summary endpoint
- May require separate API call for summary generation
- Implement streaming with Server-Sent Events or chunked response
- Fallback: show service description from database if KOOP unavailable

---

#### Story 3.6: Feature Flag Testing and Validation

**As a** developer/admin
**I want to** validate both engines work correctly with automated tests
**So that** feature toggle doesn't break existing functionality

**Acceptance Criteria**:
- Playwright E2E test for template engine mode
- Playwright E2E test for KOOP API mode
- Playwright test for toggle switching
- Unit tests for API proxy transformation logic
- Manual test checklist for both engines
- Performance comparison report (template vs KOOP)

**Technical Notes**:
- Mock KOOP API responses for E2E tests
- Test fallback behavior when KOOP unavailable
- Validate response time <200ms for both engines
- Test category display with both engines

---

## Story Status

**Epic 1 & 2**: Completed (MVP delivered)
**Epic 3**: Not Started
**Total Stories**: 18 (12 complete, 6 pending)

---

## Next Steps

**For Epic 3 Implementation:**

1. Review Epic 3 stories with stakeholders
2. Create tech-spec-epic-3.md (solution architecture)
3. Estimate story points for Epic 3
4. Prioritize Epic 3 stories for Sprint
5. Begin Epic 3 Story 3.1 (Feature Toggle)
