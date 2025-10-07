"""
Create admin user script.
Creates an admin user with bcrypt hashed password.

Usage:
    cd backend && python scripts/create_admin.py

Default credentials:
    Username: admin
    Password: changeme123 (CHANGE IN PRODUCTION!)
"""
import sys
import asyncio
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.config import settings
from app.core.security import SecurityService
from app.core.database import async_session_maker
from app.models.admin_user import AdminUser


async def create_admin():
    """Create admin user if it doesn't exist."""
    async with async_session_maker() as session:
        try:
            # Check if admin user already exists
            result = await session.execute(
                select(AdminUser).where(AdminUser.username == settings.admin_username)
            )
            existing_admin = result.scalar_one_or_none()

            if existing_admin:
                print(f"ℹ️  Admin user '{settings.admin_username}' already exists. Skipping creation.")
                return

            # Hash the password
            password_hash = SecurityService.hash_password(settings.admin_password)

            # Create new admin user
            admin = AdminUser(
                username=settings.admin_username,
                password_hash=password_hash
            )

            session.add(admin)
            await session.commit()

            print("✅ Admin user created successfully!")
            print(f"   Username: {settings.admin_username}")
            print(f"   Password: {settings.admin_password}")
            print("\n⚠️  WARNING: Change the default password in production!")
            print("   Update ADMIN_PASSWORD in .env file")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error creating admin user: {e}")
            raise


def main():
    """Main entry point."""
    print("=" * 60)
    print("ONLSuggest - Admin User Creation")
    print("=" * 60)
    asyncio.run(create_admin())


if __name__ == "__main__":
    main()
