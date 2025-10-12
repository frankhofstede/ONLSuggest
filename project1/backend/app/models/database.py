"""
Database operations for ONLSuggest
Uses psycopg2 for PostgreSQL (Neon)
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from app.core.config import settings


@contextmanager
def get_connection():
    """Get database connection with automatic cleanup"""
    conn = psycopg2.connect(settings.DATABASE_URL)
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


class Database:
    """Database connection and operations handler"""

    # GEMEENTE CRUD
    def get_all_gemeentes(self) -> List[Dict[str, Any]]:
        """Get all gemeentes from database"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM gemeentes ORDER BY name")
                return [dict(row) for row in cur.fetchall()]

    def get_gemeente(self, gemeente_id: int) -> Optional[Dict[str, Any]]:
        """Get single gemeente by ID"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, name, metadata, created_at FROM gemeentes WHERE id = %s",
                    (gemeente_id,)
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def create_gemeente(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new gemeente"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO gemeentes (name, metadata)
                    VALUES (%(name)s, %(metadata)s)
                    RETURNING *
                    """,
                    data
                )
                return dict(cur.fetchone())

    def update_gemeente(self, gemeente_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a gemeente"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build update query dynamically
                fields = []
                values = {}
                for key, value in data.items():
                    if key not in ['id', 'created_at']:
                        fields.append(f"{key} = %({key})s")
                        values[key] = value

                if not fields:
                    return self.get_gemeente(gemeente_id)

                values['id'] = gemeente_id
                query = f"UPDATE gemeentes SET {', '.join(fields)} WHERE id = %(id)s RETURNING *"

                cur.execute(query, values)
                row = cur.fetchone()
                return dict(row) if row else None

    def delete_gemeente(self, gemeente_id: int) -> bool:
        """Delete a gemeente"""
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Delete associated associations first
                cur.execute("DELETE FROM associations WHERE gemeente_id = %s", (gemeente_id,))
                # Delete gemeente
                cur.execute("DELETE FROM gemeentes WHERE id = %s", (gemeente_id,))
                return cur.rowcount > 0

    # SERVICE CRUD
    def get_all_services(self) -> List[Dict[str, Any]]:
        """Get all services from database"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM services ORDER BY category, name")
                return [dict(row) for row in cur.fetchall()]

    def get_service(self, service_id: int) -> Optional[Dict[str, Any]]:
        """Get single service by ID"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, name, description, category, keywords, created_at FROM services WHERE id = %s",
                    (service_id,)
                )
                row = cur.fetchone()
                return dict(row) if row else None

    def create_service(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new service"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    INSERT INTO services (name, description, category, keywords)
                    VALUES (%(name)s, %(description)s, %(category)s, %(keywords)s)
                    RETURNING *
                    """,
                    data
                )
                return dict(cur.fetchone())

    def update_service(self, service_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a service"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build update query dynamically
                fields = []
                values = {}
                for key, value in data.items():
                    if key not in ['id', 'created_at']:
                        fields.append(f"{key} = %({key})s")
                        values[key] = value

                if not fields:
                    return self.get_service(service_id)

                values['id'] = service_id
                query = f"UPDATE services SET {', '.join(fields)} WHERE id = %(id)s RETURNING *"

                cur.execute(query, values)
                row = cur.fetchone()
                return dict(row) if row else None

    def delete_service(self, service_id: int) -> bool:
        """Delete a service"""
        with get_connection() as conn:
            with conn.cursor() as cur:
                # Delete associated associations first
                cur.execute("DELETE FROM associations WHERE service_id = %s", (service_id,))
                # Delete service
                cur.execute("DELETE FROM services WHERE id = %s", (service_id,))
                return cur.rowcount > 0

    # ASSOCIATIONS
    def get_all_associations(self) -> List[Dict[str, Any]]:
        """Get all associations with gemeente and service names"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        a.id,
                        a.gemeente_id,
                        g.name as gemeente_name,
                        a.service_id,
                        s.name as service_name,
                        a.created_at
                    FROM associations a
                    JOIN gemeentes g ON a.gemeente_id = g.id
                    JOIN services s ON a.service_id = s.id
                    ORDER BY g.name, s.name
                    """
                )
                return [dict(row) for row in cur.fetchall()]

    def get_associations_by_gemeente(self, gemeente_id: int) -> List[Dict[str, Any]]:
        """Get associations for a specific gemeente"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, gemeente_id, service_id, created_at FROM associations WHERE gemeente_id = %s",
                    (gemeente_id,)
                )
                return [dict(row) for row in cur.fetchall()]

    def get_associations_by_service(self, service_id: int) -> List[Dict[str, Any]]:
        """Get associations for a specific service"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, gemeente_id, service_id, created_at FROM associations WHERE service_id = %s",
                    (service_id,)
                )
                return [dict(row) for row in cur.fetchall()]

    def create_association(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new association"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Check if already exists
                cur.execute(
                    "SELECT id, gemeente_id, service_id, created_at FROM associations WHERE gemeente_id = %s AND service_id = %s",
                    (data['gemeente_id'], data['service_id'])
                )
                existing = cur.fetchone()
                if existing:
                    return dict(existing)

                # Create new
                cur.execute(
                    """
                    INSERT INTO associations (gemeente_id, service_id)
                    VALUES (%(gemeente_id)s, %(service_id)s)
                    RETURNING *
                    """,
                    data
                )
                return dict(cur.fetchone())

    def delete_association(self, association_id: int) -> bool:
        """Delete an association"""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM associations WHERE id = %s", (association_id,))
                return cur.rowcount > 0

    # STATISTICS
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with get_connection() as conn:
            with conn.cursor() as cur:
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

    # APP SETTINGS
    def get_setting(self, key: str) -> Optional[str]:
        """Get a setting value by key"""
        with get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT value FROM app_settings WHERE key = %s",
                    (key,)
                )
                row = cur.fetchone()
                return row['value'] if row else None

    def update_setting(self, key: str, value: str) -> bool:
        """Update a setting value by key"""
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE app_settings SET value = %s, updated_at = CURRENT_TIMESTAMP WHERE key = %s",
                    (value, key)
                )
                return cur.rowcount > 0


# Global database instance
db = Database()
