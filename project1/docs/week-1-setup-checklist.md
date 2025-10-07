# Week 1: Development Environment Setup Checklist

**Project:** ONLSuggest-v1
**Phase:** Environment Setup & Preparation
**Duration:** Week 1 (5 days)
**Goal:** Complete development environment ready for Epic 1, Story 1.1 implementation

---

## Day 1: Repository & Backend Foundation

### ✅ Task 1.1: Repository Structure Setup
**Estimated Time:** 30 minutes

- [ ] Navigate to project root
  ```bash
  cd /Users/koop/PycharmProjects/ONLSuggest/project1
  ```

- [ ] Create monorepo directory structure
  ```bash
  mkdir -p backend/app/{models,schemas,routers,services,middleware,core,utils}
  mkdir -p backend/app/services
  mkdir -p backend/alembic/versions
  mkdir -p backend/tests/{unit,integration}
  mkdir -p backend/scripts
  mkdir -p frontend/src/{components/{public,admin,common},pages/{admin},api,hooks,contexts,types,utils}
  mkdir -p frontend/public
  mkdir -p frontend/tests
  ```

- [ ] Verify structure created
  ```bash
  tree -L 3 -d
  ```

**Acceptance:** All directories exist, visible in `tree` output

---

### ✅ Task 1.2: Python Virtual Environment
**Estimated Time:** 15 minutes

- [ ] Verify Python version
  ```bash
  python3 --version  # Should be 3.11 or higher
  ```

- [ ] Create virtual environment
  ```bash
  cd backend
  python3 -m venv .venv
  ```

- [ ] Activate virtual environment
  ```bash
  source .venv/bin/activate
  ```

- [ ] Verify activation (prompt should show `(.venv)`)
  ```bash
  which python  # Should point to .venv/bin/python
  ```

**Acceptance:** `(.venv)` prefix in terminal, `python --version` shows 3.11+

---

### ✅ Task 1.3: Backend Dependencies Installation
**Estimated Time:** 20 minutes

- [ ] Create `backend/requirements.txt`
  ```txt
  # Web Framework
  fastapi==0.109.0
  uvicorn[standard]==0.27.0

  # Database
  sqlalchemy==2.0.25
  asyncpg==0.29.0
  psycopg2-binary==2.9.9
  alembic==1.13.0

  # Redis
  redis==5.0.1

  # NLP
  spacy==3.7.2
  rapidfuzz==3.5.2

  # Security
  bcrypt==4.1.2
  python-multipart==0.0.6

  # Rate Limiting
  slowapi==0.1.9

  # Logging
  structlog==24.1.0

  # Validation
  pydantic==2.5.0
  pydantic-settings==2.1.0

  # CORS
  python-jose[cryptography]==3.3.0

  # Testing
  pytest==7.4.0
  pytest-asyncio==0.21.0
  httpx==0.25.0
  ```

- [ ] Install dependencies
  ```bash
  pip install --upgrade pip
  pip install -r requirements.txt
  ```

- [ ] Verify installations
  ```bash
  pip list | grep fastapi
  pip list | grep spacy
  ```

- [ ] Download Dutch NLP model
  ```bash
  python -m spacy download nl_core_news_sm
  ```

- [ ] Verify spaCy model
  ```python
  python -c "import spacy; nlp = spacy.load('nl_core_news_sm'); print('Dutch model loaded successfully')"
  ```

**Acceptance:** All packages installed, Dutch model loads without error

---

### ✅ Task 1.4: Create Development Requirements
**Estimated Time:** 10 minutes

- [ ] Create `backend/requirements-dev.txt`
  ```txt
  # Development tools
  pytest==7.4.0
  pytest-asyncio==0.21.0
  pytest-cov==4.1.0
  black==23.12.0
  flake8==7.0.0
  mypy==1.8.0

  # Load testing
  locust==2.20.0
  ```

- [ ] Install dev dependencies
  ```bash
  pip install -r requirements-dev.txt
  ```

**Acceptance:** Dev tools installed, `black --version` works

---

## Day 2: Database & Configuration

### ✅ Task 2.1: PostgreSQL Database Setup
**Estimated Time:** 45 minutes

**Option A: Docker (Recommended)**

- [ ] Create `docker-compose.yml` in project root
  ```yaml
  version: '3.8'
  services:
    postgres:
      image: postgres:15-alpine
      environment:
        POSTGRES_USER: onlsuggest
        POSTGRES_PASSWORD: devpassword
        POSTGRES_DB: onlsuggest
      ports:
        - "5432:5432"
      volumes:
        - postgres_data:/var/lib/postgresql/data

    redis:
      image: redis:7-alpine
      ports:
        - "6379:6379"

  volumes:
    postgres_data:
  ```

