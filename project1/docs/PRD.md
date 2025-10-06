# ONLSuggest-v1 Product Requirements Document (PRD)

**Author:** Frank
**Date:** 2025-10-06
**Project Level:** Level 2 (Small complete system)
**Project Type:** Web application
**Target Scale:** 8-12 stories, 1-2 epics, 4-8 week MVP

---

## Description, Context and Goals

### Description

ONLSuggest is an intelligent query suggestion system designed to help Dutch citizens discover relevant municipal (gemeente) services. Rather than traditional autocomplete functionality, the system transforms partial user input into clear, actionable questions that guide users toward the services they need.

The system prioritizes user experience experimentation and operational simplicity. Dataset management will be handled manually through an administrative interface, avoiding premature complexity and allowing the team to focus on validating the core user experience with real citizens before investing in automation.

**Key Differentiator:** Question-based suggestions rather than keyword completion - helping citizens articulate what they're looking for rather than guessing search terms.

### Deployment Intent

**Demo/POC** - This initial version serves as a proof-of-concept to validate the question-based suggestion approach and explore multiple UX patterns. The goal is to demonstrate value to stakeholders and gather feedback from real users before committing to a full production implementation.

### Context

Citizens often struggle to find relevant government services because they don't know the official terminology or exact phrasing used by municipal systems. Traditional search and autocomplete solutions force users to guess correct keywords, creating friction and abandonment. This POC addresses this gap by transforming the way citizens interact with government service discovery - allowing natural, conversational input while generating precise, helpful question suggestions that guide them to the right services. The timing is critical as governments increasingly prioritize digital accessibility and user-centered design.

### Goals

1. **Validate intelligent query transformation**: Demonstrate that the system can map various partial input formulations (fragments, keywords, incomplete phrases) into coherent, full-text question suggestions that feel natural and anticipated to users.

2. **Create perception of pre-generated suggestions**: Real-time generation must be fast and contextually accurate enough that users believe they're seeing pre-written suggestions rather than dynamically generated queries - establishing trust and confidence in the system.

3. **Prove user-friendly gemeente/service discovery**: Show that citizens unfamiliar with government terminology can successfully find relevant municipal services through conversational question suggestions, reducing friction in accessing government services.

## Requirements

### Functional Requirements

**FR001**: Users can enter partial query text (minimum 2 characters) into a search input field

**FR002**: System generates 3-5 full-text question suggestions in real-time based on partial input

**FR003**: Generated suggestions combine gemeente (municipality) names with relevant service categories/types

**FR004**: Users can select a suggested question to execute a full search for that service

**FR005**: System supports Dutch language input and generates Dutch-language question suggestions

**FR006**: Admin users can create, edit, and delete gemeente entries via admin interface

**FR007**: Admin users can create, edit, and delete service entries via admin interface

**FR008**: Admin users can associate services with specific gemeentes via admin interface

**FR009**: System provides real-time search feedback with response time under 200ms for suggestion generation

**FR010**: Users can clear input and restart query process at any time

**FR011**: System displays service results/information when a suggested question is selected

**FR012**: Admin users can authenticate to access the admin interface (basic auth for POC)

### Non-Functional Requirements

**NFR001 - Performance**: Query suggestion generation must complete within 200ms to create the perception of instant, pre-generated suggestions

**NFR002 - Usability**: Interface must be accessible and intuitive for Dutch citizens of all technical skill levels, following WCAG 2.1 AA standards

**NFR003 - Language Support**: All user-facing text, suggestions, and questions must be in correct, natural Dutch language

**NFR004 - Reliability**: System must handle graceful degradation - if suggestion generation fails, provide helpful fallback message without breaking user flow

**NFR005 - Scalability (POC)**: System should support testing with 10-50 concurrent users and datasets of 50+ gemeentes and 100+ services

## User Journeys

### Primary Journey: Citizen Discovering Municipal Service

**Persona**: Maria, 42, needs to apply for a parking permit in Amsterdam but doesn't know the official terminology

**Journey Steps**:

