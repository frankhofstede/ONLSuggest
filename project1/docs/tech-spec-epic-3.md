
# Tech Spec: Epic 3 - KOOP Suggester API Integration

**Author:** John (Product Manager) + Winston (Architect, pending)
**Date:** 2025-10-10
**Epic:** Epic 3 - KOOP Suggester API Integration
**Status:** Draft (Awaiting Architect Review)

---

## Epic Overview

**Epic Goal:** Integrate external KOOP Suggester API as an alternative suggestion engine with admin-controlled feature toggle

**Business Value:** Validates enterprise-grade government API integration while maintaining current template engine as fallback, enabling A/B testing and gradual migration strategy

**Stories Covered:**
- Story 3.1: Admin Feature Toggle for Suggestion Engine Selection
- Story 3.2: KOOP API Proxy Endpoint
- Story 3.3: Category-Based Suggestion Display
- Story 3.4: URL-Based Question Examples
- Story 3.5: AI Document Summary with Streaming Display
- Story 3.6: Feature Flag Testing and Validation

**Dependencies:**
- Epic 1 complete (existing template engine)
- Epic 2 complete (admin interface)
- KOOP API production-ready: https://onl-suggester.koop-innovatielab-tst.test5.s15m.nl

**Estimated Effort:** 2-4 weeks

---

## Architecture Context

**From solution-architecture.md:**

**Existing Tech Stack (from Epic 1 & 2):**
- Backend: Python 3.12, Vercel Serverless Functions
- Frontend: React 18.2.0, TypeScript 5.3.0
- Database: Neon Postgres (serverless)
- State: Custom React hooks

**New Integrations for Epic 3:**
- KOOP Suggester API (external service)
- Server-Sent Events or streaming for AI summaries
- Feature flag storage in database

**Performance Target:** Maintain <200ms P95 latency (with potential network overhead from external API)

---

## External API Specification

**KOOP Suggester API Documentation:**

**Base URL:** `https://onl-suggester.koop-innovatielab-tst.test5.s15m.nl`

**Endpoint:** `POST /api/suggest` ⚠️ **Note:** Use `/api/suggest` not `/v1/suggest`

**Authentication:** ✅ None required (open API)

**Request Schema:**
```json
{
  "text": "string (required)",  // User query
  "prev_uris": ["string"],     // Optional: Previously selected document URIs
  "categories": ["string"],    // Optional: Filter by categories ("Dienst", "Wegwijzer Overheid")
  "max_items": 25              // Optional: Max suggestions (default 25)
}
```

**Response Schema (VERIFIED via API testing 2025-10-10):**
```json
{
  "suggestions": [
    {
      "category": "Wegwijzer Overheid" | "Dienst",
      "suggest_entries": [
        {
          "id": "string (URL)",           // Unique identifier
          "source": "WEGWIJZER" | "UPL",  // Data source
          "category": "string",            // Same as parent category
          "title": "string",               // Display title
          "helptext_after_select": "string | null",  // Help text for user
          "uri": "string | null",          // Semantic URI (for lookups)
          "url": "string | null",          // Direct web URL
          "url_template": "string | null"  // Template for dynamic URLs
        }
      ]
    }
  ]
}
```

**Example Response:**
```json
{
  "suggestions": [
    {
      "category": "Wegwijzer Overheid",
      "suggest_entries": [
        {
          "id": "https://wegwijzer.overheid.nl/parkeren/parkeervergunning-bewoners-aanvragen",
          "source": "WEGWIJZER",
          "category": "Wegwijzer Overheid",
          "title": "Wegwijzer: Parkeervergunning voor bewoners aanvragen (Parkeren)",
          "helptext_after_select": null,
          "uri": null,
          "url": "https://wegwijzer.overheid.nl/parkeren/parkeervergunning-bewoners-aanvragen",
          "url_template": null
        }
      ]
    },
    {
      "category": "Dienst",
      "suggest_entries": [
        {
          "id": "http://standaarden.overheid.nl/owms/terms/parkeervergunning",
          "source": "UPL",
          "category": "Dienst",
          "title": "parkeervergunning",
          "helptext_after_select": "Zoek naar de organisatie voor de geselecteerde dienst",
          "uri": "http://standaarden.overheid.nl/owms/terms/parkeervergunning",
          "url": null,
          "url_template": null
        }
      ]
    }
  ]
}
```