- [ ] Start services
  ```bash
  docker-compose up -d
  ```

- [ ] Verify PostgreSQL running
  ```bash
  docker-compose ps
  psql postgresql://onlsuggest:devpassword@localhost:5432/onlsuggest -c "SELECT version();"
  ```

**Option B: Homebrew (macOS)**

- [ ] Install PostgreSQL
  ```bash
  brew install postgresql@15
  brew services start postgresql@15
  ```

- [ ] Create database
  ```bash
  createdb onlsuggest
  ```

**Configuration:**

- [ ] Create `backend/app/core/config.py`
  ```python
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      # Database
      database_url: str = "postgresql+asyncpg://onlsuggest:devpassword@localhost:5432/onlsuggest"

      # Redis
      redis_url: str = "redis://localhost:6379"

      # Security
      secret_key: str = "dev-secret-key-change-in-production"

      # Admin
      admin_username: str = "admin"
      admin_password: str = "changeme123"

      # App
      app_name: str = "ONLSuggest"
      debug: bool = True

      class Config:
          env_file = ".env"

  settings = Settings()
  ```

- [ ] Create `backend/.env`
  ```bash
  DATABASE_URL=postgresql+asyncpg://onlsuggest:devpassword@localhost:5432/onlsuggest
  REDIS_URL=redis://localhost:6379
  SECRET_KEY=dev-secret-key-please-change
  ADMIN_USERNAME=admin
  ADMIN_PASSWORD=changeme123
  DEBUG=True
  ```

- [ ] Add `.env` to `.gitignore`
  ```bash
  echo ".env" >> backend/.gitignore
  echo ".venv/" >> backend/.gitignore
  echo "__pycache__/" >> backend/.gitignore
  echo "*.pyc" >> backend/.gitignore
  ```

**Acceptance:** PostgreSQL accessible, config loads without error, `.env` excluded from git

---

### ✅ Task 2.2: Database Models
**Estimated Time:** 45 minutes

- [ ] Create `backend/app/models/base.py`
  ```python
  from sqlalchemy.ext.declarative import declarative_base

  Base = declarative_base()
  ```

- [ ] Create `backend/app/models/gemeente.py`
  ```python
  from sqlalchemy import Column, Integer, String, Text, DateTime
  from sqlalchemy.sql import func
  from app.models.base import Base

  class Gemeente(Base):
      __tablename__ = "gemeentes"

      id = Column(Integer, primary_key=True)
      name = Column(String(100), unique=True, nullable=False, index=True)
      description = Column(Text, nullable=True)
      created_at = Column(DateTime, server_default=func.now())
      updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
  ```

- [ ] Create `backend/app/models/service.py`
  ```python
  from sqlalchemy import Column, Integer, String, Text, DateTime
  from sqlalchemy.sql import func
  from app.models.base import Base

  class Service(Base):
      __tablename__ = "services"

      id = Column(Integer, primary_key=True)
      name = Column(String(200), unique=True, nullable=False, index=True)
      description = Column(Text, nullable=False)
      keywords = Column(Text, nullable=True)
      category = Column(String(50), nullable=True)
      created_at = Column(DateTime, server_default=func.now())
      updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
  ```

- [ ] Create `backend/app/models/association.py`
  ```python
  from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
  from sqlalchemy.sql import func
  from app.models.base import Base

  class GemeenteServiceAssociation(Base):
      __tablename__ = "gemeente_service_associations"

      id = Column(Integer, primary_key=True)
      gemeente_id = Column(Integer, ForeignKey('gemeentes.id', ondelete='CASCADE'), nullable=False)
      service_id = Column(Integer, ForeignKey('services.id', ondelete='CASCADE'), nullable=False)
      created_at = Column(DateTime, server_default=func.now())

      __table_args__ = (
          UniqueConstraint('gemeente_id', 'service_id', name='uq_gemeente_service'),
      )
  ```

- [ ] Create `backend/app/models/admin_user.py`
  ```python
  from sqlalchemy import Column, Integer, String, DateTime
  from sqlalchemy.sql import func
  from app.models.base import Base

  class AdminUser(Base):
      __tablename__ = "admin_users"

      id = Column(Integer, primary_key=True)
      username = Column(String(50), unique=True, nullable=False, index=True)
      password_hash = Column(String(255), nullable=False)
      created_at = Column(DateTime, server_default=func.now())
      last_login = Column(DateTime, nullable=True)
  ```

