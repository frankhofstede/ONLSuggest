# ONLSuggest Deployment Guide (Render.com)

## Quick Deploy to Render

### Option 1: One-Click Deploy (Blueprint)

1. **Push to GitHub** (if not already):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - ONLSuggest v1"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy via Render Dashboard**:
   - Go to https://dashboard.render.com
   - Click **"New +"** → **"Blueprint"**
   - Connect your GitHub repository
   - Select `render.yaml`
   - Click **"Apply"**

   Render will automatically create:
   - ✅ Backend API (FastAPI)
   - ✅ Frontend (React)
   - ✅ PostgreSQL database
   - ✅ Redis cache

3. **Wait for deployment** (~5-10 minutes)
   - Backend will run migrations automatically
   - Seed data will be loaded
   - Admin user created (admin/admin123)

4. **Access your app**:
   - Frontend: `https://onlsuggest-frontend.onrender.com`
   - Backend API: `https://onlsuggest-api.onrender.com`
   - API Docs: `https://onlsuggest-api.onrender.com/docs`

---

### Option 2: Manual Deploy

#### Step 1: Create PostgreSQL Database

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name:** `onlsuggest-db`
   - **Database:** `onlsuggest`
   - **User:** `onlsuggest`
   - **Plan:** Free
4. Click **"Create Database"**
5. **Copy** the **Internal Database URL** (starts with `postgresql://`)

#### Step 2: Create Redis Instance

1. Click **"New +"** → **"Redis"**
2. Configure:
   - **Name:** `onlsuggest-redis`
   - **Plan:** Free
3. Click **"Create Redis"**
4. **Copy** the **Internal Redis URL** (starts with `redis://`)

#### Step 3: Deploy Backend

1. Click **"New +"** → **"Web Service"**
2. **Connect your GitHub repo**
3. Configure:
   - **Name:** `onlsuggest-api`
   - **Runtime:** Docker
   - **Dockerfile Path:** `./backend/Dockerfile`
   - **Docker Context:** `./backend`
   - **Plan:** Free

4. **Environment Variables:**
   ```
   DATABASE_URL=<paste-database-url-from-step-1>
   REDIS_URL=<paste-redis-url-from-step-2>
   DEBUG=false
   SECRET_KEY=<generate-random-secret-min-32-chars>
   CORS_ORIGINS=["https://onlsuggest-frontend.onrender.com"]
   ```

5. **Advanced Settings:**
   - **Health Check Path:** `/health`

6. Click **"Create Web Service"**

#### Step 4: Deploy Frontend

1. Click **"New +"** → **"Static Site"**
2. **Connect your GitHub repo**
3. Configure:
   - **Name:** `onlsuggest-frontend`
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`

4. **Environment Variables:**
   ```
   VITE_API_URL=https://onlsuggest-api.onrender.com
   ```

5. **Rewrite Rules** (for SPA routing):
   - Source: `/*`
   - Destination: `/index.html`

6. Click **"Create Static Site"**

---

## Post-Deployment

### 1. Verify Backend

Visit: `https://onlsuggest-api.onrender.com/health`

Should return:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "ONLSuggest API"
}
```

### 2. Test API

```bash
curl -X POST https://onlsuggest-api.onrender.com/api/v1/suggestions \
  -H "Content-Type: application/json" \
  -d '{"query":"park"}'
```

### 3. Access Frontend

Visit: `https://onlsuggest-frontend.onrender.com`

Should see the SearchBox component.

### 4. Check Logs

- Backend logs: Dashboard → onlsuggest-api → Logs
- Check for migration success
- Check for seed data loaded

---

## Environment Variables Reference

### Backend (onlsuggest-api)

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host/db` |
| `REDIS_URL` | Redis connection string | `redis://host:port` |
| `DEBUG` | Debug mode | `false` |
| `SECRET_KEY` | Secret for JWT/sessions | Random 32+ char string |
| `CORS_ORIGINS` | Allowed frontend origins | `["https://frontend.onrender.com"]` |

### Frontend (onlsuggest-frontend)

| Variable | Description | Example |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `https://onlsuggest-api.onrender.com` |

---

## Troubleshooting

### Backend won't start

**Check logs for:**
- Database connection errors
- Missing environment variables
- Migration failures

**Solution:**
```bash
# Manually run migrations (in Render Shell)
alembic upgrade head
python scripts/create_admin.py
python scripts/seed_data.py
```

### Frontend can't reach backend

**Check:**
1. CORS_ORIGINS includes frontend URL
2. VITE_API_URL is set correctly
3. Backend health check passes

### Redis connection errors

**Check:**
- Redis instance is running
- REDIS_URL is correct
- Fallback: System works without Redis (no caching)

### Database migrations fail

**Solution:**
```bash
# Access Render Shell
alembic downgrade -1
alembic upgrade head
```

---

## Free Tier Limitations

**Render Free Tier:**
- ✅ Backend API (750 hours/month)
- ✅ PostgreSQL (90 days, then expires - upgrade to Starter)
- ✅ Redis (limited memory)
- ✅ Static site (unlimited)
- ⚠️ Services spin down after 15min inactivity (50s cold start)

**Recommendations:**
- Use **Starter Plan** ($7/month) for persistent database
- Upgrade backend to **Starter** to avoid cold starts

---

## Production Checklist

Before going live:

- [ ] Change admin password from default
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS only
- [ ] Set up custom domain
- [ ] Configure monitoring
- [ ] Set up backups (PostgreSQL)
- [ ] Review CORS origins
- [ ] Add rate limiting
- [ ] Set up error tracking (Sentry)

---

## Custom Domain (Optional)

1. Go to onlsuggest-frontend settings
2. Click **"Custom Domains"**
3. Add your domain (e.g., `onlsuggest.nl`)
4. Update DNS records as instructed
5. Update CORS_ORIGINS in backend

---

## Monitoring

**Health Endpoints:**
- Backend: `/health`
- Database: `/api/test/db`
- Redis: `/api/test/redis`

**Set up UptimeRobot or similar** to ping `/health` every 5 minutes.

---

## Support

**Render Docs:** https://render.com/docs
**ONLSuggest Issues:** <your-github-repo>/issues

---

## Cost Estimate

**Free Tier (POC):**
- $0/month
- Database expires after 90 days

**Starter Tier (Production):**
- Backend: $7/month
- PostgreSQL: $7/month
- Redis: Free
- Frontend: Free
- **Total: ~$14/month**

**Recommended for production:**
- Upgrade to Starter for persistent database
- Consider Professional ($25/month) for better performance

---

## Next Steps

1. ✅ Deploy to Render
2. ✅ Test all functionality
3. ✅ Change admin password
4. ⏭️ Add custom domain (optional)
5. ⏭️ Implement Epic 2 (Admin interface)
6. ⏭️ Add more gemeentes and services