**Key Findings:**
- ✅ No authentication required
- ✅ Response is grouped by category with nested `suggest_entries` arrays
- ✅ Each entry has both `url` (direct link) and `uri` (semantic identifier)
- ✅ `title` field contains display text (not full question like template engine)
- ✅ Two data sources: WEGWIJZER and UPL
- ⚠️ No confidence scores provided by API (will need to add default)

**Rate Limits:** Unknown (assume production-ready, monitor in production)

**Timeout Recommendations:** 5 seconds (external API)

---

## Story-by-Story Technical Breakdown

### Story 3.1: Admin Feature Toggle for Suggestion Engine Selection

**Acceptance Criteria:**
- Admin settings page shows "Suggestion Engine" toggle (Template Engine / KOOP API)
- Current selection persists in database
- Toggle takes effect immediately for all users
- Shows current engine status on admin dashboard
- Default: Template Engine (safe fallback)

**Database Schema Addition:**

```sql
-- New table for application settings
CREATE TABLE app_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)  -- Admin user who made change
);

-- Initial setting
INSERT INTO app_settings (key, value, description)
VALUES ('suggestion_engine', 'template', 'Active suggestion engine: template | koop');
```

**Backend Implementation:**

**API Endpoint: `backend/api/admin/settings.py`** (new file)

```python
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Get current suggestion engine setting"""
        # Query: SELECT value FROM app_settings WHERE key = 'suggestion_engine'
        # Return: {"suggestion_engine": "template" | "koop"}
        pass

    def do_PUT(self):
        """Update suggestion engine setting"""
        # Body: {"suggestion_engine": "template" | "koop"}
        # Validate: value in ['template', 'koop']
        # Update: UPDATE app_settings SET value = ?, updated_at = NOW()
        # Response: {"success": true, "suggestion_engine": "koop"}
        pass
```

**Frontend Implementation:**

**Component: `frontend/src/pages/AdminSettings.tsx`** (new file)

```typescript
interface SettingsState {
  suggestionEngine: 'template' | 'koop';
}

const AdminSettings: React.FC = () => {
  const [engine, setEngine] = useState<'template' | 'koop'>('template');
  const [testing, setTesting] = useState(false);

  const handleToggle = async (newEngine: 'template' | 'koop') => {
    // PUT /api/admin/settings
    // Update local state
    setEngine(newEngine);
  };

  const testKOOPConnection = async () => {
    // Test API call to KOOP endpoint
    // Show success/failure message
  };

  return (
    <div className="admin-settings">
      <h2>Suggestion Engine Settings</h2>

      <div className="setting-group">
        <label>
          <input
            type="radio"
            value="template"
            checked={engine === 'template'}
            onChange={() => handleToggle('template')}
          />
          Template Engine (Local)
        </label>

        <label>
          <input
            type="radio"
            value="koop"
            checked={engine === 'koop'}
            onChange={() => handleToggle('koop')}
          />
          KOOP API (External)
        </label>
      </div>

      {engine === 'koop' && (
        <button onClick={testKOOPConnection} disabled={testing}>
          {testing ? 'Testing...' : 'Test KOOP Connection'}
        </button>
      )}

      <div className="status">
        Current Engine: <strong>{engine}</strong>
      </div>
    </div>
  );
};
```

**Dependencies:**
- Database migration to add `app_settings` table
- Admin authentication (already exists from Epic 2)

**Testing:**
- Unit test: Toggle saves to database
- E2E test: Admin changes setting, verify persists
- E2E test: Verify frontend reads correct engine on load

---

### Story 3.2: KOOP API Proxy Endpoint

**Acceptance Criteria:**
- New backend endpoint: `POST /api/v1/suggestions/koop`
- Transforms request format: `{query, max_results}` → `{text, max_items}`
- Adds optional `categories` and `prev_uris` support
- Transforms KOOP response → frontend Suggestion interface
- Returns error with graceful message if KOOP API fails
- Automatic fallback to template engine on KOOP failure

**Backend Implementation:**

**API Endpoint: `backend/api/index.py`** (update existing file)

