"""
Seed database with initial test data.
Creates 8 gemeentes, 10 services, and 80 associations.

Usage:
    cd backend && python scripts/seed_data.py

Data:
    - 8 Dutch gemeentes (Amsterdam, Rotterdam, Utrecht, etc.)
    - 10 common government services with Dutch keywords
    - 80 associations (all gemeentes support all services for POC)
"""
import sys
import asyncio
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from app.core.database import async_session_maker
from app.models import Gemeente, Service, GemeenteServiceAssociation


# 8 Dutch gemeentes with descriptions
GEMEENTES = [
    {"name": "Amsterdam", "description": "Hoofdstad van Nederland"},
    {"name": "Rotterdam", "description": "Havenstad"},
    {"name": "Utrecht", "description": "Centraal in Nederland"},
    {"name": "Den Haag", "description": "Regeringszetel"},
    {"name": "Eindhoven", "description": "Technologiestad in Brabant"},
    {"name": "Groningen", "description": "Stad in het noorden"},
    {"name": "Tilburg", "description": "Stad in Noord-Brabant"},
    {"name": "Almere", "description": "Jonge stad in Flevoland"},
]

# 10 Common Dutch government services with keywords for search
SERVICES = [
    {
        "name": "Parkeervergunning aanvragen",
        "description": "Aanvragen van een bewonersvergunning voor parkeren in uw wijk",
        "keywords": ["parkeren", "bewonersvergunning", "auto", "parkeerplaats", "vergunning"],
        "category": "Verkeer & Vervoer"
    },
    {
        "name": "Paspoort aanvragen",
        "description": "Nieuw paspoort aanvragen of verlengen",
        "keywords": ["paspoort", "identiteitsbewijs", "reisdocument", "ID"],
        "category": "Documenten & Identiteit"
    },
    {
        "name": "Rijbewijs aanvragen",
        "description": "Rijbewijs aanvragen of verlengen",
        "keywords": ["rijbewijs", "rijbewijs verlengen", "autorijbewijs", "motor"],
        "category": "Verkeer & Vervoer"
    },
    {
        "name": "Afvalcontainer aanvragen",
        "description": "Container aanvragen voor GFT, papier of restafval",
        "keywords": ["afval", "container", "gft", "restafval", "papier"],
        "category": "Afval & Milieu"
    },
    {
        "name": "Verhuizing doorgeven",
        "description": "Verhuizing doorgeven aan de gemeente (adreswijziging)",
        "keywords": ["verhuizen", "adreswijziging", "inschrijven", "verhuizing", "BRP"],
        "category": "Wonen & Leven"
    },
    {
        "name": "Bouwvergunning aanvragen",
        "description": "Vergunning aanvragen voor bouwen of verbouwen",
        "keywords": ["bouwen", "verbouwen", "vergunning", "aanbouw", "uitbouw"],
        "category": "Bouwen & Wonen"
    },
    {
        "name": "Huwelijk voltrekken",
        "description": "Trouwen of geregistreerd partnerschap aangaan",
        "keywords": ["trouwen", "huwelijk", "partnerschap", "trouwdag"],
        "category": "Burgerlijke Stand"
    },
    {
        "name": "Kinderopvang toeslag",
        "description": "Toeslag aanvragen voor kinderopvang",
        "keywords": ["kinderopvang", "toeslag", "kinderen", "opvang", "subsidie"],
        "category": "Jeugd & Onderwijs"
    },
    {
        "name": "Uittreksel GBA aanvragen",
        "description": "Uittreksel uit de Gemeentelijke Basisadministratie",
        "keywords": ["gba", "uittreksel", "persoonsgegevens", "verklaring"],
        "category": "Documenten & Identiteit"
    },
    {
        "name": "Kapvergunning boom aanvragen",
        "description": "Vergunning voor het kappen van een boom",
        "keywords": ["boom", "kappen", "vergunning", "groen", "boom kappen"],
        "category": "Groen & Natuur"
    },
]


async def seed_database():
    """Seed database with gemeentes, services, and associations."""
    async with async_session_maker() as session:
        try:
            # Check if data already exists
            result = await session.execute(select(func.count()).select_from(Gemeente))
            gemeente_count = result.scalar()

            if gemeente_count > 0:
                print(f"ℹ️  Database already has {gemeente_count} gemeentes. Skipping seed.")
                print("   Delete existing data if you want to re-seed:")
                print("   docker exec onlsuggest_postgres psql -U onlsuggest -d onlsuggest -c 'TRUNCATE gemeentes, services, gemeente_service_associations CASCADE;'")
                return

            print("Creating gemeentes...")
            # Create gemeentes
            gemeentes = []
            for data in GEMEENTES:
                gemeente = Gemeente(**data)
                session.add(gemeente)
                gemeentes.append(gemeente)

            await session.flush()  # Get IDs
            print(f"✅ Created {len(gemeentes)} gemeentes")

            print("\nCreating services...")
            # Create services
            services = []
            for data in SERVICES:
                service = Service(**data)
                session.add(service)
                services.append(service)

            await session.flush()  # Get IDs
            print(f"✅ Created {len(services)} services")

            print("\nCreating associations...")
            # Create associations (all gemeentes support all services for POC)
            associations = []
            for gemeente in gemeentes:
                for service in services:
                    assoc = GemeenteServiceAssociation(
                        gemeente_id=gemeente.id,
                        service_id=service.id
                    )
                    session.add(assoc)
                    associations.append(assoc)

            await session.commit()
            print(f"✅ Created {len(associations)} associations")

            print("\n" + "=" * 60)
            print("✅ Database seeding completed successfully!")
            print("=" * 60)
            print(f"   Gemeentes: {len(gemeentes)}")
            print(f"   Services: {len(services)}")
            print(f"   Associations: {len(associations)}")
            print(f"   Total records: {len(gemeentes) + len(services) + len(associations)}")

        except Exception as e:
            await session.rollback()
            print(f"❌ Error seeding database: {e}")
            raise


def main():
    """Main entry point."""
    print("=" * 60)
    print("ONLSuggest - Database Seeding")
    print("=" * 60)
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()
