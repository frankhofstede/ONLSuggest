# Tech Spec: Epic 2 - Admin Data Management

**Author:** Winston (Architect)
**Date:** 2025-10-07
**Epic:** Epic 2 - Admin Data Management
**Status:** Draft

---

## Epic Overview

**Epic Goal:** Enable manual curation of gemeentes and services through simple admin interface

**Business Value:** Allows rapid dataset iteration without developer involvement, keeping POC flexible and testable

**Stories Covered:**
- Story 2.1: Admin Authentication (Basic Auth)
- Story 2.2: Gemeente CRUD Operations
- Story 2.3: Service CRUD Operations
- Story 2.4: Gemeente-Service Association Management
- Story 2.5: Data Validation and Duplicate Prevention
- Story 2.6: Basic Admin Dashboard with Data Overview

**Dependencies:** None (can develop in parallel with Epic 1)

**Estimated Effort:** 2-3 weeks

---

## Architecture Context

**From solution-architecture.md:**

**Tech Stack:**
- Backend: FastAPI 0.109.0, Python 3.11+
- Database: PostgreSQL 15+ with SQLAlchemy 2.0.25 (async)
- Auth: bcrypt 4.1.2 for password hashing
- Sessions: Redis 7.2 for token storage
- Frontend: React 18.2.0, TypeScript 5.3.0, Tailwind CSS 3.4.0
- Forms: react-hook-form 7.49.0
- State: TanStack Query 5.17.0

**Security:** Basic authentication with bcrypt password hashing, session tokens stored in Redis

**Architecture Pattern:** Monolith, Monorepo, SPA, REST API

---

## Story-by-Story Technical Breakdown

### Story 2.1: Admin Authentication (Basic Auth)

**Acceptance Criteria:**
- Basic authentication mechanism (username/password)
- Login page with Dutch labels
- Session management (stays logged in)
- Logout functionality
- Password stored securely (hashed)

**Backend Implementation:**

**Models: `backend/app/models/admin_user.py`**

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

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username={self.username})>"
```

**Security Service: `backend/app/core/security.py`**

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

    @staticmethod
    def create_session_data(user_id: int, username: str) -> dict:
        """Create session data dictionary."""
        return {
            "user_id": user_id,
            "username": username,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
```

**Auth Schemas: `backend/app/schemas/auth.py`**

```python
from pydantic import BaseModel, Field
from datetime import datetime

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)

class LoginResponse(BaseModel):
    token: str
    username: str
    expires_at: datetime

class LogoutRequest(BaseModel):
    token: str
```

**Auth Router: `backend/app/routers/admin.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import json

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/auth", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """
    Authenticate admin user and create session.

    Steps:
    1. Lookup user by username
    2. Verify password with bcrypt
    3. Generate session token
    4. Store session in Redis (24-hour expiry)
    5. Update last_login timestamp
    6. Return token and expiration
    """
    # Lookup user
    result = await db.execute(
        select(AdminUser).where(AdminUser.username == body.username)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ongeldige gebruikersnaam of wachtwoord"
        )

    # Verify password
    if not SecurityService.verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ongeldige gebruikersnaam of wachtwoord"
        )

    # Generate session token
    token = SecurityService.generate_session_token()

    # Create session data
    session_data = SecurityService.create_session_data(user.id, user.username)

    # Store in Redis (24-hour expiry)
    await redis.setex(
        f"session:{token}",
        86400,  # 24 hours in seconds
        json.dumps(session_data)
    )

    # Update last_login
    user.last_login = datetime.utcnow()
    await db.commit()

    return LoginResponse(
        token=token,
        username=user.username,
        expires_at=datetime.fromisoformat(session_data["expires_at"])
    )

@router.post("/logout")
async def logout(
    body: LogoutRequest,
    redis: Redis = Depends(get_redis)
):
    """
    Logout admin user by deleting session.
    """
    await redis.delete(f"session:{body.token}")

    return {"message": "Uitgelogd"}
```

**Auth Middleware: `backend/app/middleware/auth.py`**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import json

security = HTTPBearer()

