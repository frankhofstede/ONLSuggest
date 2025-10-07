"""
Gemeente (Municipality) model.
Represents Dutch municipalities (gemeentes) in the system.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from .base import Base


class Gemeente(Base):
    """Municipality model - stores gemeente data."""

    __tablename__ = "gemeentes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    services = relationship(
        "Service",
        secondary="gemeente_service_associations",
        back_populates="gemeentes",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Gemeente(id={self.id}, name='{self.name}')>"
