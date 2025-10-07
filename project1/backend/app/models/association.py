"""
GemeenteServiceAssociation model.
Junction table for many-to-many relationship between Gemeentes and Services.
"""
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.sql import func

from .base import Base


class GemeenteServiceAssociation(Base):
    """Association table linking gemeentes to services."""

    __tablename__ = "gemeente_service_associations"

    id = Column(Integer, primary_key=True, index=True)
    gemeente_id = Column(
        Integer,
        ForeignKey("gemeentes.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Unique constraint: a gemeente can only have a service once
    __table_args__ = (
        UniqueConstraint("gemeente_id", "service_id", name="uq_gemeente_service"),
    )

    def __repr__(self):
        return f"<GemeenteServiceAssociation(gemeente_id={self.gemeente_id}, service_id={self.service_id})>"