1. **Entry**: Maria visits the ONLSuggest interface with a vague idea ("parkeren vergunning amsterdam")

2. **Initial Input**: She types "parkeren" (parking) - only 8 characters

3. **Suggestion Generation**: System instantly shows 3-5 full questions:
   - "Hoe vraag ik een parkeervergunning aan in Amsterdam?"
   - "Waar kan ik een bewonersvergunning parkeren aanvragen in Amsterdam?"
   - "Wat kost een parkeervergunning in Amsterdam?"

4. **Recognition**: Maria sees her need articulated clearly - "Ah yes, that's exactly what I want!"

5. **Selection**: She clicks the first suggestion

6. **Result**: System displays relevant service information for parking permit application in Amsterdam

7. **Success**: Maria finds the right service without knowing official terms or navigating complex menus

**Key Success Metric**: Maria believes the suggestions were pre-written (not realizing they were generated in real-time based on her 8-character input)

## UX Design Principles

**1. Invisible Intelligence**: The system's intelligence should feel natural and anticipated, not algorithmic. Users should believe suggestions are curated, not generated.

**2. Progressive Disclosure**: Start minimal (search box) and reveal complexity only when needed. Avoid overwhelming users with options upfront.

**3. Conversational Framing**: Present suggestions as questions users might ask, not system-centric categories. Mirror natural language patterns.

**4. Instant Feedback**: No loading spinners or delays - suggestions appear instantly as if they were already there, reinforcing the "smart autocomplete" perception.

**5. Experimentation-First Architecture**: Design must support A/B testing multiple UX patterns (dropdown vs. cards, single-column vs. multi-column, etc.) without rebuilding core logic.

**Note**: Step 12 will recommend running the dedicated UX specification workflow to explore these principles in depth with multiple interaction patterns.

## Epics

### Epic 1: Query Suggestion Engine
**Goal**: Build the core suggestion generation system that transforms partial input into full-text questions

**Stories** (6 stories):
- Story 1.1: Basic input field with character minimum validation
- Story 1.2: Real-time suggestion generation API endpoint
- Story 1.3: Question template engine for gemeente/service combinations
- Story 1.4: Dutch language processing and natural question formation
- Story 1.5: Sub-200ms performance optimization
- Story 1.6: Graceful error handling and fallback messaging

### Epic 2: Admin Data Management
**Goal**: Enable manual curation of gemeentes and services through simple admin interface

**Stories** (6 stories):
- Story 2.1: Admin authentication (basic auth)
- Story 2.2: Gemeente CRUD operations (Create, Read, Update, Delete)
- Story 2.3: Service CRUD operations
- Story 2.4: Gemeente-Service association management
- Story 2.5: Data validation and duplicate prevention
- Story 2.6: Basic admin dashboard with data overview

**Total**: 2 epics, 12 stories

_Note: Detailed user stories with acceptance criteria will be generated in epic-stories.md_

## Out of Scope

The following features are explicitly out of scope for this POC but may be considered for future iterations:

**Automation & Integration**:
- Automated dataset synchronization from government APIs
- Integration with existing gemeente websites/portals
- Automated service catalog updates
- Real-time data feeds from municipal systems

**Advanced Features**:
- Multi-language support (beyond Dutch)
- User accounts and personalization
- Search history and favorites
- Advanced analytics and usage tracking
- AI/ML-powered suggestion improvements beyond template-based generation

**Scale & Performance**:
- Production-grade infrastructure
- High-availability architecture
- Support for 1000+ gemeentes
- Load testing beyond 50 concurrent users

**Content & Data**:
- Comprehensive service catalog (starting with subset)
- Detailed service descriptions and requirements
- Integration with appointment scheduling systems
- Payment processing for services

**Reason for Deferral**: Focus POC on validating core value proposition (question-based suggestions) before investing in automation and scale infrastructure.

## Assumptions and Dependencies

### Assumptions

**A1**: Manual dataset management is acceptable for POC phase - admin users can maintain 50+ gemeentes and 100+ services without automation

**A2**: Template-based question generation (non-AI/ML) can achieve sufficient quality and naturalness for Dutch language suggestions