```python
import requests
from urllib.parse import urljoin

KOOP_API_BASE = "https://onl-suggester.koop-innovatielab-tst.test5.s15m.nl"
KOOP_TIMEOUT = 5  # 5 second timeout

def _call_koop_api(query: str, max_results: int = 5, categories: list = None):
    """
    Call KOOP Suggester API and transform response

    KOOP Response Structure:
    {
      "suggestions": [
        {
          "category": "Dienst" | "Wegwijzer Overheid",
          "suggest_entries": [
            {
              "id": "url",
              "title": "Display title",
              "url": "Direct link",
              "uri": "Semantic URI",
              "helptext_after_select": "Help text"
            }
          ]
        }
      ]
    }

    Returns:
        List of suggestions in our format

    Raises:
        HTTPException on failure
    """
    try:
        # Transform request
        payload = {
            "text": query,
            "max_items": max_results
        }
        if categories:
            payload["categories"] = categories

        # Call KOOP API (use /api/suggest not /v1/suggest)
        response = requests.post(
            urljoin(KOOP_API_BASE, "/api/suggest"),
            json=payload,
            timeout=KOOP_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )

        response.raise_for_status()

        # Transform response
        koop_data = response.json()

        suggestions = []

        # Flatten nested structure: categories -> suggest_entries
        for category_group in koop_data.get("suggestions", []):
            category = category_group.get("category", "Dienst")

            for entry in category_group.get("suggest_entries", []):
                suggestions.append({
                    "suggestion": entry.get("title", ""),
                    "confidence": 0.85,  # KOOP doesn't provide confidence, use default
                    "category": category,
                    "uri": entry.get("uri") or entry.get("url") or entry.get("id"),
                    "helptext": entry.get("helptext_after_select"),
                    "source": entry.get("source"),  # "WEGWIJZER" or "UPL"
                    "service": {
                        "id": None,  # KOOP doesn't map to our service IDs
                        "name": entry.get("title", ""),
                        "description": entry.get("helptext_after_select") or "",
                        "category": category
                    },
                    "gemeente": None  # KOOP doesn't return specific gemeente
                })

        return suggestions[:max_results]  # Respect max_results limit

    except requests.Timeout:
        raise Exception("KOOP API timeout")
    except requests.RequestException as e:
        raise Exception(f"KOOP API error: {str(e)}")

def do_POST(self):
    if self.path == '/api/v1/suggestions':
        # ... existing code ...

        # Check which engine to use
        engine = self._get_suggestion_engine()  # Query app_settings

        if engine == 'koop':
            try:
                suggestions = _call_koop_api(query, max_results)
                response = {
                    "query": request_data.get('query'),
                    "suggestions": suggestions,
                    "response_time_ms": response_time_ms,
                    "using_engine": "koop"
                }
            except Exception as e:
                # Fallback to template engine
                logger.warning(f"KOOP API failed, falling back to template: {e}")
                suggestions = self._generate_suggestions_from_database(query, max_results)
                response = {
                    "query": request_data.get('query'),
                    "suggestions": suggestions,
                    "response_time_ms": response_time_ms,
                    "using_engine": "template",
                    "fallback": True,
                    "fallback_reason": str(e)
                }
        else:
            # Use template engine
            suggestions = self._generate_suggestions_from_database(query, max_results)
            response = {
                "query": request_data.get('query'),
                "suggestions": suggestions,
                "response_time_ms": response_time_ms,
                "using_engine": "template"
            }

        # ... send response ...
```

**Performance Considerations:**
- KOOP API timeout: 5 seconds (configurable)
- Network overhead: ~50-100ms for external API call
- Total P95 target: Still aim for <200ms when possible
- Fallback ensures reliability

**Error Handling:**
- Timeout → Fallback to template engine
- Network error → Fallback to template engine
- Invalid response → Fallback to template engine
- Log all KOOP failures for monitoring

**Dependencies:**
- `requests` library (add to requirements.txt)
- Environment variable for KOOP_API_BASE (optional)

**Testing:**
- Unit test: Transform request format correctly
- Unit test: Transform response format correctly
- Integration test: Mock KOOP API, verify fallback works
- E2E test: Call real KOOP API, verify suggestions appear
- E2E test: Simulate KOOP failure, verify fallback

