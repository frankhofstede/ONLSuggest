"""
Week 1 Environment Setup - Completion Report.
Validates all development environment components are functional.

Usage:
    cd backend && python scripts/week1_report.py
"""
import sys
import asyncio
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.core.database import async_session_maker
from app.core.redis_client import redis_client
from app.models import Gemeente, Service, GemeenteServiceAssociation, AdminUser


async def check_database():
    """Check database connectivity and seeded data."""
    try:
        async with async_session_maker() as session:
            # Query counts
            gemeentes_result = await session.execute(select(func.count()).select_from(Gemeente))
            gemeentes_count = gemeentes_result.scalar()

            services_result = await session.execute(select(func.count()).select_from(Service))
            services_count = services_result.scalar()

            assoc_result = await session.execute(select(func.count()).select_from(GemeenteServiceAssociation))
            assoc_count = assoc_result.scalar()

            admin_result = await session.execute(select(func.count()).select_from(AdminUser))
            admin_count = admin_result.scalar()

            return {
                "status": "ok",
                "gemeentes": gemeentes_count,
                "services": services_count,
                "associations": assoc_count,
                "admin_users": admin_count
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_redis():
    """Check Redis connectivity."""
    try:
        # Test ping
        redis_client.ping()

        # Test set/get
        test_key = "onlsuggest:week1:test"
        redis_client.set(test_key, "working", ex=10)
        value = redis_client.get(test_key)
        redis_client.delete(test_key)

        return {"status": "ok", "test": value}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_dependencies():
    """Check installed Python dependencies."""
    try:
        import fastapi
        import sqlalchemy
        import spacy
        import bcrypt

        return {
            "status": "ok",
            "fastapi": fastapi.__version__,
            "sqlalchemy": sqlalchemy.__version__,
            "spacy": spacy.__version__,
            "bcrypt": bcrypt.__version__
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_nlp_model():
    """Check Dutch NLP model is available."""
    try:
        import spacy
        nlp = spacy.load("nl_core_news_sm")
        return {"status": "ok", "model": "nl_core_news_sm", "loaded": True}
    except Exception as e:
        return {"status": "error", "error": str(e)}


async def main():
    """Run all checks and print report."""
    print("=" * 60)
    print("📊 Week 1 Environment Setup - Completion Report")
    print("=" * 60)
    print()

    # Check database
    print("🔍 Checking Database...")
    db_result = await check_database()
    if db_result["status"] == "ok":
        print("✅ Database Setup")
        print(f"   - Gemeentes: {db_result['gemeentes']}")
        print(f"   - Services: {db_result['services']}")
        print(f"   - Associations: {db_result['associations']}")
        print(f"   - Admin users: {db_result['admin_users']}")
    else:
        print(f"❌ Database Error: {db_result.get('error')}")
    print()

    # Check Redis
    print("🔍 Checking Redis...")
    redis_result = check_redis()
    if redis_result["status"] == "ok":
        print("✅ Redis Connected")
        print(f"   - Status: {redis_result['test']}")
    else:
        print(f"❌ Redis Error: {redis_result.get('error')}")
    print()

    # Check dependencies
    print("🔍 Checking Backend Dependencies...")
    deps_result = check_dependencies()
    if deps_result["status"] == "ok":
        print("✅ Backend Dependencies")
        print(f"   - FastAPI: {deps_result['fastapi']}")
        print(f"   - SQLAlchemy: {deps_result['sqlalchemy']}")
        print(f"   - spaCy: {deps_result['spacy']}")
        print(f"   - bcrypt: {deps_result['bcrypt']}")
    else:
        print(f"❌ Dependencies Error: {deps_result.get('error')}")
    print()

    # Check NLP model
    print("🔍 Checking Dutch NLP Model...")
    nlp_result = check_nlp_model()
    if nlp_result["status"] == "ok":
        print("✅ Dutch NLP Model")
        print(f"   - Model: {nlp_result['model']} loaded")
    else:
        print(f"❌ NLP Model Error: {nlp_result.get('error')}")
    print()

    print("=" * 60)
    all_ok = all([
        db_result["status"] == "ok",
        redis_result["status"] == "ok",
        deps_result["status"] == "ok",
        nlp_result["status"] == "ok"
    ])

    if all_ok:
        print("🎉 Week 1 Setup Complete - Ready for Epic 1 Development!")
    else:
        print("⚠️  Some checks failed - please review errors above")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
