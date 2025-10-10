# ONLSuggest - Dutch Municipal Service Discovery

A web application that helps Dutch citizens find gemeente (municipal) services through intelligent query suggestions. The system transforms partial Dutch input into full-text questions, eliminating the need to know official terminology.

## Project Status

**Phase:** Admin Dashboard MVP Complete (2025-10-08)

### What's Working

✅ **Admin Dashboard**
- Full authentication (Basic Auth)
- CRUD operations for gemeentes, services, and associations
- Real-time data management with Neon Postgres
- All 12 Playwright E2E tests passing

✅ **Deployment**
- Frontend: https://frontend-rust-iota-49.vercel.app
- Backend: https://backend-black-xi.vercel.app
- Admin Panel: https://frontend-rust-iota-49.vercel.app/admin

✅ **Test Data**
- 3 Gemeentes: Amsterdam, Rotterdam, Utrecht
- 4 Services: Parkeervergunning, Paspoort aanvragen, Verhuizing doorgeven, Trouwen
- 12 Active associations

### Admin Access

```
Username: admin
Password: onlsuggest2024
```

## Technical Stack

### Backend (`/backend`)
- **Language:** Python 3.12
- **Database:** Neon Postgres (serverless)
- **ORM:** psycopg2-binary
- **Deployment:** Vercel Serverless Functions
- **API Endpoints:**
  - `/api/admin/*` - Admin CRUD operations
  - `/api/suggestions` - Query suggestion endpoint (WIP)

### Frontend (`/frontend`)
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **Styling:** Custom CSS
- **Testing:** Playwright
- **Routes:**
  - `/` - Public search interface (WIP)
  - `/admin` - Admin dashboard
  - `/admin/gemeentes` - Gemeentes management
  - `/admin/services` - Services management
  - `/admin/associations` - Associations management

### Database Schema

```sql
-- Gemeentes (municipalities)
CREATE TABLE gemeentes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Services
CREATE TABLE services (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    keywords TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Associations (gemeente <-> service)
CREATE TABLE associations (
    id SERIAL PRIMARY KEY,
    gemeente_id INTEGER REFERENCES gemeentes(id) ON DELETE CASCADE,
    service_id INTEGER REFERENCES services(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(gemeente_id, service_id)
);
```

## Development Setup

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://..."
```

### Frontend

```bash
cd frontend
npm install
npm run dev  # Development server on http://localhost:5173
```

### Testing

```bash
cd frontend
npx playwright test                    # Run all tests
npx playwright test --headed          # Run with browser visible
npx playwright test associations-delete-test.spec.ts  # Run specific test
```

## Project Structure

```
project1/
├── backend/
│   ├── api/
│   │   ├── admin.py          # Admin CRUD endpoints
│   │   ├── database.py       # Database layer
│   │   └── index.py          # Main API endpoints
│   ├── database.py           # Database utilities (root)
│   ├── requirements.txt      # Python dependencies
│   └── vercel.json          # Vercel deployment config
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── AdminDashboard.tsx
│   │   │   ├── AdminGemeentes.tsx
│   │   │   ├── AdminServices.tsx
│   │   │   └── AdminAssociations.tsx
│   │   ├── components/
│   │   │   ├── SearchBox.tsx
│   │   │   ├── SuggestionList.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorMessage.tsx
│   │   ├── utils/
│   │   │   └── adminApi.ts
│   │   └── App.tsx
│   ├── tests/
│   │   ├── admin-full-test.spec.ts
│   │   ├── admin-crud-test.spec.ts
│   │   └── associations-delete-test.spec.ts
│   └── playwright.config.ts
│
└── docs/
    ├── PRD.md
    ├── epic-stories.md
    └── project-workflow-analysis.md
```

## Recent Fixes (2025-10-08)

1. **DateTime JSON Serialization** - Added custom encoder for Python datetime objects in API responses
2. **Associations Delete** - Fixed missing association IDs by creating dedicated `/api/admin/associations` endpoint with enriched data
3. **Smart Loading Detection** - Playwright tests now poll every 10s for data load instead of fixed 30s timeout
4. **Project Cleanup** - Removed duplicate `/frontend/` and `/project1/api/` folders

## Known Issues

- Associations endpoint takes ~30 seconds to load due to N+1 query pattern (needs SQL JOIN optimization)
- No caching layer implemented
- Public search interface not yet implemented

## Next Steps

1. **Implement Public Search UI**
   - SearchBox with Dutch character support (ë, ï, ü, é)
   - SuggestionList with question templates
   - Integration with `/api/suggestions`

2. **Complete Suggestion Algorithm**
   - Keyword matching logic
   - Template-based question generation
   - Sub-200ms response time optimization

3. **Testing & Polish**
   - User testing with real Dutch queries
   - Performance optimization
   - WCAG 2.1 AA accessibility compliance

## Environment Variables

### Backend `.env`
```bash
DATABASE_URL=postgresql://user:pass@host/db
```

### Frontend `.env.production`
```bash
VITE_API_URL=https://backend-black-xi.vercel.app
```

## License

[To be determined]