---

### Story 3.3: Category-Based Suggestion Display

**Acceptance Criteria:**
- Suggestions display category badge/label
- Categories visually distinct (color/icon)
- Can filter suggestions by category (optional)
- Categories returned from KOOP API mapped correctly
- Template engine suggestions marked as "Dienst" (backward compatibility)

**TypeScript Interface Update:**

**File: `frontend/src/types/suggestion.ts`** (update)

```typescript
export interface Suggestion {
  suggestion: string;
  confidence: number;
  service: {
    id: number | null;
    name: string;
    description: string;
    category: string;
  };
  gemeente: string | null;
  category?: string;  // NEW: "Dienst" | "Wegwijzer Overheid"
  uri?: string;       // NEW: For AI summaries
}
```

**Frontend Implementation:**

**Component: `frontend/src/components/CategoryBadge.tsx`** (new file)

```typescript
interface CategoryBadgeProps {
  category: string;
}

const CategoryBadge: React.FC<CategoryBadgeProps> = ({ category }) => {
  const styles = {
    'Dienst': {
      bg: 'bg-blue-100',
      text: 'text-blue-800',
      icon: '🏛️'
    },
    'Wegwijzer Overheid': {
      bg: 'bg-green-100',
      text: 'text-green-800',
      icon: '🗂️'
    }
  };

  const style = styles[category] || styles['Dienst'];

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded text-xs ${style.bg} ${style.text}`}>
      <span className="mr-1">{style.icon}</span>
      {category}
    </span>
  );
};
```

**Update SuggestionList component:**

```typescript
// frontend/src/components/SuggestionList.tsx
const SuggestionItem = ({ suggestion }) => (
  <div className="suggestion-item">
    <CategoryBadge category={suggestion.category || 'Dienst'} />
    <p className="suggestion-text">{suggestion.suggestion}</p>
    <span className="confidence">{(suggestion.confidence * 100).toFixed(0)}%</span>
  </div>
);
```

**Backend Update:**

Ensure template engine suggestions include category:

```python
# backend/api/template_engine.py
def generate_suggestions(...):
    suggestions.append({
        ...existing fields...,
        "category": "Dienst"  # Default for template engine
    })
```

**Dependencies:**
- None (CSS only)

**Testing:**
- Unit test: CategoryBadge renders correct colors
- E2E test: KOOP suggestions show correct categories
- E2E test: Template suggestions show "Dienst"

---

### Story 3.4: URL-Based Question Examples

**Acceptance Criteria:**
- URL parameter `?q=<query>` pre-fills search box
- Search triggers automatically on page load if `?q=` present
- URL parameter `?example=<id>` loads predefined example queries
- Examples configurable in admin interface
- Browser back button clears pre-filled query

**Database Schema:**

```sql
-- New table for example queries
CREATE TABLE example_queries (
    id SERIAL PRIMARY KEY,
    label VARCHAR(200) NOT NULL,
    query_text VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    display_order INT DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sample data
INSERT INTO example_queries (label, query_text, category, display_order)
VALUES
    ('Parkeervergunning Amsterdam', 'parkeervergunning amsterdam', 'Verkeer', 1),
    ('Paspoort aanvragen', 'paspoort aanvragen', 'Burgerzaken', 2),
    ('Afval ophalen Rotterdam', 'afval ophalen rotterdam', 'Milieu', 3);
```

**Frontend Implementation:**

**Component: `frontend/src/pages/PublicSearch.tsx`** (update)

```typescript
import { useSearchParams } from 'react-router-dom';

const PublicSearch: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [query, setQuery] = useState('');

  useEffect(() => {
    // Check for ?q= parameter
    const queryParam = searchParams.get('q');
    if (queryParam) {
      setQuery(queryParam);
      // Auto-trigger search
      handleSearch(queryParam);
    }

    // Check for ?example= parameter
    const exampleId = searchParams.get('example');
    if (exampleId) {
      // Fetch example query from API
      fetch(`/api/examples/${exampleId}`)
        .then(res => res.json())
        .then(data => {
          setQuery(data.query_text);
          handleSearch(data.query_text);
        });
    }
  }, [searchParams]);

  return (
    <div>
      <SearchBox
        value={query}
        onChange={setQuery}
        onSearch={handleSearch}
      />
      <ExampleQueries />  {/* Shows predefined examples */}
    </div>
  );
};
```

**Component: `frontend/src/components/ExampleQueries.tsx`** (new file)

```typescript
const ExampleQueries: React.FC = () => {
  const [examples, setExamples] = useState([]);

  useEffect(() => {
    // Fetch examples from API
    fetch('/api/examples')
      .then(res => res.json())
      .then(data => setExamples(data));
  }, []);

  return (
    <div className="example-queries">
      <h3>Voorbeelden:</h3>
      {examples.map(ex => (
        <a
          key={ex.id}
          href={`?example=${ex.id}`}
          className="example-link"
        >
          {ex.label}
        </a>
      ))}
    </div>
  );
};
```

**Backend API:**

```python
# backend/api/examples.py (new file)
def do_GET(self):
    if self.path == '/api/examples':
        # Return all active examples
        # SELECT * FROM example_queries WHERE active = TRUE ORDER BY display_order
        pass

    if self.path.startswith('/api/examples/'):
        # Return specific example
        example_id = self.path.split('/')[-1]
        # SELECT * FROM example_queries WHERE id = ?
        pass