- [ ] Create `backend/app/models/__init__.py`
  ```python
  from app.models.base import Base
  from app.models.gemeente import Gemeente
  from app.models.service import Service
  from app.models.association import GemeenteServiceAssociation
  from app.models.admin_user import AdminUser

  __all__ = ["Base", "Gemeente", "Service", "GemeenteServiceAssociation", "AdminUser"]
  ```

**Acceptance:** All models import without error

---

### ✅ Task 2.3: Database Connection Setup
**Estimated Time:** 20 minutes

- [ ] Create `backend/app/core/database.py`
  ```python
  from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
  from sqlalchemy.orm import sessionmaker
  from app.core.config import settings
  from app.models.base import Base

  # Create async engine
  engine = create_async_engine(
      settings.database_url,
      echo=settings.debug,
      future=True
  )

  # Create async session factory
  async_session_maker = sessionmaker(
      engine,
      class_=AsyncSession,
      expire_on_commit=False
  )

  async def get_db():
      """Dependency for FastAPI routes"""
      async with async_session_maker() as session:
          yield session

  async def init_db():
      """Initialize database (create tables)"""
      async with engine.begin() as conn:
          await conn.run_sync(Base.metadata.create_all)
  ```

**Acceptance:** No import errors when running `python -c "from app.core.database import engine"`

---

### ✅ Task 2.4: Alembic Migration Setup
**Estimated Time:** 30 minutes

- [ ] Initialize Alembic
  ```bash
  cd backend
  alembic init alembic
  ```

- [ ] Edit `backend/alembic.ini` - Update sqlalchemy.url line:
  ```ini
  # sqlalchemy.url = driver://user:pass@localhost/dbname
  # Comment out the above line, we'll use env.py instead
  ```

- [ ] Edit `backend/alembic/env.py` - Replace with:
  ```python
  from logging.config import fileConfig
  from sqlalchemy import engine_from_config, pool
  from alembic import context
  import asyncio
  from sqlalchemy.ext.asyncio import AsyncEngine

  # Import models and config
  from app.models.base import Base
  from app.models import *  # Import all models
  from app.core.config import settings

  config = context.config

  # Set sqlalchemy.url from settings
  config.set_main_option("sqlalchemy.url", settings.database_url.replace('+asyncpg', '').replace('postgresql', 'postgresql+psycopg2'))

  if config.config_file_name is not None:
      fileConfig(config.config_file_name)

  target_metadata = Base.metadata

  def run_migrations_offline() -> None:
      url = config.get_main_option("sqlalchemy.url")
      context.configure(
          url=url,
          target_metadata=target_metadata,
          literal_binds=True,
          dialect_opts={"paramstyle": "named"},
      )

      with context.begin_transaction():
          context.run_migrations()

  def do_run_migrations(connection):
      context.configure(connection=connection, target_metadata=target_metadata)
      with context.begin_transaction():
          context.run_migrations()

  async def run_migrations_online() -> None:
      configuration = config.get_section(config.config_ini_section)
      configuration["sqlalchemy.url"] = settings.database_url.replace('+asyncpg', '').replace('postgresql', 'postgresql+psycopg2')

      connectable = AsyncEngine(
          engine_from_config(
              configuration,
              prefix="sqlalchemy.",
              poolclass=pool.NullPool,
              future=True,
          )
      )

      async with connectable.connect() as connection:
          await connection.run_sync(do_run_migrations)

      await connectable.dispose()

  if context.is_offline_mode():
      run_migrations_offline()
  else:
      asyncio.run(run_migrations_online())
  ```

- [ ] Create initial migration
  ```bash
  alembic revision --autogenerate -m "Initial schema: gemeentes, services, associations, admin_users"
  ```

- [ ] Review migration file in `backend/alembic/versions/`

- [ ] Apply migration
  ```bash
  alembic upgrade head
  ```

- [ ] Verify database created
  ```bash
  psql postgresql://onlsuggest:devpassword@localhost:5432/onlsuggest -c "\dt"
  # Should show: admin_users, gemeentes, services, gemeente_service_associations, alembic_version
  ```

**Acceptance:** PostgreSQL database contains all 5 tables

---

## Day 3: Redis, Scripts & Seed Data

### ✅ Task 3.1: Redis Installation & Setup
**Estimated Time:** 30 minutes

**Option A: Local Redis (macOS)**
- [ ] Install Redis via Homebrew
  ```bash
  brew install redis
  ```

- [ ] Start Redis service
  ```bash
  brew services start redis
  ```

- [ ] Verify Redis running
  ```bash
  redis-cli ping  # Should return: PONG
  ```

