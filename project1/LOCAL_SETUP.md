# Local Development Setup

## Current Status

- **Version**: `vercel-deployment-v1` (tagged in git)
- **Vercel Deployment**: Working but slow (~2.5s response time)
- **Local Development**: Recommended for now

## Quick Start

### Backend (Port 8000)
```bash
cd /Users/koop/PycharmProjects/ONLSuggest/project1/backend
python -m uvicorn app.index:app --reload --port 8000
```

### Frontend (Port 3000)
```bash
cd /Users/koop/PycharmProjects/ONLSuggest/project1/frontend
npm run dev
```

## Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin**: http://localhost:3000/admin

## Admin Credentials

- Username: `admin`
- Password: `onlsuggest2024`

## Current Issues

### Vercel Deployment
1. **Slow Response Time**: Template engine takes ~2.5 seconds
   - Loads ALL services from database
   - Loads ALL gemeentes
   - Loads ALL associations
   - Performs NLP matching on everything
   - Generates templates

2. **KOOP API Not Accessible**:
   - Hostname `onl-suggester.koop-innovatielab-tst.test5.s15m.nl` cannot be resolved from Vercel's network
   - Would need public/accessible KOOP API endpoint

### Performance Issues
- Current template engine is not optimized
- Should use indexed queries or caching
- OR use fast KOOP API if accessible

## Architecture

### Backend (`/project1/backend/`)
- **FastAPI** application
- **PostgreSQL** (Neon) database
- **psycopg2** for database access
- Suggestion engines:
  - `template`: Uses database + NLP matching (slow)
  - `koop`: Uses external API (not accessible from Vercel)

### Frontend (`/project1/frontend/`)
- **React 18** with TypeScript
- **Vite** build tool
- Custom CSS (no Tailwind)

## Database

Using Neon PostgreSQL:
- Connection configured via `DATABASE_URL` environment variable
- Schema: gemeentes, services, associations tables
- Currently has 3 gemeentes, 4 services each

## Reference Version

To restore Vercel deployment version:
```bash
git checkout vercel-deployment-v1
```

## Next Steps

1. Optimize database queries for template engine
2. Find accessible KOOP API endpoint
3. Consider own hosting environment (not Vercel)
