"""
Pydantic schemas for admin API
"""
from typing import Optional, Any, Dict
from pydantic import BaseModel
from datetime import datetime


# Gemeente schemas
class GemeenteCreate(BaseModel):
    """Schema for creating a gemeente"""
    name: str
    metadata: Optional[Dict[str, Any]] = None


class GemeenteUpdate(BaseModel):
    """Schema for updating a gemeente"""
    name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class GemeenteResponse(BaseModel):
    """Schema for gemeente response"""
    id: int
    name: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Service schemas
class ServiceCreate(BaseModel):
    """Schema for creating a service"""
    name: str
    description: str
    category: str
    keywords: Optional[list] = None


class ServiceUpdate(BaseModel):
    """Schema for updating a service"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    keywords: Optional[list] = None


class ServiceResponse(BaseModel):
    """Schema for service response"""
    id: int
    name: str
    description: str
    category: str
    keywords: Optional[list] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Association schemas
class AssociationCreate(BaseModel):
    """Schema for creating an association"""
    gemeente_id: int
    service_id: int


class AssociationResponse(BaseModel):
    """Schema for association response"""
    id: int
    gemeente_id: int
    service_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Settings schemas
class SettingsResponse(BaseModel):
    """Schema for settings response"""
    suggestion_engine: str


class SettingsUpdate(BaseModel):
    """Schema for updating settings"""
    suggestion_engine: str


# Stats schema
class StatsResponse(BaseModel):
    """Schema for statistics response"""
    total_gemeentes: int
    total_services: int
    total_associations: int