**Option B: Redis Cloud (Free Tier)**
- [ ] Visit https://redis.com/try-free/
- [ ] Sign up for free account
- [ ] Create free database (30MB limit, sufficient for POC)
- [ ] Copy connection string
- [ ] Update `backend/.env`:
  ```bash
  REDIS_URL=redis://default:password@redis-12345.c1.us-east-1-2.ec2.cloud.redislabs.com:12345
  ```

**Option C: Docker Redis**
- [ ] Start Redis container
  ```bash
  docker run -d -p 6379:6379 --name onlsuggest-redis redis:7.2-alpine
  ```

- [ ] Verify running
  ```bash
  docker exec -it onlsuggest-redis redis-cli ping
  ```

**Test Redis Connection:**
- [ ] Create test script `backend/test_redis.py`
  ```python
  import asyncio
  from redis import asyncio as aioredis
  from app.core.config import settings

  async def test_redis():
      redis = await aioredis.from_url(settings.redis_url, decode_responses=True)
      await redis.set("test_key", "Hello Redis!")
      value = await redis.get("test_key")
      print(f"Redis test: {value}")
      await redis.close()

  if __name__ == "__main__":
      asyncio.run(test_redis())
  ```

- [ ] Run test
  ```bash
  python test_redis.py  # Should print: Redis test: Hello Redis!
  ```

**Acceptance:** Redis responds to ping, Python test script succeeds

---

### ✅ Task 3.2: Create Admin User Script
**Estimated Time:** 20 minutes

- [ ] Create `backend/app/core/security.py`
  ```python
  import bcrypt
  import secrets
  from datetime import datetime, timedelta

  class SecurityService:
      @staticmethod
      def hash_password(password: str) -> str:
          """Hash password using bcrypt."""
          salt = bcrypt.gensalt()
          hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
          return hashed.decode('utf-8')

      @staticmethod
      def verify_password(password: str, hashed: str) -> bool:
          """Verify password against bcrypt hash."""
          return bcrypt.checkpw(
              password.encode('utf-8'),
              hashed.encode('utf-8')
          )

      @staticmethod
      def generate_session_token() -> str:
          """Generate secure random session token."""
          return secrets.token_urlsafe(32)
  ```

- [ ] Create `backend/scripts/create_admin.py`
  ```python
  import asyncio
  import sys
  from pathlib import Path

  # Add parent directory to path
  sys.path.insert(0, str(Path(__file__).parent.parent))

  from sqlalchemy import select
  from app.core.database import async_session_maker, init_db
  from app.models.admin_user import AdminUser
  from app.core.security import SecurityService
  from app.core.config import settings

  async def create_admin():
      # Initialize database
      await init_db()

      async with async_session_maker() as db:
          # Check if admin exists
          result = await db.execute(
              select(AdminUser).where(AdminUser.username == settings.admin_username)
          )
          existing = result.scalar_one_or_none()

          if existing:
              print(f"Admin user '{settings.admin_username}' already exists")
              return

          # Create admin
          admin = AdminUser(
              username=settings.admin_username,
              password_hash=SecurityService.hash_password(settings.admin_password)
          )
          db.add(admin)
          await db.commit()

          print(f"✅ Admin user created:")
          print(f"   Username: {settings.admin_username}")
          print(f"   Password: {settings.admin_password}")
          print(f"   ⚠️  CHANGE PASSWORD IN PRODUCTION!")

  if __name__ == "__main__":
      asyncio.run(create_admin())
  ```

- [ ] Run script
  ```bash
  cd backend
  python scripts/create_admin.py
  ```

- [ ] Verify admin created
  ```bash
  sqlite3 app.db "SELECT username FROM admin_users;"
  # Should show: admin
  ```

**Acceptance:** Admin user created, can query from database

---

### ✅ Task 3.3: Create Seed Data Script
**Estimated Time:** 45 minutes