**A3**: 200ms response time is achievable with template engine approach (not requiring heavy NLP processing)

**A4**: Target users (Dutch citizens) have basic internet literacy and can interact with a search-style interface

**A5**: Initial dataset will focus on common/high-demand services rather than comprehensive catalog

**A6**: Basic authentication is sufficient security for POC admin interface

### Dependencies

**D1**: Dutch language NLP library (for fuzzy matching, stemming) - needs research/selection during tech spec phase

**D2**: Access to sample gemeente and service data to seed initial dataset

**D3**: Hosting/infrastructure for demo deployment (development environment)

**D4**: Stakeholder availability for UX testing and feedback sessions

**D5**: No dependency on existing government systems/APIs (greenfield advantage)

---

## Next Steps

Since this is a Level 2 project, you need solutioning before implementation.

### Phase 1: Solution Architecture and Design (REQUIRED)

**Start new chat with solutioning workflow and provide:**

1. This PRD: `/Users/koop/PycharmProjects/ONLSuggest/project1/docs/PRD.md`
2. Epic structure: `/Users/koop/PycharmProjects/ONLSuggest/project1/docs/epic-stories.md`
3. Project analysis: `/Users/koop/PycharmProjects/ONLSuggest/project1/docs/project-workflow-analysis.md`

**Command:** Run `3-solutioning` workflow to generate:
- `solution-architecture.md` - Overall technical architecture
- `tech-spec-epic-1.md` - Query Suggestion Engine technical spec
- `tech-spec-epic-2.md` - Admin Data Management technical spec

**Critical Decisions Needed in Tech Spec:**
- Dutch NLP library selection (D1)
- Web framework choice
- Database selection
- Template engine approach
- Performance optimization strategy for <200ms

### Phase 2: UX Specification (HIGHLY RECOMMENDED)

**Why:** You explicitly want to "brainstorm and test many UX approaches" - this workflow is designed for that.

**Command:** Run UX specification workflow via `2-plan` then select "UX specification"

**Generates:**
- `ux-specification.md` - Multiple UX interaction patterns
- Component library exploration
- A/B testing strategy
- Wireframes/mockups for different approaches

**Value:** Explores dropdown vs. cards, single vs. multi-column layouts, animation patterns, etc.

### Phase 3: Early Preparation

**Before Development Starts:**

- [ ] **Acquire sample dataset** (D2)
  - 5-10 gemeentes (e.g., Amsterdam, Rotterdam, Utrecht, Den Haag, Eindhoven)
  - 20-30 common services (parkeervergunning, paspoort, rijbewijs, etc.)
  - Create initial seed data file

- [ ] **Set up hosting/infrastructure** (D3)
  - Development environment
  - Demo deployment platform

- [ ] **Schedule stakeholder reviews**
  - PRD approval session
  - UX feedback sessions (D4)

### Phase 4: Development Preparation

**After Tech Spec Complete:**

- [ ] **Set up development environment**
  - Repository initialization
  - Install dependencies (Dutch NLP library, web framework, etc.)
  - Database setup
  - CI/CD pipeline

- [ ] **Create sprint plan**
  - Story prioritization (suggest: Epic 1 Stories 1.1-1.3 first sprint)
  - Sprint boundaries (2-week sprints recommended)
  - Resource allocation

### Complete Workflow Sequence

```
✅ 1. PRD Complete (YOU ARE HERE)
📋 2. Run 3-solutioning workflow → tech specs
🎨 3. Run UX specification workflow → UX exploration
📊 4. Acquire sample data
🏗️ 5. Set up infrastructure
💻 6. Begin development (Epic 1, Story 1.1)
```

## Document Status

- [ ] Goals and context validated with stakeholders
- [ ] All functional requirements reviewed
- [ ] User journeys cover all major personas
- [ ] Epic structure approved for phased delivery
- [ ] Ready for architecture phase

_Note: See technical-decisions.md for captured technical context_

---

_This PRD adapts to project level Level 2 (Small complete system) - providing appropriate detail without overburden._