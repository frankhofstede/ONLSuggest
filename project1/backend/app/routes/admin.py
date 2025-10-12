"""
Admin API routes with Basic Authentication
Epic 2: Admin Data Management
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import secrets
import json
from datetime import datetime

from app.core.config import settings
from app.models.database import db

router = APIRouter()
security = HTTPBasic()


def json_serial(obj):
    """JSON serializer for datetime objects"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify Basic Auth credentials"""
    correct_username = secrets.compare_digest(
        credentials.username, settings.ADMIN_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.ADMIN_PASSWORD
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# Request models
class GemeenteCreate(BaseModel):
    name: str
    metadata: Optional[Dict[str, Any]] = None


class ServiceCreate(BaseModel):
    name: str
    description: str
    category: str
    keywords: Optional[list] = None


class AssociationCreate(BaseModel):
    gemeente_id: int
    service_id: int


class SettingUpdate(BaseModel):
    value: str


# GEMEENTE ENDPOINTS
@router.get("/gemeentes")
async def get_gemeentes(username: str = Depends(verify_admin)):
    """Get all gemeentes"""
    try:
        gemeentes = db.get_all_gemeentes()
        return {"gemeentes": json.loads(json.dumps(gemeentes, default=json_serial))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch gemeentes: {str(e)}")


@router.get("/gemeentes/{gemeente_id}")
async def get_gemeente(gemeente_id: int, username: str = Depends(verify_admin)):
    """Get specific gemeente"""
    try:
        gemeente = db.get_gemeente(gemeente_id)
        if not gemeente:
            raise HTTPException(status_code=404, detail="Gemeente not found")
        return json.loads(json.dumps(gemeente, default=json_serial))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gemeentes")
async def create_gemeente(gemeente: GemeenteCreate, username: str = Depends(verify_admin)):
    """Create new gemeente"""
    try:
        result = db.create_gemeente(gemeente.dict())
        return json.loads(json.dumps(result, default=json_serial))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/gemeentes/{gemeente_id}")
async def update_gemeente(
    gemeente_id: int,
    gemeente: GemeenteCreate,
    username: str = Depends(verify_admin)
):
    """Update gemeente"""
    try:
        result = db.update_gemeente(gemeente_id, gemeente.dict())
        if not result:
            raise HTTPException(status_code=404, detail="Gemeente not found")
        return json.loads(json.dumps(result, default=json_serial))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/gemeentes/{gemeente_id}")
async def delete_gemeente(gemeente_id: int, username: str = Depends(verify_admin)):
    """Delete gemeente"""
    try:
        success = db.delete_gemeente(gemeente_id)
        if not success:
            raise HTTPException(status_code=404, detail="Gemeente not found")
        return {"message": "Gemeente deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# SERVICE ENDPOINTS
@router.get("/services")
async def get_services(username: str = Depends(verify_admin)):
    """Get all services"""
    try:
        services = db.get_all_services()
        return {"services": json.loads(json.dumps(services, default=json_serial))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch services: {str(e)}")


@router.get("/services/{service_id}")
async def get_service(service_id: int, username: str = Depends(verify_admin)):
    """Get specific service"""
    try:
        service = db.get_service(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return json.loads(json.dumps(service, default=json_serial))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/services")
async def create_service(service: ServiceCreate, username: str = Depends(verify_admin)):
    """Create new service"""
    try:
        result = db.create_service(service.dict())
        return json.loads(json.dumps(result, default=json_serial))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/services/{service_id}")
async def update_service(
    service_id: int,
    service: ServiceCreate,
    username: str = Depends(verify_admin)
):
    """Update service"""
    try:
        result = db.update_service(service_id, service.dict())
        if not result:
            raise HTTPException(status_code=404, detail="Service not found")
        return json.loads(json.dumps(result, default=json_serial))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/services/{service_id}")
async def delete_service(service_id: int, username: str = Depends(verify_admin)):
    """Delete service"""
    try:
        success = db.delete_service(service_id)
        if not success:
            raise HTTPException(status_code=404, detail="Service not found")
        return {"message": "Service deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ASSOCIATION ENDPOINTS
@router.get("/associations")
async def get_associations(username: str = Depends(verify_admin)):
    """Get all associations"""
    try:
        associations = db.get_all_associations()
        return {"associations": json.loads(json.dumps(associations, default=json_serial))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch associations: {str(e)}")


@router.post("/associations")
async def create_association(association: AssociationCreate, username: str = Depends(verify_admin)):
    """Create new association"""
    try:
        result = db.create_association(association.dict())
        return json.loads(json.dumps(result, default=json_serial))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/associations/{association_id}")
async def delete_association(association_id: int, username: str = Depends(verify_admin)):
    """Delete association"""
    try:
        success = db.delete_association(association_id)
        if not success:
            raise HTTPException(status_code=404, detail="Association not found")
        return {"message": "Association deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# SETTINGS ENDPOINTS
@router.get("/settings/{key}")
async def get_setting(key: str, username: str = Depends(verify_admin)):
    """Get setting value"""
    try:
        value = db.get_setting(key)
        if value is None:
            raise HTTPException(status_code=404, detail="Setting not found")
        return {"key": key, "value": value}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings/{key}")
async def update_setting(
    key: str,
    setting: SettingUpdate,
    username: str = Depends(verify_admin)
):
    """Update setting value"""
    try:
        success = db.update_setting(key, setting.value)
        if not success:
            raise HTTPException(status_code=404, detail="Setting not found")
        return {"message": "Setting updated successfully", "key": key, "value": setting.value}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# STATS ENDPOINT
@router.get("/stats")
async def get_stats(username: str = Depends(verify_admin)):
    """Get database statistics"""
    try:
        stats = db.get_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