- [ ] Create `backend/scripts/seed_data.py`
  ```python
  import asyncio
  import sys
  from pathlib import Path

  sys.path.insert(0, str(Path(__file__).parent.parent))

  from sqlalchemy import select
  from app.core.database import async_session_maker, init_db
  from app.models.gemeente import Gemeente
  from app.models.service import Service
  from app.models.association import GemeenteServiceAssociation

  # Sample gemeentes
  GEMEENTES = [
      {"name": "Amsterdam", "description": "Hoofdstad van Nederland"},
      {"name": "Rotterdam", "description": "Havenstad"},
      {"name": "Utrecht", "description": "Centraal in Nederland"},
      {"name": "Den Haag", "description": "Regeringszetel"},
      {"name": "Eindhoven", "description": "Technologiestad in Brabant"},
      {"name": "Groningen", "description": "Stad in het noorden"},
      {"name": "Tilburg", "description": "Stad in Noord-Brabant"},
      {"name": "Almere", "description": "Jonge stad in Flevoland"},
  ]

  # Sample services
  SERVICES = [
      {
          "name": "Parkeervergunning",
          "description": "Vergunning voor parkeren in de stad voor bewoners",
          "keywords": "parkeren,bewonersvergunning,auto,parkeerplaats,vergunning",
          "category": "Verkeer"
      },
      {
          "name": "Paspoort aanvragen",
          "description": "Nieuwe paspoort aanvragen of verlengen",
          "keywords": "paspoort,identiteitsbewijs,reisdocument,ID",
          "category": "Burgerzaken"
      },
      {
          "name": "Rijbewijs aanvragen",
          "description": "Rijbewijs aanvragen of vernieuwen",
          "keywords": "rijbewijs,rijbewijs verlengen,rijbewijs aanvragen,autorijbewijs",
          "category": "Burgerzaken"
      },
      {
          "name": "Afvalcontainer aanvragen",
          "description": "Container voor afvalscheiding aanvragen",
          "keywords": "afval,container,gft,restafval,papier",
          "category": "Milieu"
      },
      {
          "name": "Verhuizing doorgeven",
          "description": "Adreswijziging doorgeven aan gemeente",
          "keywords": "verhuizen,adreswijziging,inschrijven,verhuizing",
          "category": "Burgerzaken"
      },
      {
          "name": "Bouwvergunning",
          "description": "Vergunning voor verbouwing of nieuwbouw",
          "keywords": "bouwen,verbouwen,vergunning,aanbouw,uitbouw",
          "category": "Bouwen & Wonen"
      },
      {
          "name": "Huwelijk voltrekken",
          "description": "Huwelijk of partnerschap registreren",
          "keywords": "trouwen,huwelijk,partnerschap,geregistreerd partnerschap",
          "category": "Burgerzaken"
      },
      {
          "name": "Kinderopvang toeslag",
          "description": "Toeslag aanvragen voor kinderopvang",
          "keywords": "kinderopvang,toeslag,kinderen,opvang,subsidie",
          "category": "Jeugd & Gezin"
      },
      {
          "name": "Uittreksel GBA",
          "description": "Uittreksel uit Gemeentelijke Basisadministratie",
          "keywords": "gba,uittreksel,persoonsgegevens,verklaring",
          "category": "Burgerzaken"
      },
      {
          "name": "Kapvergunning boom",
          "description": "Vergunning om boom te kappen",
          "keywords": "boom,kappen,vergunning,groen",
          "category": "Groen & Milieu"
      },
  ]

  async def seed_data():
      await init_db()

      async with async_session_maker() as db:
          # Check if data already exists
          result = await db.execute(select(Gemeente))
          if result.scalar_one_or_none():
              print("⚠️  Database already contains data. Skipping seed.")
              return

          print("Seeding gemeentes...")
          gemeente_objects = []
          for g_data in GEMEENTES:
              gemeente = Gemeente(**g_data)
              db.add(gemeente)
              gemeente_objects.append(gemeente)

          await db.flush()  # Get IDs
          print(f"✅ Created {len(gemeente_objects)} gemeentes")

          print("\nSeeding services...")
          service_objects = []
          for s_data in SERVICES:
              service = Service(**s_data)
              db.add(service)
              service_objects.append(service)

          await db.flush()  # Get IDs
          print(f"✅ Created {len(service_objects)} services")

          print("\nCreating associations (all gemeentes support all services)...")
          association_count = 0
          for gemeente in gemeente_objects:
              for service in service_objects:
                  assoc = GemeenteServiceAssociation(
                      gemeente_id=gemeente.id,
                      service_id=service.id
                  )
                  db.add(assoc)
                  association_count += 1

          await db.commit()
          print(f"✅ Created {association_count} associations")

          print("\n" + "="*50)
          print("✅ Seed data complete!")
          print("="*50)
          print(f"Gemeentes: {len(gemeente_objects)}")
          print(f"Services: {len(service_objects)}")
          print(f"Associations: {association_count}")

  if __name__ == "__main__":
      asyncio.run(seed_data())
  ```

- [ ] Run seed script
  ```bash
  cd backend
  python scripts/seed_data.py
  ```

- [ ] Verify seed data
  ```bash
  sqlite3 app.db "SELECT COUNT(*) FROM gemeentes;"  # Should show: 8
  sqlite3 app.db "SELECT COUNT(*) FROM services;"   # Should show: 10
  sqlite3 app.db "SELECT COUNT(*) FROM gemeente_service_associations;"  # Should show: 80
  ```