async def verify_admin_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    redis: Redis = Depends(get_redis)
) -> dict:
    """
    Verify admin session token.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        Session data (user_id, username)

    Raises:
        HTTPException: 401 if session invalid or expired
    """
    token = credentials.credentials

    # Lookup session in Redis
    session_json = await redis.get(f"session:{token}")

    if not session_json:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessie verlopen of ongeldig. Log opnieuw in."
        )

    session_data = json.loads(session_json)

    # Check expiration
    expires_at = datetime.fromisoformat(session_data["expires_at"])
    if datetime.utcnow() > expires_at:
        await redis.delete(f"session:{token}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessie verlopen. Log opnieuw in."
        )

    return session_data

# Use as dependency in protected routes
@router.get("/protected")
async def protected_route(session: dict = Depends(verify_admin_session)):
    return {"message": f"Hello, {session['username']}"}
```

**Frontend Implementation:**

**Page: `frontend/src/pages/admin/Login.tsx`**

```typescript
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(username, password);
      navigate('/admin/dashboard');
    } catch (err: any) {
      if (err.response?.status === 401) {
        setError('Ongeldige gebruikersnaam of wachtwoord');
      } else {
        setError('Er is iets misgegaan. Probeer het opnieuw.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold mb-6 text-gray-800">
          Admin Login
        </h1>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 p-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-medium mb-2">
              Gebruikersnaam
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              minLength={3}
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-700 text-sm font-medium mb-2">
              Wachtwoord
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
              minLength={8}
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
          >
            {isLoading ? 'Inloggen...' : 'Inloggen'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
```

**Auth Context: `frontend/src/contexts/AuthContext.tsx`**

```typescript
import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

interface AuthContextType {
  isAuthenticated: boolean;
  username: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    // Check if token exists in localStorage
    const token = localStorage.getItem('admin_token');
    const storedUsername = localStorage.getItem('admin_username');

    if (token && storedUsername) {
      setIsAuthenticated(true);
      setUsername(storedUsername);

      // Set axios default Authorization header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, []);

  const login = async (username: string, password: string) => {
    const response = await axios.post('/api/admin/auth', { username, password });

    const { token, username: user, expires_at } = response.data;

    // Store token and username
    localStorage.setItem('admin_token', token);
    localStorage.setItem('admin_username', user);

    // Set axios default header
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

    setIsAuthenticated(true);
    setUsername(user);
  };

  const logout = async () => {
    const token = localStorage.getItem('admin_token');

    if (token) {
      try {
        await axios.post('/api/admin/logout', { token });
      } catch (err) {
        console.error('Logout error:', err);
      }
    }

    // Clear local storage
    localStorage.removeItem('admin_token');
    localStorage.removeItem('admin_username');

    // Clear axios header
    delete axios.defaults.headers.common['Authorization'];

    setIsAuthenticated(false);
    setUsername(null);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, username, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

**Dependencies:**
- bcrypt 4.1.2
- Redis 7.2
- react-hook-form 7.49.0

**Testing:**
- Unit test: Hash password → verify password
- Unit test: Generate session token → verify uniqueness
- Integration test: POST /api/admin/auth → verify session created in Redis
- E2E test: Login → verify redirect to dashboard

---

### Story 2.2: Gemeente CRUD Operations

**Acceptance Criteria:**
- List view shows all gemeentes
- Create form with required fields (name, optional metadata)
- Edit form pre-populates existing data
- Delete with confirmation prompt
- Validation prevents empty names
- Success/error feedback in Dutch

**Backend Implementation:**

**Schemas: `backend/app/schemas/gemeente.py`**

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class GemeenteBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Naam mag niet leeg zijn")
        return v.strip()

class GemeenteCreate(GemeenteBase):
    pass

class GemeenteUpdate(GemeenteBase):
    pass

class GemeenteResponse(GemeenteBase):
    id: int
    service_count: int  # Number of associated services
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GemeenteListResponse(BaseModel):
    gemeentes: list[GemeenteResponse]
    total: int
```

**Router: `backend/app/routers/admin.py` (addition)**

```python
@router.get("/gemeentes", response_model=GemeenteListResponse)
async def list_gemeentes(
    db: AsyncSession = Depends(get_db),
    session: dict = Depends(verify_admin_session)
):
    """List all gemeentes with service count."""
    result = await db.execute(
        select(
            Gemeente,
            func.count(Association.service_id).label('service_count')
        )
        .outerjoin(Association)
        .group_by(Gemeente.id)
        .order_by(Gemeente.name)
    )

    gemeentes = []
    for gemeente, service_count in result.all():
        gemeentes.append(
            GemeenteResponse(
                **gemeente.__dict__,
                service_count=service_count
            )
        )

    return GemeenteListResponse(
        gemeentes=gemeentes,
        total=len(gemeentes)
    )

@router.post("/gemeentes", response_model=GemeenteResponse, status_code=201)
async def create_gemeente(
    body: GemeenteCreate,
    db: AsyncSession = Depends(get_db),
    session: dict = Depends(verify_admin_session)
):
    """Create new gemeente."""
    # Check for duplicate
    existing = await db.execute(
        select(Gemeente).where(
            func.lower(Gemeente.name) == body.name.lower()
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Gemeente '{body.name}' bestaat al"
        )

    # Create gemeente
    gemeente = Gemeente(**body.dict())
    db.add(gemeente)
    await db.commit()
    await db.refresh(gemeente)

    # Clear cache (invalidate suggestion cache)
    await invalidate_suggestion_cache(redis)

    return GemeenteResponse(
        **gemeente.__dict__,
        service_count=0
    )

@router.put("/gemeentes/{id}", response_model=GemeenteResponse)
async def update_gemeente(
    id: int,
    body: GemeenteUpdate,
    db: AsyncSession = Depends(get_db),
    session: dict = Depends(verify_admin_session)
):
    """Update existing gemeente."""
    result = await db.execute(
        select(Gemeente).where(Gemeente.id == id)
    )
    gemeente = result.scalar_one_or_none()

    if not gemeente:
        raise HTTPException(status_code=404, detail="Gemeente niet gevonden")

    # Check for duplicate name (excluding current gemeente)
    duplicate = await db.execute(
        select(Gemeente).where(
            func.lower(Gemeente.name) == body.name.lower(),
            Gemeente.id != id
        )
    )
    if duplicate.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail=f"Gemeente '{body.name}' bestaat al"
        )

    # Update fields
    gemeente.name = body.name
    gemeente.description = body.description
    gemeente.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(gemeente)

    # Clear cache
    await invalidate_suggestion_cache(redis)

    # Get service count
    service_count = await db.scalar(
        select(func.count(Association.service_id))
        .where(Association.gemeente_id == id)
    )

    return GemeenteResponse(
        **gemeente.__dict__,
        service_count=service_count or 0
    )

@router.delete("/gemeentes/{id}", status_code=204)
async def delete_gemeente(
    id: int,
    db: AsyncSession = Depends(get_db),
    session: dict = Depends(verify_admin_session)
):
    """Delete gemeente (CASCADE deletes associations)."""
    result = await db.execute(
        select(Gemeente).where(Gemeente.id == id)
    )
    gemeente = result.scalar_one_or_none()

    if not gemeente:
        raise HTTPException(status_code=404, detail="Gemeente niet gevonden")

    await db.delete(gemeente)
    await db.commit()

    # Clear cache
    await invalidate_suggestion_cache(redis)

    return None
```

**Frontend Implementation:**

**Page: `frontend/src/pages/admin/Gemeentes.tsx`**

```typescript
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import AdminTable from '../../components/admin/AdminTable';
import AdminForm from '../../components/admin/AdminForm';
import Modal from '../../components/common/Modal';
import { getGemeentes, createGemeente, updateGemeente, deleteGemeente } from '../../api/admin';

const Gemeentes = () => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingGemeente, setEditingGemeente] = useState<any>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  const queryClient = useQueryClient();

  // Fetch gemeentes
  const { data, isLoading, error } = useQuery({
    queryKey: ['gemeentes'],
    queryFn: getGemeentes
  });

  // Create mutation
  const createMutation = useMutation({
    mutationFn: createGemeente,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gemeentes'] });
      setIsFormOpen(false);
    }
  });

  // Update mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, data }: any) => updateGemeente(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gemeentes'] });
      setEditingGemeente(null);
    }
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: deleteGemeente,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['gemeentes'] });
      setDeleteConfirm(null);
    }
  });

  const handleCreate = (formData: any) => {
    createMutation.mutate(formData);
  };

  const handleUpdate = (formData: any) => {
    updateMutation.mutate({ id: editingGemeente.id, data: formData });
  };

  const handleDelete = (id: number) => {
    deleteMutation.mutate(id);
  };

  const columns = [
    { key: 'name', label: 'Naam' },
    { key: 'description', label: 'Beschrijving' },
    { key: 'service_count', label: 'Diensten' }
  ];

  const fields = [
    {
      name: 'name',
      label: 'Naam',
      type: 'text',
      required: true,
      minLength: 2,
      maxLength: 100
    },
    {
      name: 'description',
      label: 'Beschrijving',
      type: 'textarea',
      required: false
    }
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Gemeentes</h1>
        <button
          onClick={() => setIsFormOpen(true)}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Nieuwe Gemeente
        </button>
      </div>

      {isLoading && <p>Laden...</p>}
      {error && <p className="text-red-600">Fout bij laden van gemeentes</p>}

      {data && (
        <AdminTable
          columns={columns}
          data={data.gemeentes}
          onEdit={(gemeente) => setEditingGemeente(gemeente)}
          onDelete={(gemeente) => setDeleteConfirm(gemeente.id)}
        />
      )}

      {/* Create Modal */}
      {isFormOpen && (
        <Modal onClose={() => setIsFormOpen(false)} title="Nieuwe Gemeente">
          <AdminForm
            fields={fields}
            onSubmit={handleCreate}
            onCancel={() => setIsFormOpen(false)}
            error={createMutation.error?.response?.data?.detail}
          />
        </Modal>
      )}

      {/* Edit Modal */}
      {editingGemeente && (
        <Modal onClose={() => setEditingGemeente(null)} title="Gemeente Bewerken">
          <AdminForm
            fields={fields}
            initialData={editingGemeente}
            onSubmit={handleUpdate}
            onCancel={() => setEditingGemeente(null)}
            error={updateMutation.error?.response?.data?.detail}
          />
        </Modal>
      )}

      {/* Delete Confirmation */}
      {deleteConfirm && (
        <Modal onClose={() => setDeleteConfirm(null)} title="Gemeente Verwijderen">
          <p className="mb-4">
            Weet je zeker dat je deze gemeente wilt verwijderen? Alle koppelingen met diensten worden ook verwijderd.
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => handleDelete(deleteConfirm)}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
              Verwijderen
            </button>
            <button
              onClick={() => setDeleteConfirm(null)}
              className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
            >
              Annuleren
            </button>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Gemeentes;
```

**Reusable Components:**

**`frontend/src/components/admin/AdminTable.tsx`**

```typescript
interface AdminTableProps {
  columns: { key: string; label: string }[];
  data: any[];
  onEdit: (item: any) => void;
  onDelete: (item: any) => void;
}

const AdminTable: React.FC<AdminTableProps> = ({ columns, data, onEdit, onDelete }) => {
  return (
    <table className="w-full bg-white shadow rounded">
      <thead className="bg-gray-100">
        <tr>
          {columns.map((col) => (
            <th key={col.key} className="p-3 text-left">{col.label}</th>
          ))}
          <th className="p-3 text-right">Acties</th>
        </tr>
      </thead>
      <tbody>
        {data.map((item) => (
          <tr key={item.id} className="border-t">
            {columns.map((col) => (
              <td key={col.key} className="p-3">{item[col.key] || '-'}</td>
            ))}
            <td className="p-3 text-right">
              <button
                onClick={() => onEdit(item)}
                className="text-blue-600 hover:underline mr-3"
              >
                Bewerken
              </button>
              <button
                onClick={() => onDelete(item)}
                className="text-red-600 hover:underline"
              >
                Verwijderen
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default AdminTable;
```

**`frontend/src/components/admin/AdminForm.tsx`**

```typescript
import { useForm } from 'react-hook-form';

interface Field {
  name: string;
  label: string;
  type: 'text' | 'textarea' | 'select';
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  options?: { value: string; label: string }[];
}

interface AdminFormProps {
  fields: Field[];
  initialData?: any;
  onSubmit: (data: any) => void;
  onCancel: () => void;
  error?: string;
}

const AdminForm: React.FC<AdminFormProps> = ({
  fields,
  initialData,
  onSubmit,
  onCancel,
  error
}) => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: initialData
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 p-3 rounded mb-4">
          {error}
        </div>
      )}

      {fields.map((field) => (
        <div key={field.name} className="mb-4">
          <label className="block text-gray-700 font-medium mb-2">
            {field.label}
            {field.required && <span className="text-red-600">*</span>}
          </label>

          {field.type === 'textarea' ? (
            <textarea
              {...register(field.name, {
                required: field.required ? `${field.label} is verplicht` : false,
                minLength: field.minLength,
                maxLength: field.maxLength
              })}
              className="w-full px-3 py-2 border rounded"
              rows={4}
            />
          ) : (
            <input
              type={field.type}
              {...register(field.name, {
                required: field.required ? `${field.label} is verplicht` : false,
                minLength: field.minLength,
                maxLength: field.maxLength
              })}
              className="w-full px-3 py-2 border rounded"
            />
          )}

          {errors[field.name] && (
            <p className="text-red-600 text-sm mt-1">
              {errors[field.name]?.message as string}
            </p>
          )}
        </div>
      ))}

      <div className="flex gap-2">
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Opslaan
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="bg-gray-300 px-4 py-2 rounded hover:bg-gray-400"
        >
          Annuleren
        </button>
      </div>
    </form>
  );
};

export default AdminForm;
```

**Dependencies:**
- react-hook-form 7.49.0
- @tanstack/react-query 5.17.0

**Testing:**
- Unit test: Create gemeente → verify duplicate check
- Integration test: CRUD operations → verify database state
- E2E test: Create, edit, delete gemeente via UI

---

### Story 2.3: Service CRUD Operations

**Implementation:** Similar to Story 2.2, with these differences:

**Schemas: `backend/app/schemas/service.py`**

```python
class ServiceBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10)
    keywords: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=50)

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    pass

class ServiceResponse(ServiceBase):
    id: int
    gemeente_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

**Router endpoints:**
- GET /api/admin/services
- POST /api/admin/services
- PUT /api/admin/services/{id}
- DELETE /api/admin/services/{id}

**Frontend:** Reuse AdminTable and AdminForm components with service-specific fields.

---

### Story 2.4: Gemeente-Service Association Management

**Acceptance Criteria:**
- Interface to associate multiple services with a gemeente
- Interface to associate multiple gemeentes with a service
- View existing associations
- Remove associations
- Prevent duplicate associations

**Backend Implementation:**

**Schemas: `backend/app/schemas/association.py`**

```python
class AssociationCreate(BaseModel):
    gemeente_id: int
    service_id: int

class AssociationResponse(BaseModel):
    id: int
    gemeente_id: int
    gemeente_name: str
    service_id: int
    service_name: str
    created_at: datetime

    class Config:
        from_attributes = True

class AssociationListResponse(BaseModel):
    associations: list[AssociationResponse]
    total: int
```

**Router: `backend/app/routers/admin.py` (addition)**

```python
@router.get("/associations", response_model=AssociationListResponse)
async def list_associations(
    db: AsyncSession = Depends(get_db),
    session: dict = Depends(verify_admin_session)
):
    """List all gemeente-service associations."""
    result = await db.execute(
        select(Association, Gemeente.name, Service.name)
        .join(Gemeente, Association.gemeente_id == Gemeente.id)
        .join(Service, Association.service_id == Service.id)
        .order_by(Gemeente.name, Service.name)
    )

    associations = []
    for assoc, gemeente_name, service_name in result.all():
        associations.append(
            AssociationResponse(
                **assoc.__dict__,
                gemeente_name=gemeente_name,
                service_name=service_name
            )
        )

    return AssociationListResponse(
        associations=associations,
        total=len(associations)
    )

@router.post("/associations", response_model=AssociationResponse, status_code=201)
async def create_association(
    body: AssociationCreate,
    db: AsyncSession = Depends(get_db),
    session: dict = Depends(verify_admin_session)
):
    """Create new gemeente-service association."""
    # Check if association already exists
    existing = await db.execute(
        select(Association).where(
            Association.gemeente_id == body.gemeente_id,
            Association.service_id == body.service_id
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Deze koppeling bestaat al"
        )

    # Verify gemeente and service exist
    gemeente = await db.get(Gemeente, body.gemeente_id)
    service = await db.get(Service, body.service_id)

    if not gemeente:
        raise HTTPException(status_code=404, detail="Gemeente niet gevonden")
    if not service:
        raise HTTPException(status_code=404, detail="Dienst niet gevonden")

    # Create association
    assoc = Association(**body.dict())
    db.add(assoc)
    await db.commit()
    await db.refresh(assoc)

    # Clear cache
    await invalidate_suggestion_cache(redis)

    return AssociationResponse(
        **assoc.__dict__,
        gemeente_name=gemeente.name,
        service_name=service.name
    )

@router.delete("/associations/{id}", status_code=204)
async def delete_association(
    id: int,
    db: AsyncSession = Depends(get_db),
    session: dict = Depends(verify_admin_session)
):
    """Delete association."""
    assoc = await db.get(Association, id)

    if not assoc:
        raise HTTPException(status_code=404, detail="Koppeling niet gevonden")

    await db.delete(assoc)
    await db.commit()

    # Clear cache
    await invalidate_suggestion_cache(redis)

    return None
```

**Frontend Implementation:**

**Component: `frontend/src/components/admin/AssociationManager.tsx`**

```typescript
const AssociationManager = () => {
  const [selectedGemeente, setSelectedGemeente] = useState<number | null>(null);
  const [selectedService, setSelectedService] = useState<number | null>(null);

  const { data: associations } = useQuery({
    queryKey: ['associations'],
    queryFn: getAssociations
  });

  const { data: gemeentes } = useQuery({
    queryKey: ['gemeentes'],
    queryFn: getGemeentes
  });

  const { data: services } = useQuery({
    queryKey: ['services'],
    queryFn: getServices
  });

  const createMutation = useMutation({
    mutationFn: createAssociation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['associations'] });
      setSelectedGemeente(null);
      setSelectedService(null);
    }
  });

  const deleteMutation = useMutation({
    mutationFn: deleteAssociation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['associations'] });
    }
  });

  const handleCreate = () => {
    if (selectedGemeente && selectedService) {
      createMutation.mutate({
        gemeente_id: selectedGemeente,
        service_id: selectedService
      });
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Koppelingen Beheren</h1>

      {/* Create Association */}
      <div className="bg-white p-4 rounded shadow mb-6">
        <h2 className="font-medium mb-4">Nieuwe Koppeling</h2>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block mb-2">Gemeente</label>
            <select
              value={selectedGemeente || ''}
              onChange={(e) => setSelectedGemeente(Number(e.target.value))}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">Selecteer gemeente</option>
              {gemeentes?.gemeentes.map((g: any) => (
                <option key={g.id} value={g.id}>{g.name}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block mb-2">Dienst</label>
            <select
              value={selectedService || ''}
              onChange={(e) => setSelectedService(Number(e.target.value))}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">Selecteer dienst</option>
              {services?.services.map((s: any) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleCreate}
          disabled={!selectedGemeente || !selectedService}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          Koppeling Toevoegen
        </button>

        {createMutation.error && (
          <p className="text-red-600 mt-2">
            {createMutation.error.response?.data?.detail}
          </p>
        )}
      </div>

      {/* Association List */}
      <div className="bg-white p-4 rounded shadow">
        <h2 className="font-medium mb-4">Bestaande Koppelingen</h2>

        <table className="w-full">
          <thead className="bg-gray-100">
            <tr>
              <th className="p-3 text-left">Gemeente</th>
              <th className="p-3 text-left">Dienst</th>
              <th className="p-3 text-right">Acties</th>
            </tr>
          </thead>
          <tbody>
            {associations?.associations.map((assoc: any) => (
              <tr key={assoc.id} className="border-t">
                <td className="p-3">{assoc.gemeente_name}</td>
                <td className="p-3">{assoc.service_name}</td>
                <td className="p-3 text-right">
                  <button
                    onClick={() => deleteMutation.mutate(assoc.id)}
                    className="text-red-600 hover:underline"
                  >
                    Verwijderen
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AssociationManager;
```

**Testing:**
- Unit test: Create association → verify duplicate check
- Integration test: Delete association → verify cascade behavior
- E2E test: Create and delete associations via UI

---

### Story 2.5: Data Validation and Duplicate Prevention

**Acceptance Criteria:**
- Cannot create duplicate gemeente names
- Cannot create duplicate service names
- Required fields enforced
- Character limits enforced
- Clear validation error messages in Dutch

**Implementation:** Already covered in Stories 2.2, 2.3, 2.4 with:

**Backend Validation (Pydantic):**
```python
class GemeenteCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Naam mag niet leeg zijn")
        return v.strip()
```

**Database Constraint:**
```sql
CREATE UNIQUE INDEX idx_gemeentes_name_unique
ON gemeentes(LOWER(name));  -- Case-insensitive unique
```

**Duplicate Check Logic:**
```python
existing = await db.execute(
    select(Gemeente).where(
        func.lower(Gemeente.name) == body.name.lower()
    )
)
if existing.scalar_one_or_none():
    raise HTTPException(
        status_code=409,
        detail=f"Gemeente '{body.name}' bestaat al"
    )
```

**Frontend Validation (react-hook-form):**
```typescript
{...register('name', {
  required: 'Naam is verplicht',
  minLength: { value: 2, message: 'Minimaal 2 tekens' },
  maxLength: { value: 100, message: 'Maximaal 100 tekens' }
})}
```

---

### Story 2.6: Basic Admin Dashboard with Data Overview

**Acceptance Criteria:**
- Shows count of gemeentes
- Shows count of services
- Shows count of associations
- Shows recent activity (last 10 changes)
- Link to each CRUD interface

**Backend Implementation:**

**Router: `backend/app/routers/admin.py` (addition)**

```python
@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    session: dict = Depends(verify_admin_session)
):
    """Get dashboard statistics."""
    gemeente_count = await db.scalar(select(func.count(Gemeente.id)))
    service_count = await db.scalar(select(func.count(Service.id)))
    association_count = await db.scalar(select(func.count(Association.id)))

    # Recent activity (last 10 changes)
    # Note: For POC, we'll use created_at timestamps
    recent_gemeentes = await db.execute(
        select(Gemeente.name, Gemeente.created_at)
        .order_by(Gemeente.created_at.desc())
        .limit(5)
    )
    recent_services = await db.execute(
        select(Service.name, Service.created_at)
        .order_by(Service.created_at.desc())
        .limit(5)
    )

    activity = []
    for name, created_at in recent_gemeentes.all():
        activity.append({
            "type": "gemeente",
            "name": name,
            "action": "toegevoegd",
            "timestamp": created_at
        })
    for name, created_at in recent_services.all():
        activity.append({
            "type": "dienst",
            "name": name,
            "action": "toegevoegd",
            "timestamp": created_at
        })

    # Sort by timestamp
    activity.sort(key=lambda x: x["timestamp"], reverse=True)

    return {
        "gemeente_count": gemeente_count,
        "service_count": service_count,
        "association_count": association_count,
        "recent_activity": activity[:10]
    }
```

**Frontend Implementation:**

**Page: `frontend/src/pages/admin/Dashboard.tsx`**

```typescript
const Dashboard = () => {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: getAdminStats
  });

  if (isLoading) return <p>Laden...</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-gray-600 text-sm mb-2">Gemeentes</h3>
          <p className="text-3xl font-bold text-blue-600">
            {data?.gemeente_count}
          </p>
          <Link to="/admin/gemeentes" className="text-blue-600 text-sm hover:underline">
            Beheren →
          </Link>
        </div>

        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-gray-600 text-sm mb-2">Diensten</h3>
          <p className="text-3xl font-bold text-green-600">
            {data?.service_count}
          </p>
          <Link to="/admin/services" className="text-green-600 text-sm hover:underline">
            Beheren →
          </Link>
        </div>

        <div className="bg-white p-6 rounded shadow">
          <h3 className="text-gray-600 text-sm mb-2">Koppelingen</h3>
          <p className="text-3xl font-bold text-purple-600">
            {data?.association_count}
          </p>
          <Link to="/admin/associations" className="text-purple-600 text-sm hover:underline">
            Beheren →
          </Link>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white p-6 rounded shadow">
        <h2 className="font-medium mb-4">Recente Wijzigingen</h2>

        {data?.recent_activity.length === 0 ? (
          <p className="text-gray-500">Nog geen wijzigingen</p>
        ) : (
          <ul className="space-y-2">
            {data?.recent_activity.map((item: any, index: number) => (
              <li key={index} className="flex justify-between items-center py-2 border-b">
                <span>
                  <span className="font-medium">{item.name}</span>
                  {' '}({item.type}) {item.action}
                </span>
                <span className="text-gray-500 text-sm">
                  {new Date(item.timestamp).toLocaleString('nl-NL')}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
```

**Testing:**
- Integration test: Verify stats count accuracy
- E2E test: Navigate from dashboard to CRUD pages

---

## Cache Invalidation Strategy

**Problem:** When admin creates/updates/deletes data, suggestion cache must be cleared.

**Solution: `backend/app/core/cache.py`**

```python
async def invalidate_suggestion_cache(redis: Redis):
    """
    Clear all suggestion cache entries.

    Cache keys follow pattern: suggestion:{hash}
    """
    # Scan for all suggestion keys
    keys = []
    async for key in redis.scan_iter(match="suggestion:*"):
        keys.append(key)

    # Delete all keys
    if keys:
        await redis.delete(*keys)

    logger.info(f"Invalidated {len(keys)} suggestion cache entries")
```

**Alternative (simpler):** Use short TTL (5 minutes) instead of manual invalidation.

---

## Data Model

**Tables for Epic 2:**

```sql
-- Admin users
CREATE TABLE admin_users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL
);

-- Gemeentes (full CRUD)
CREATE TABLE gemeentes (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Services (full CRUD)
CREATE TABLE services (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    keywords TEXT NULL,
    category VARCHAR(50) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Associations (full CRUD)
CREATE TABLE gemeente_service_associations (
    id INTEGER PRIMARY KEY,
    gemeente_id INTEGER NOT NULL REFERENCES gemeentes(id) ON DELETE CASCADE,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(gemeente_id, service_id)
);
```

---

## Testing Strategy

**Unit Tests:**
- Password hashing/verification
- Session token generation
- Validation logic (duplicates, required fields)

**Integration Tests:**
- Admin auth flow (login → session → logout)
- CRUD operations (create → read → update → delete)
- Association management
- Cache invalidation

**E2E Tests:**
- Login → Dashboard → Create Gemeente → Logout
- Full CRUD workflow via UI

---

## Deployment Notes

**Environment Variables:**

```bash
# Admin credentials (initial setup)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changeme123  # Will be hashed on first run
```

**Create Initial Admin User:**

```python
# backend/scripts/create_admin.py
import asyncio
from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.core.security import SecurityService

async def create_admin():
    db = next(get_db())

    # Check if admin exists
    existing = await db.execute(
        select(AdminUser).where(AdminUser.username == "admin")
    )
    if existing.scalar_one_or_none():
        print("Admin user already exists")
        return

    # Create admin
    admin = AdminUser(
        username="admin",
        password_hash=SecurityService.hash_password("changeme123")
    )
    db.add(admin)
    await db.commit()

    print("Admin user created: admin / changeme123")

if __name__ == "__main__":
    asyncio.run(create_admin())
```

---

## Success Criteria

**Definition of Done for Epic 2:**

- ✅ All 6 stories completed and tested
- ✅ Admin can login and logout
- ✅ Admin can CRUD gemeentes, services, associations
- ✅ Duplicate prevention works
- ✅ Dashboard shows accurate stats
- ✅ All forms validate properly
- ✅ Error messages in Dutch

---

## Open Questions / Risks

**Risks:**

1. **Session expiration UX:** If session expires mid-edit, user loses work. Mitigation: Show warning 5 minutes before expiry.

2. **Concurrent edits:** Two admins editing same record. Mitigation: For POC, last-write-wins. Future: optimistic locking.

**Open Questions:**

1. Should we track full audit log (who changed what when)? → Not for POC, add later if needed.

2. Should we support bulk import (CSV upload)? → Not for POC, manual entry only.

---

## Next Steps

**After completing Epic 2:**

1. Integrate with Epic 1
2. End-to-end testing (suggestions + admin)
3. Deploy to Render

**Immediate action:**

- Implement Story 2.1 (Auth)
- Create initial admin user
- Implement reusable AdminTable/AdminForm components

---

**End of Tech Spec: Epic 2 - Admin Data Management**
