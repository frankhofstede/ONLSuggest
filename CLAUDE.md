# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ONLSuggest is a Python 3.12 web application project for Dutch government service discovery through intelligent query suggestions.

## Project Planning Status - 2025-10-06

### ✅ COMPLETED: PRD Phase
**Current Phase:** Planning complete, ready for solutioning

**Completed Documents:**
- `/project1/docs/PRD.md` - Product Requirements Document (Level 2)
- `/project1/docs/epic-stories.md` - 2 Epics, 12 User Stories
- `/project1/docs/project-workflow-analysis.md` - Project classification and routing
- `/project1/docs/PRD-validation-report.md` - Cohesion validation (14/16 pass)

**Project Classification:**
- **Level:** 2 (Small complete system)
- **Type:** Web application
- **Field:** Greenfield
- **Scale:** 8-12 stories, 1-2 epics, 4-8 week MVP
- **Deployment:** Demo/POC

**Core Concept:**
Query suggestion system that transforms partial Dutch input into full-text questions, helping citizens find gemeente (municipal) services without knowing official terminology.

### 🎯 NEXT IMMEDIATE ACTIONS

When you return, Frank needs to:

1. **Run `/bmad:bmm:agents:architect` (3-solutioning workflow)** - REQUIRED
   - Input: PRD.md, epic-stories.md, project-workflow-analysis.md
   - Output: solution-architecture.md, tech-spec-epic-1.md, tech-spec-epic-2.md
   - Critical decisions: Dutch NLP library, web framework, database, template engine

2. **Run UX Specification Workflow** - HIGHLY RECOMMENDED
   - Frank wants to "brainstorm and test many UX approaches"
   - Command: `/bmad:bmm:agents:pm` then select option 2 (UX specification)
   - Output: ux-specification.md with multiple interaction patterns

3. **Acquire sample dataset**
   - 5-10 gemeentes (Amsterdam, Rotterdam, Utrecht, etc.)
   - 20-30 services (parkeervergunning, paspoort, rijbewijs, etc.)

### Session Context for Continuity

**Last Agent:** Product Manager (John) - `/bmad:bmm:agents:pm`
**Last Action:** Completed PRD workflow Step 12 (Next Steps generation)
**User Preference:** Frank wants to explore multiple UX approaches before committing to design

**Key Technical Preferences Captured:**
- Manual dataset management (admin interface)
- Question-based suggestions (not autocomplete)
- Template-based generation (not AI/ML initially)
- Sub-200ms response time requirement
- Dutch language only for POC
- Basic auth for admin (POC security)

**To Resume:**
Either start fresh with architect agent, or if user says "continue" - remind them they completed PRD and should now run solutioning workflow.

## Development Environment

### Setup
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt
```

### Python Version
- Python 3.12

## Architecture

### Communication Protocol
- All communication between components uses ONLY A2A (as per global architecture standards)

## Development Workflow

### Before Development
1. **Never start developing without explicit approval**
2. **Explain planned changes first and wait for confirmation**
3. **No shortcuts without explicit permission**

### After Testing
- **Always kill processes** so they can be run manually in terminal

### Code Quality
- **Verify functionality with tests** before claiming completion
- **Never claim "fully functional" without proof**