**Acceptance:** Database contains 8 gemeentes, 10 services, 80 associations

---

## Day 4: Frontend Setup

### ✅ Task 4.1: Node.js & Frontend Initialization
**Estimated Time:** 30 minutes

- [ ] Verify Node.js version
  ```bash
  node --version  # Should be v18 or higher
  npm --version
  ```

- [ ] Create React + TypeScript + Vite project
  ```bash
  cd /Users/koop/PycharmProjects/ONLSuggest/project1
  npm create vite@latest frontend -- --template react-ts
  ```

- [ ] Navigate to frontend
  ```bash
  cd frontend
  ```

- [ ] Install dependencies
  ```bash
  npm install
  ```

- [ ] Test dev server
  ```bash
  npm run dev
  # Visit http://localhost:5173
  # Should see Vite + React default page
  ```

- [ ] Stop dev server (Ctrl+C)

**Acceptance:** Vite dev server runs, default React page visible

---

### ✅ Task 4.2: Install Frontend Dependencies
**Estimated Time:** 20 minutes

- [ ] Install core dependencies
  ```bash
  npm install react-router-dom@6.21.0
  npm install @tanstack/react-query@5.17.0
  npm install axios@1.6.0
  npm install react-hook-form@7.49.0
  ```

- [ ] Install Tailwind CSS
  ```bash
  npm install -D tailwindcss@3.4.0 postcss autoprefixer
  npx tailwindcss init -p
  ```

- [ ] Configure Tailwind - Edit `frontend/tailwind.config.js`:
  ```javascript
  /** @type {import('tailwindcss').Config} */
  export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {},
    },
    plugins: [],
  }
  ```

- [ ] Update `frontend/src/index.css`:
  ```css
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  ```

- [ ] Verify package.json contains all dependencies
  ```bash
  cat package.json
  ```

**Acceptance:** All npm packages installed without errors

---

### ✅ Task 4.3: Frontend Project Structure
**Estimated Time:** 15 minutes

- [ ] Create directory structure
  ```bash
  cd frontend/src
  mkdir -p components/{public,admin,common}
  mkdir -p pages/admin
  mkdir -p api
  mkdir -p hooks
  mkdir -p contexts
  mkdir -p types
  mkdir -p utils
  ```

- [ ] Verify structure
  ```bash
  tree -L 3 src/
  ```

- [ ] Create placeholder files
  ```bash
  touch src/components/public/.gitkeep
  touch src/components/admin/.gitkeep
  touch src/components/common/.gitkeep
  touch src/pages/admin/.gitkeep
  touch src/api/.gitkeep
  touch src/hooks/.gitkeep
  touch src/contexts/.gitkeep
  touch src/types/.gitkeep
  touch src/utils/.gitkeep
  ```

**Acceptance:** All directories exist with .gitkeep files

---

### ✅ Task 4.4: Basic Frontend Configuration
**Estimated Time:** 20 minutes

- [ ] Create `frontend/src/api/client.ts`
  ```typescript
  import axios from 'axios';

  const client = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // Request interceptor to add auth token
  client.interceptors.request.use((config) => {
    const token = localStorage.getItem('admin_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  export default client;
  ```

- [ ] Create `frontend/src/types/suggestion.ts`
  ```typescript
  export interface Suggestion {
    id: string;
    question: string;
    gemeente: string;
    service_id: number;
    service_name: string;
    confidence: number;
  }

  export interface SuggestionResponse {
    suggestions: Suggestion[];
    query: string;
    generated_at: string;
    cached: boolean;
  }
  ```

- [ ] Create `frontend/.env`
  ```bash
  VITE_API_URL=http://localhost:8000
  ```

- [ ] Add `.env` to `.gitignore`
  ```bash
  echo ".env" >> frontend/.gitignore
  echo "node_modules/" >> frontend/.gitignore
  echo "dist/" >> frontend/.gitignore
  ```

**Acceptance:** TypeScript compiles without errors

---

## Day 5: FastAPI Backend & Testing

### ✅ Task 5.1: Basic FastAPI Application
**Estimated Time:** 30 minutes

