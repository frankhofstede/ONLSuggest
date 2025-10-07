"""
SQLAlchemy declarative base for all models.
All models must inherit from Base for Alembic autogenerate to detect them.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