```

**Admin CRUD for Examples:**

Add to admin interface (similar to gemeentes/services):
- List examples
- Create/edit/delete examples
- Reorder examples

**Dependencies:**
- react-router-dom (already installed)
- Database migration for `example_queries` table

**Testing:**
- E2E test: Navigate to `?q=parkeren`, verify search triggers
- E2E test: Navigate to `?example=1`, verify example loads
- E2E test: Browser back button clears query
- Unit test: URL parameter parsing

---

### Story 3.5: AI Document Summary with Streaming Display

**Acceptance Criteria:**
- Clicking suggestion shows summary panel/modal
- Summary displays incrementally (streaming effect)
- Shows document title from suggestion metadata
- "View Full Document" link opens actual service page
- Close button returns to suggestions
- Loading state while summary generates

**Frontend Implementation:**

**Component: `frontend/src/components/DocumentSummaryModal.tsx`** (new file)

```typescript
interface DocumentSummaryModalProps {
  uri: string;
  title: string;
  onClose: () => void;
}

const DocumentSummaryModal: React.FC<DocumentSummaryModalProps> = ({ uri, title, onClose }) => {
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Call streaming endpoint
    const fetchSummary = async () => {
      try {
        const response = await fetch(`/api/v1/summary?uri=${encodeURIComponent(uri)}`);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          setSummary(prev => prev + chunk);
          setLoading(false);
        }
      } catch (error) {
        console.error('Summary streaming failed:', error);
        setSummary('Samenvatting kon niet worden geladen.');
        setLoading(false);
      }
    };

    fetchSummary();
  }, [uri]);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>

        <h2>{title}</h2>

        {loading && <p>Samenvatting genereren...</p>}

        <div className="summary-text">
          {summary}
        </div>

        <a href={uri} target="_blank" rel="noopener noreferrer" className="view-full-doc">
          Bekijk volledig document →
        </a>
      </div>
    </div>
  );
};
```

**Backend Implementation:**

**API Endpoint: `backend/api/summary.py`** (new file)

```python
from http.server import BaseHTTPRequestHandler
import requests
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Stream AI-generated summary from KOOP API"""
        # Parse ?uri= parameter
        # Call KOOP API (endpoint TBD - may be /v1/summarize?uri=...)
        # Stream response chunks back to frontend

        # Set headers for streaming
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Transfer-Encoding', 'chunked')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()

        try:
            # Call KOOP summary endpoint (streaming)
            response = requests.get(
                f"{KOOP_API_BASE}/v1/summarize",
                params={"uri": uri},
                stream=True,
                timeout=30
            )

            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    self.wfile.write(chunk)
                    self.wfile.flush()

        except Exception as e:
            error_msg = f"Fout bij genereren samenvatting: {str(e)}"
            self.wfile.write(error_msg.encode('utf-8'))
```

**Fallback for Template Engine:**

If using template engine (not KOOP), show service description:

```python
if engine == 'template':
    # No AI summary, return service description from database
    service = get_service_by_uri(uri)
    summary = service.description
    self.wfile.write(summary.encode('utf-8'))
```

**Dependencies:**
- Streaming API support (Server-Sent Events or chunked transfer)
- KOOP API summary endpoint (TBD - requires API documentation)

**Testing:**
- E2E test: Click suggestion, verify modal opens
- E2E test: Verify streaming text appears incrementally
- E2E test: Click "View Full Document", verify link opens
- Unit test: Fallback to service description if KOOP unavailable

---

### Story 3.6: Feature Flag Testing and Validation

**Acceptance Criteria:**
- Playwright E2E test for template engine mode
- Playwright E2E test for KOOP API mode
- Playwright test for toggle switching
- Unit tests for API proxy transformation logic
- Manual test checklist for both engines
- Performance comparison report (template vs KOOP)

**Testing Strategy:**

**E2E Tests: `frontend/tests/epic-3-integration.spec.ts`** (new file)

```typescript
import { test, expect } from '@playwright/test';

test.describe('Epic 3: KOOP Integration', () => {

  test('Admin can toggle suggestion engines', async ({ page }) => {
    // Login as admin
    await page.goto('/admin');
    await page.fill('[name="username"]', 'admin');
    await page.fill('[name="password"]', 'onlsuggest2024');
    await page.click('button[type="submit"]');

    // Navigate to settings
    await page.click('a[href="/admin/settings"]');

    // Toggle to KOOP
    await page.click('input[value="koop"]');
    await expect(page.locator('.status')).toContainText('koop');

    // Toggle back to template
    await page.click('input[value="template"]');
    await expect(page.locator('.status')).toContainText('template');
  });

  test('Template engine generates suggestions', async ({ page }) => {
    // Ensure template mode active
    await page.goto('/admin/settings');
    await page.click('input[value="template"]');

    // Go to public search
    await page.goto('/');
    await page.fill('input[type="text"]', 'parkeren');

    // Wait for suggestions
    await page.waitForSelector('.suggestion-item', { timeout: 2000 });

    const suggestions = await page.$$('.suggestion-item');
    expect(suggestions.length).toBeGreaterThan(0);

    // Verify category badge shows "Dienst"
    await expect(page.locator('.category-badge').first()).toContainText('Dienst');
  });

  test('KOOP API generates suggestions with categories', async ({ page }) => {
    // Enable KOOP mode
    await page.goto('/admin/settings');
    await page.click('input[value="koop"]');

    // Go to public search
    await page.goto('/');
    await page.fill('input[type="text"]', 'parkeervergunning');

    // Wait for suggestions
    await page.waitForSelector('.suggestion-item', { timeout: 5000 });

    const suggestions = await page.$$('.suggestion-item');
    expect(suggestions.length).toBeGreaterThan(0);

    // Verify categories from KOOP API
    const categories = await page.$$('.category-badge');
    expect(categories.length).toBeGreaterThan(0);
  });

  test('URL parameter ?q= triggers search', async ({ page }) => {
    await page.goto('/?q=parkeren');

    // Should auto-trigger search
    await page.waitForSelector('.suggestion-item', { timeout: 2000 });

    const suggestions = await page.$$('.suggestion-item');
    expect(suggestions.length).toBeGreaterThan(0);
  });

  test('AI summary modal displays on click', async ({ page }) => {
    // Enable KOOP mode
    await page.goto('/admin/settings');
    await page.click('input[value="koop"]');

    // Search and click suggestion
    await page.goto('/');
    await page.fill('input[type="text"]', 'parkeren');
    await page.waitForSelector('.suggestion-item');
    await page.click('.suggestion-item:first-child');

    // Verify modal opens
    await expect(page.locator('.modal-content')).toBeVisible();
    await expect(page.locator('.summary-text')).toBeVisible();

    // Wait for streaming content
    await page.waitForTimeout(2000);
    const summaryText = await page.textContent('.summary-text');
    expect(summaryText.length).toBeGreaterThan(0);
  });

  test('Fallback to template engine on KOOP failure', async ({ page }) => {
    // This test would require mocking network to simulate failure
    // Or manually disable KOOP API and verify fallback

    // TODO: Implement with Playwright network interception
  });
});
```

**Unit Tests: `backend/tests/test_koop_proxy.py`** (new file)

```python
import pytest
from backend.api.index import _call_koop_api

def test_transform_request_to_koop_format():
    """Test request transformation"""
    # Mock KOOP API
    # Verify payload format: {text, max_items, categories}
    pass

def test_transform_koop_response_to_suggestion_format():
    """Test response transformation"""
    # Mock KOOP response
    # Verify transformed format matches Suggestion interface
    pass

def test_fallback_on_koop_timeout():
    """Test fallback to template engine on timeout"""
    # Mock timeout
    # Verify template engine called
    pass

def test_fallback_on_koop_error():
    """Test fallback to template engine on error"""
    # Mock error response
    # Verify template engine called
    pass
```

**Performance Testing:**

```bash
# Compare template vs KOOP response times
python backend/tests/performance_comparison.py

# Output:
# Template Engine P95: 45ms
# KOOP API P95: 180ms (includes network overhead)
# Both under 200ms target ✅
```

**Manual Test Checklist:**

```markdown
## Epic 3 Manual Test Checklist

### Story 3.1: Feature Toggle
- [ ] Admin can see toggle in settings
- [ ] Toggle saves to database
- [ ] Toggle persists after page refresh
- [ ] Test KOOP Connection button works

### Story 3.2: KOOP API Proxy
- [ ] KOOP mode returns suggestions
- [ ] Template mode returns suggestions
- [ ] Fallback works when KOOP fails
- [ ] Response time <200ms (template)
- [ ] Response time <300ms (KOOP with network)

### Story 3.3: Categories
- [ ] Suggestions show category badges
- [ ] "Dienst" badge shows blue
- [ ] "Wegwijzer Overheid" badge shows green
- [ ] Template suggestions default to "Dienst"

### Story 3.4: URL Parameters
- [ ] ?q=parkeren pre-fills search
- [ ] ?example=1 loads example query
- [ ] Browser back button clears query
- [ ] Example queries visible on homepage

### Story 3.5: AI Summaries
- [ ] Click suggestion opens modal
- [ ] Summary streams incrementally
- [ ] "View Full Document" link works
- [ ] Close button closes modal
- [ ] Fallback to service description if KOOP unavailable

### Story 3.6: Testing
- [ ] All Playwright tests passing
- [ ] Unit tests passing
- [ ] Performance tests passing
- [ ] Both engines tested in production
```

**Dependencies:**
- Playwright (already installed)
- pytest (already installed)
- Mock KOOP API responses for testing

**Testing:**
- All E2E tests passing
- All unit tests passing
- Performance comparison documented

---

## Data Model Changes

**New Tables:**

```sql
-- Application settings (Story 3.1)
CREATE TABLE app_settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Example queries (Story 3.4)
CREATE TABLE example_queries (
    id SERIAL PRIMARY KEY,
    label VARCHAR(200) NOT NULL,
    query_text VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    display_order INT DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**No changes to existing tables** (gemeentes, services, associations)

---

## API Contracts

**GET /api/admin/settings**

Response:
```json
{
  "suggestion_engine": "template" | "koop"
}
```

**PUT /api/admin/settings**

Request:
```json
{
  "suggestion_engine": "template" | "koop"
}
```

Response:
```json
{
  "success": true,
  "suggestion_engine": "koop"
}
```

**POST /api/v1/suggestions** (updated)

Request:
```json
{
  "query": "parkeren amsterdam",
  "max_results": 5,
  "categories": ["Dienst"]  // NEW: Optional
}
```

Response:
```json
{
  "query": "parkeren amsterdam",
  "suggestions": [
    {
      "suggestion": "Hoe vraag ik een parkeervergunning aan?",
      "confidence": 0.95,
      "category": "Dienst",  // NEW
      "uri": "https://...",  // NEW
      "service": {...},
      "gemeente": "Amsterdam"
    }
  ],
  "response_time_ms": 145,
  "using_engine": "koop",  // NEW
  "fallback": false  // NEW
}
```

**GET /api/v1/summary?uri=...**

Response (streamed):
```
Dit is een samenvatting van het document...
[streaming text chunks]
```

**GET /api/examples**

Response:
```json
[
  {
    "id": 1,
    "label": "Parkeervergunning Amsterdam",
    "query_text": "parkeervergunning amsterdam",
    "category": "Verkeer"
  }
]
```

---

## Deployment Notes

**Environment Variables:**

```bash
# .env (add to existing)
KOOP_API_BASE=https://onl-suggester.koop-innovatielab-tst.test5.s15m.nl
KOOP_API_TIMEOUT=5
KOOP_API_KEY=<if_required>  # TBD
```

**New Dependencies:**

Backend:
```bash
pip install requests==2.31.0  # For KOOP API calls
```

Frontend:
```bash
# No new dependencies (uses existing fetch API)
```

**Database Migrations:**

```bash
# Create migration for new tables
alembic revision --autogenerate -m "Add app_settings and example_queries"
alembic upgrade head
```

**Seed Data:**

```sql
-- Default setting
INSERT INTO app_settings (key, value, description)
VALUES ('suggestion_engine', 'template', 'Active suggestion engine');

-- Example queries
INSERT INTO example_queries (label, query_text, category, display_order)
VALUES
    ('Parkeervergunning', 'parkeervergunning', 'Verkeer', 1),
    ('Paspoort', 'paspoort aanvragen', 'Burgerzaken', 2),
    ('Afval', 'afval ophalen', 'Milieu', 3);
```

---

## Success Criteria

**Definition of Done for Epic 3:**

- ✅ All 6 stories completed and tested
- ✅ Admin can toggle between template and KOOP engines
- ✅ KOOP API proxy functional with fallback
- ✅ Category badges display correctly
- ✅ URL parameters (?q=, ?example=) work
- ✅ AI summaries stream correctly
- ✅ All Playwright E2E tests passing
- ✅ Performance maintained <200ms P95 (template mode)
- ✅ Performance acceptable ~180-250ms (KOOP mode with network)

**Quality Gates:**

- Unit test coverage: >80%
- E2E tests: All passing (both engine modes)
- Performance tests: Both engines benchmarked
- Manual checklist: Fully validated

---

## Open Questions / Risks

**Risks:**

1. **KOOP API availability:** External dependency. Mitigation: Automatic fallback to template engine.

2. **KOOP API performance:** Network latency may exceed 200ms. Mitigation: Accept 200-300ms for KOOP mode, maintain <200ms for template mode.

3. **KOOP API rate limits:** Unknown limits. Mitigation: Monitor usage, implement client-side rate limiting if needed.

4. **AI summary endpoint:** Unclear if KOOP provides streaming summaries. Mitigation: Test API, implement fallback to service description.

**Open Questions:**

1. ~~Does KOOP API require authentication (API key)?~~ → **✅ RESOLVED: No authentication required**

2. ~~What is the exact response schema from KOOP `/v1/suggest`?~~ → **✅ RESOLVED: Documented above, use `/api/suggest`**

3. Does KOOP provide a summary endpoint (`/v1/summarize` or `/api/summarize`)? → **Needs testing** (Story 3.5)

4. What are KOOP's rate limits and SLA? → **Contact KOOP team** (monitor in production)

5. Should we cache KOOP responses in Redis? → **Yes, similar to template caching (5 min TTL)**

6. Should we use `url` or `uri` field for AI summaries? → **Test both** (`url` seems more appropriate for web links)

---

## Next Steps

**Immediate Actions:**

1. **Test KOOP API manually:**
   ```bash
   curl -X POST https://onl-suggester.koop-innovatielab-tst.test5.s15m.nl/v1/suggest \
     -H "Content-Type: application/json" \
     -d '{"text": "parkeervergunning", "max_items": 5}'
   ```

2. **Document actual KOOP response format** (update this spec)

3. **Check KOOP API authentication requirements**

4. **Architect review and approval** (Winston)

5. **Begin Story 3.1 implementation** (Feature Toggle)

**After Epic 3 Complete:**

1. A/B testing with real users (template vs KOOP)
2. Analytics dashboard for engine performance comparison
3. Consider hybrid approach (KOOP for some queries, template for others)

---

**End of Tech Spec: Epic 3 - KOOP Suggester API Integration**

**Status:** Draft - Awaiting:
- KOOP API testing and documentation
- Architect (Winston) review
- Frank's approval to proceed with implementation