- [ ] Create `backend/app/main.py`
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  from app.core.config import settings

  app = FastAPI(
      title=settings.app_name,
      debug=settings.debug
  )

  # CORS middleware
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["http://localhost:5173"],  # Vite dev server
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )

  @app.get("/")
  async def root():
      return {"message": "ONLSuggest API is running"}

  @app.get("/health")
  async def health():
      return {"status": "healthy", "version": "0.1.0"}
  ```

- [ ] Test FastAPI app
  ```bash
  cd backend
  uvicorn app.main:app --reload
  # Visit http://localhost:8000
  # Should see: {"message": "ONLSuggest API is running"}
  ```

- [ ] Test health endpoint
  ```bash
  curl http://localhost:8000/health
  # Should return: {"status":"healthy","version":"0.1.0"}
  ```

- [ ] Test OpenAPI docs
  ```bash
  # Visit http://localhost:8000/docs
  # Should see Swagger UI
  ```

- [ ] Stop server (Ctrl+C)

**Acceptance:** FastAPI runs, endpoints respond, Swagger docs visible

---

### ✅ Task 5.2: Test Database Integration
**Estimated Time:** 20 minutes

- [ ] Create test endpoint `backend/app/main.py` (add):
  ```python
  from fastapi import Depends
  from sqlalchemy.ext.asyncio import AsyncSession
  from sqlalchemy import select, func
  from app.core.database import get_db
  from app.models.gemeente import Gemeente
  from app.models.service import Service

  @app.get("/api/test/db")
  async def test_database(db: AsyncSession = Depends(get_db)):
      gemeente_count = await db.scalar(select(func.count(Gemeente.id)))
      service_count = await db.scalar(select(func.count(Service.id)))

      return {
          "database": "connected",
          "gemeentes": gemeente_count,
          "services": service_count
      }
  ```

- [ ] Start server
  ```bash
  uvicorn app.main:app --reload
  ```

- [ ] Test endpoint
  ```bash
  curl http://localhost:8000/api/test/db
  # Should return: {"database":"connected","gemeentes":8,"services":10}
  ```

**Acceptance:** Database connection works, correct counts returned

---

### ✅ Task 5.3: Test Redis Integration
**Estimated Time:** 15 minutes

- [ ] Create Redis client `backend/app/core/redis_client.py`
  ```python
  from redis import asyncio as aioredis
  from app.core.config import settings

  redis_client = None

  async def get_redis():
      global redis_client
      if redis_client is None:
          redis_client = await aioredis.from_url(
              settings.redis_url,
              decode_responses=True
          )
      return redis_client

  async def close_redis():
      global redis_client
      if redis_client:
          await redis_client.close()
  ```

- [ ] Add test endpoint to `backend/app/main.py`:
  ```python
  from app.core.redis_client import get_redis

  @app.get("/api/test/redis")
  async def test_redis():
      redis = await get_redis()
      await redis.set("test_key", "Hello from ONLSuggest!")
      value = await redis.get("test_key")
      return {"redis": "connected", "test_value": value}
  ```

- [ ] Test endpoint
  ```bash
  curl http://localhost:8000/api/test/redis
  # Should return: {"redis":"connected","test_value":"Hello from ONLSuggest!"}
  ```

**Acceptance:** Redis connection works, can set/get values

---

### ✅ Task 5.4: Frontend-Backend Integration Test
**Estimated Time:** 25 minutes

- [ ] Ensure backend is running
  ```bash
  # Terminal 1
  cd backend
  source .venv/bin/activate
  uvicorn app.main:app --reload
  ```

- [ ] Start frontend dev server
  ```bash
  # Terminal 2
  cd frontend
  npm run dev
  ```

- [ ] Create test component `frontend/src/App.tsx`:
  ```typescript
  import { useEffect, useState } from 'react';
  import client from './api/client';

  function App() {
    const [health, setHealth] = useState<any>(null);
    const [db, setDb] = useState<any>(null);

    useEffect(() => {
      // Test health endpoint
      client.get('/health').then(res => setHealth(res.data));

      // Test database endpoint
      client.get('/api/test/db').then(res => setDb(res.data));
    }, []);

    return (
      <div className="min-h-screen bg-gray-100 p-8">
        <h1 className="text-3xl font-bold text-blue-600 mb-6">
          ONLSuggest - Environment Setup ✅
        </h1>

        <div className="bg-white rounded-lg shadow p-6 mb-4">
          <h2 className="text-xl font-semibold mb-2">API Health</h2>
          <pre className="bg-gray-100 p-3 rounded">
            {JSON.stringify(health, null, 2)}
          </pre>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-2">Database</h2>
          <pre className="bg-gray-100 p-3 rounded">
            {JSON.stringify(db, null, 2)}
          </pre>
        </div>
      </div>
    );
  }

  export default App;
  ```

- [ ] Visit http://localhost:5173
- [ ] Verify page shows:
  - API health status
  - Database gemeentes: 8, services: 10

**Acceptance:** Frontend successfully calls backend APIs, displays data

---

### ✅ Task 5.5: Create Week 1 Completion Report
**Estimated Time:** 15 minutes

- [ ] Create `backend/scripts/week1_report.py`
  ```python
  import asyncio
  import sys
  from pathlib import Path

  sys.path.insert(0, str(Path(__file__).parent.parent))

  from sqlalchemy import select, func
  from app.core.database import async_session_maker
  from app.models.gemeente import Gemeente
  from app.models.service import Service
  from app.models.association import GemeenteServiceAssociation
  from app.models.admin_user import AdminUser
  from app.core.redis_client import get_redis

  async def generate_report():
      print("\n" + "="*60)
      print("📊 Week 1 Environment Setup - Completion Report")
      print("="*60 + "\n")

      # Database check
      async with async_session_maker() as db:
          gemeente_count = await db.scalar(select(func.count(Gemeente.id)))
          service_count = await db.scalar(select(func.count(Service.id)))
          assoc_count = await db.scalar(select(func.count(GemeenteServiceAssociation.id)))
          admin_count = await db.scalar(select(func.count(AdminUser.id)))

          print("✅ Database Setup")
          print(f"   - Gemeentes: {gemeente_count}")
          print(f"   - Services: {service_count}")
          print(f"   - Associations: {assoc_count}")
          print(f"   - Admin users: {admin_count}\n")

      # Redis check
      try:
          redis = await get_redis()
          await redis.set("setup_test", "complete")
          value = await redis.get("setup_test")
          print("✅ Redis Connected")
          print(f"   - Status: Working ({value})\n")
      except Exception as e:
          print(f"❌ Redis Error: {e}\n")

      # Dependencies check
      print("✅ Backend Dependencies")
      import fastapi, sqlalchemy, spacy, bcrypt
      print(f"   - FastAPI: {fastapi.__version__}")
      print(f"   - SQLAlchemy: {sqlalchemy.__version__}")
      print(f"   - spaCy: {spacy.__version__}")
      print(f"   - bcrypt: {bcrypt.__version__}\n")

      # NLP model check
      try:
          nlp = spacy.load("nl_core_news_sm")
          print("✅ Dutch NLP Model")
          print(f"   - Model: nl_core_news_sm loaded\n")
      except:
          print("❌ Dutch NLP Model not found\n")

      print("="*60)
      print("🎉 Week 1 Setup Complete - Ready for Epic 1 Development!")
      print("="*60 + "\n")

  if __name__ == "__main__":
      asyncio.run(generate_report())
  ```

- [ ] Run report
  ```bash
  cd backend
  python scripts/week1_report.py
  ```

- [ ] Screenshot output and save to docs/

**Acceptance:** Report shows all green checkmarks ✅

---

## Final Verification Checklist

### Backend ✅
- [ ] Python 3.11+ virtual environment active
- [ ] All dependencies installed (22 packages)
- [ ] Database initialized with 4 tables
- [ ] 8 gemeentes seeded
- [ ] 10 services seeded
- [ ] 80 associations created
- [ ] Admin user created (username: admin)
- [ ] FastAPI server runs without errors
- [ ] Swagger docs accessible at /docs
- [ ] Redis connected and working

### Frontend ✅
- [ ] Node.js 18+ installed
- [ ] Vite + React + TypeScript project created
- [ ] All npm dependencies installed
- [ ] Tailwind CSS configured
- [ ] Directory structure created
- [ ] Dev server runs at localhost:5173
- [ ] Can call backend APIs

### Integration ✅
- [ ] Frontend can fetch from backend
- [ ] CORS configured correctly
- [ ] Both servers can run simultaneously
- [ ] No console errors in browser
- [ ] Week 1 report shows all green

---

## Common Issues & Solutions

### Issue: Python version too old
**Solution:**
```bash
# macOS - Install Python 3.11
brew install python@3.11
python3.11 --version
```

### Issue: Redis connection refused
**Solution:**
```bash
# Check if Redis is running
brew services list
# Restart Redis
brew services restart redis
```

### Issue: Alembic migration fails
**Solution:**
```bash
# Delete database and recreate
rm app.db
alembic upgrade head
python scripts/seed_data.py
```

### Issue: npm install fails
**Solution:**
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Issue: CORS errors in browser
**Solution:**
- Verify backend CORS allows http://localhost:5173
- Check frontend uses correct API URL (http://localhost:8000)
- Restart both servers

---

## Next Steps After Week 1

**Week 2 Start: Epic 1, Story 1.1**
- Implement SearchBox component
- 2-character minimum validation
- 150ms debouncing
- Keyboard navigation

**Reference:**
- Tech Spec: `/docs/tech-spec-epic-1.md`
- Architecture: `/docs/solution-architecture.md`

---

**Checklist Complete! 🎉**

_When all items are checked, you're ready to start Epic 1 development._
