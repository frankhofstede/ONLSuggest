"""
Admin API routes
Epic 2: Admin Data Management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List
import secrets

from app.schemas.admin import (
    GemeenteCreate, GemeenteUpdate, GemeenteResponse,
    ServiceCreate, ServiceUpdate, ServiceResponse,
    AssociationCreate, AssociationResponse,
    SettingsResponse, SettingsUpdate,
    StatsResponse
)
from app.models.database import db
from app.core.config import settings as app_settings

router = APIRouter()
security = HTTPBasic()


def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Verify Basic Auth credentials
    Story 2.1: Authentication
    """
    correct_username = secrets.compare_digest(
        credentials.username, app_settings.ADMIN_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, app_settings.ADMIN_PASSWORD
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


# STATISTICS
@router.get("/stats", response_model=StatsResponse)
async def get_stats(username: str = Depends(verify_admin)):
    """
    Get database statistics
    Story 2.6: Dashboard
    """
    try:
        stats = db.get_stats()
        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch stats: {str(e)}"
        )


# GEMEENTES
@router.get("/gemeentes")
async def get_gemeentes(username: str = Depends(verify_admin)):
    """
    Get all gemeentes
    Story 2.2: Gemeente CRUD
    """
    try:
        gemeentes = db.get_all_gemeentes()
        return {"gemeentes": gemeentes}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch gemeentes: {str(e)}"
        )


@router.get("/gemeentes/{gemeente_id}")
async def get_gemeente(gemeente_id: int, username: str = Depends(verify_admin)):
    """Get single gemeente with associations"""
    try:
        gemeente = db.get_gemeente(gemeente_id)
        if not gemeente:
            raise HTTPException(status_code=404, detail="Gemeente not found")

        # Include associated services
        associations = db.get_associations_by_gemeente(gemeente_id)
        service_ids = [a["service_id"] for a in associations]
        services = [db.get_service(sid) for sid in service_ids]
        gemeente["services"] = [s for s in services if s]

        return gemeente
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch gemeente: {str(e)}"
        )


@router.post("/gemeentes", status_code=status.HTTP_201_CREATED)
async def create_gemeente(
    gemeente: GemeenteCreate,
    username: str = Depends(verify_admin)
):
    """Create a new gemeente"""
    try:
        # Check for duplicates
        existing = [g for g in db.get_all_gemeentes() if g["name"].lower() == gemeente.name.lower()]
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gemeente already exists"
            )

        data = {"name": gemeente.name, "metadata": gemeente.metadata or {}}
        result = db.create_gemeente(data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create gemeente: {str(e)}"
        )


@router.put("/gemeentes/{gemeente_id}")
async def update_gemeente(
    gemeente_id: int,
    gemeente: GemeenteUpdate,
    username: str = Depends(verify_admin)
):
    """Update a gemeente"""
    try:
        data = gemeente.dict(exclude_unset=True)
        result = db.update_gemeente(gemeente_id, data)
        if not result:
            raise HTTPException(status_code=404, detail="Gemeente not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update gemeente: {str(e)}"
        )


@router.delete("/gemeentes/{gemeente_id}", status_code=status.HTTP_200_OK)
async def delete_gemeente(gemeente_id: int, username: str = Depends(verify_admin)):
    """Delete a gemeente"""
    try:
        success = db.delete_gemeente(gemeente_id)
        if not success:
            raise HTTPException(status_code=404, detail="Gemeente not found")
        return {"message": "Deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete gemeente: {str(e)}"
        )


# SERVICES
@router.get("/services")
async def get_services(username: str = Depends(verify_admin)):
    """
    Get all services
    Story 2.3: Service CRUD
    """
    try:
        services = db.get_all_services()
        return {"services": services}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch services: {str(e)}"
        )


@router.get("/services/{service_id}")
async def get_service(service_id: int, username: str = Depends(verify_admin)):
    """Get single service with associations"""
    try:
        service = db.get_service(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        # Include associated gemeentes
        associations = db.get_associations_by_service(service_id)
        gemeente_ids = [a["service_id"] for a in associations]
        gemeentes = [db.get_gemeente(gid) for gid in gemeente_ids]
        service["gemeentes"] = [g for g in gemeentes if g]

        return service
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch service: {str(e)}"
        )


@router.post("/services", status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceCreate,
    username: str = Depends(verify_admin)
):
    """Create a new service"""
    try:
        # Check for duplicates
        existing = [s for s in db.get_all_services() if s["name"].lower() == service.name.lower()]
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service already exists"
            )

        data = {
            "name": service.name,
            "description": service.description,
            "category": service.category,
            "keywords": service.keywords or []
        }
        result = db.create_service(data)
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create service: {str(e)}"
        )


@router.put("/services/{service_id}")
async def update_service(
    service_id: int,
    service: ServiceUpdate,
    username: str = Depends(verify_admin)
):
    """Update a service"""
    try:
        data = service.dict(exclude_unset=True)
        result = db.update_service(service_id, data)
        if not result:
            raise HTTPException(status_code=404, detail="Service not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update service: {str(e)}"
        )


@router.delete("/services/{service_id}", status_code=status.HTTP_200_OK)
async def delete_service(service_id: int, username: str = Depends(verify_admin)):
    """Delete a service"""
    try:
        success = db.delete_service(service_id)
        if not success:
            raise HTTPException(status_code=404, detail="Service not found")
        return {"message": "Deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete service: {str(e)}"
        )


# ASSOCIATIONS
@router.get("/associations")
async def get_associations(username: str = Depends(verify_admin)):
    """
    Get all associations
    Story 2.4: Association Management
    """
    try:
        associations = db.get_all_associations()
        return {"associations": associations}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch associations: {str(e)}"
        )


@router.post("/associations", status_code=status.HTTP_201_CREATED)
async def create_association(
    association: AssociationCreate,
    username: str = Depends(verify_admin)
):
    """Create a new association"""
    try:
        data = {"gemeente_id": association.gemeente_id, "service_id": association.service_id}
        result = db.create_association(data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create association: {str(e)}"
        )


@router.delete("/associations/{association_id}", status_code=status.HTTP_200_OK)
async def delete_association(association_id: int, username: str = Depends(verify_admin)):
    """Delete an association"""
    try:
        success = db.delete_association(association_id)
        if not success:
            raise HTTPException(status_code=404, detail="Association not found")
        return {"message": "Deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete association: {str(e)}"
        )


# SETTINGS
@router.get("/settings", response_model=SettingsResponse)
async def get_settings(username: str = Depends(verify_admin)):
    """
    Get application settings
    Story 3.1: Settings Management
    """
    try:
        engine = db.get_setting('suggestion_engine')
        if engine is None:
            return SettingsResponse(suggestion_engine="template")
        return SettingsResponse(suggestion_engine=engine)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch settings: {str(e)}"
        )


@router.put("/settings", response_model=SettingsResponse)
async def update_settings(
    settings_update: SettingsUpdate,
    username: str = Depends(verify_admin)
):
    """Update application settings"""
    try:
        # Validate value
        if settings_update.suggestion_engine not in ['template', 'koop']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid suggestion_engine value. Must be 'template' or 'koop'"
            )

        # Update setting
        success = db.update_setting('suggestion_engine', settings_update.suggestion_engine)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update setting"
            )

        return SettingsResponse(suggestion_engine=settings_update.suggestion_engine)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update settings: {str(e)}"
        )
