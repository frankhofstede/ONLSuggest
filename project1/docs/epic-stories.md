# ONLSuggest-v1 - Epic Breakdown

**Author:** Frank
**Date:** 2025-10-06
**Project Level:** Level 2 (Small complete system)
**Target Scale:** 8-12 stories, 1-2 epics, 4-8 week MVP

---

## Epic Overview

This project consists of 2 core epics that enable citizens to discover municipal services through intelligent query suggestions:

1. **Query Suggestion Engine** - The core AI/algorithm that transforms partial user input into natural, full-text Dutch questions
2. **Admin Data Management** - Simple interface for manually curating the gemeente and service data that powers suggestions

Both epics work together to create a POC that validates the question-based suggestion approach while keeping operational complexity minimal through manual data management.

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

## Story Status

**Not Started**: All stories
**In Progress**: None
**Completed**: None

---

## Next Steps

1. Prioritize stories for Sprint 1
2. Estimate story points
3. Assign to developers
4. Begin Epic 1 Story 1.1 or Epic 2 Story 2.1 (can be parallel)
