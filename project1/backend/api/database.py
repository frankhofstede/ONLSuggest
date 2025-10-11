"""
Database module for ONLSuggest admin interface
Uses Neon Postgres via psycopg2
"""
import os
import psycopg2
import psycopg2.extras
from typing import List, Dict, Optional
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

@contextmanager
def get_connection():
    """Get database connection with automatic cleanup"""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

class PostgresDatabase:
    """Postgres database for ONLSuggest admin"""

    # GEMEENTE CRUD
    def create_gemeente(self, name: str, metadata: Dict = None) -> Dict:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                INSERT INTO gemeentes (name, metadata)
                VALUES (%s, %s)
                RETURNING id, name, metadata, created_at
                """,
                (name, psycopg2.extras.Json(metadata or {}))
            )
            return dict(cur.fetchone())

    def get_gemeente(self, gemeente_id: int) -> Optional[Dict]:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT id, name, metadata, created_at FROM gemeentes WHERE id = %s",
                (gemeente_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_gemeentes(self) -> List[Dict]:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT id, name, metadata, created_at FROM gemeentes ORDER BY name")
            return [dict(row) for row in cur.fetchall()]

    def update_gemeente(self, gemeente_id: int, name: str = None, metadata: Dict = None) -> Optional[Dict]:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Build dynamic update query
            updates = []
            params = []
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if metadata is not None:
                updates.append("metadata = %s")
                params.append(psycopg2.extras.Json(metadata))

            if not updates:
                return self.get_gemeente(gemeente_id)

            params.append(gemeente_id)
            cur.execute(
                f"UPDATE gemeentes SET {', '.join(updates)} WHERE id = %s RETURNING id, name, metadata, created_at",
                params
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def delete_gemeente(self, gemeente_id: int) -> bool:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM gemeentes WHERE id = %s", (gemeente_id,))
            return cur.rowcount > 0

    # SERVICE CRUD
    def create_service(self, name: str, description: str, category: str, keywords: List[str]) -> Dict:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                """
                INSERT INTO services (name, description, category, keywords)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, description, category, keywords, created_at
                """,
                (name, description, category, keywords)
            )
            return dict(cur.fetchone())

    def get_service(self, service_id: int) -> Optional[Dict]:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT id, name, description, category, keywords, created_at FROM services WHERE id = %s",
                (service_id,)
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def get_all_services(self) -> List[Dict]:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("SELECT id, name, description, category, keywords, created_at FROM services ORDER BY category, name")
            return [dict(row) for row in cur.fetchall()]

    def update_service(self, service_id: int, name: str = None, description: str = None,
                      category: str = None, keywords: List[str] = None) -> Optional[Dict]:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Build dynamic update query
            updates = []
            params = []
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if category is not None:
                updates.append("category = %s")
                params.append(category)
            if keywords is not None:
                updates.append("keywords = %s")
                params.append(keywords)

            if not updates:
                return self.get_service(service_id)

            params.append(service_id)
            cur.execute(
                f"UPDATE services SET {', '.join(updates)} WHERE id = %s RETURNING id, name, description, category, keywords, created_at",
                params
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def delete_service(self, service_id: int) -> bool:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM services WHERE id = %s", (service_id,))
            return cur.rowcount > 0

    # ASSOCIATIONS
    def create_association(self, gemeente_id: int, service_id: int) -> Dict:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            # Check if already exists
            cur.execute(
                "SELECT id, gemeente_id, service_id, created_at FROM associations WHERE gemeente_id = %s AND service_id = %s",
                (gemeente_id, service_id)
            )
            existing = cur.fetchone()
            if existing:
                return dict(existing)

            # Create new association
            cur.execute(
                """
                INSERT INTO associations (gemeente_id, service_id)
                VALUES (%s, %s)
                RETURNING id, gemeente_id, service_id, created_at
                """,
                (gemeente_id, service_id)
            )
            return dict(cur.fetchone())

    def get_associations_by_gemeente(self, gemeente_id: int) -> List[Dict]:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT id, gemeente_id, service_id, created_at FROM associations WHERE gemeente_id = %s",
                (gemeente_id,)
            )
            return [dict(row) for row in cur.fetchall()]

    def get_associations_by_service(self, service_id: int) -> List[Dict]:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT id, gemeente_id, service_id, created_at FROM associations WHERE service_id = %s",
                (service_id,)
            )
            return [dict(row) for row in cur.fetchall()]

    def get_all_associations(self) -> List[Dict]:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT id, gemeente_id, service_id, created_at FROM associations"
            )
            return [dict(row) for row in cur.fetchall()]

    def delete_association(self, association_id: int) -> bool:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM associations WHERE id = %s", (association_id,))
            return cur.rowcount > 0

    # STATISTICS
    def get_stats(self) -> Dict:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM gemeentes")
            total_gemeentes = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM services")
            total_services = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM associations")
            total_associations = cur.fetchone()[0]

            return {
                "total_gemeentes": total_gemeentes,
                "total_services": total_services,
                "total_associations": total_associations
            }

    # APP SETTINGS (Epic 3 Story 3.1)
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value by key"""
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(
                "SELECT value FROM app_settings WHERE key = %s",
                (key,)
            )
            row = cur.fetchone()
            return row['value'] if row else None

    def update_setting(self, key: str, value: str) -> bool:
        """Update a setting value by key"""
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE app_settings SET value = %s, updated_at = CURRENT_TIMESTAMP WHERE key = %s",
                (value, key)
            )
            return cur.rowcount > 0

# Global database instance
db = PostgresDatabase()
