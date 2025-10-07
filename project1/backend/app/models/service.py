"""
Service model.
Represents government services (e.g., parkeervergunning, paspoort) in the system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base


class Service(Base):
    """Service model - stores government service data."""

    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=False)
    keywords = Column(ARRAY(String), nullable=True)  # For fuzzy matching
    category = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    gemeentes = relationship(
        "Gemeente",
        secondary="gemeente_service_associations",
        back_populates="services",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Service(id={self.id}, name='{self.name}', category='{self.category}')>"
