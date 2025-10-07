"""
Security service for password hashing and session management.
Uses bcrypt for secure password hashing with auto-generated salts.
"""
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, Any


class SecurityService:
    """Security utilities for password hashing and session management."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt with auto-generated salt (12 rounds).

        Args:
            password: Plain text password to hash

        Returns:
            Bcrypt hashed password string (starts with $2b$)

        Example:
            >>> hashed = SecurityService.hash_password("mypassword")
            >>> print(hashed[:4])
            $2b$
        """
        # Encode password to bytes and hash with bcrypt
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)  # 12 rounds for balance of security/performance
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a bcrypt hash.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Bcrypt hashed password from database

        Returns:
            True if password matches, False otherwise

        Example:
            >>> hashed = SecurityService.hash_password("test123")
            >>> SecurityService.verify_password("test123", hashed)
            True
            >>> SecurityService.verify_password("wrong", hashed)
            False
        """
        try:
            password_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        except Exception:
            # Invalid hash format or other error
            return False

    @staticmethod
    def generate_session_token() -> str:
        """
        Generate a cryptographically secure session token.

        Returns:
            URL-safe token string (32 bytes = 43 characters base64)

        Example:
            >>> token = SecurityService.generate_session_token()
            >>> len(token)
            43
        """
        return secrets.token_urlsafe(32)

    @staticmethod
    def create_session_data(
        user_id: int,
        username: str,
        expires_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Create session data dictionary for Redis storage.

        Args:
            user_id: Admin user ID
            username: Admin username
            expires_hours: Session expiry in hours (default 24)

        Returns:
            Dictionary with session data including expiry timestamp

        Example:
            >>> data = SecurityService.create_session_data(1, "admin")
            >>> 'user_id' in data and 'username' in data
            True
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=expires_hours)

        return {
            "user_id": user_id,
            "username": username,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
        }

    @staticmethod
    def is_session_expired(session_data: Dict[str, Any]) -> bool:
        """
        Check if a session has expired.

        Args:
            session_data: Session dictionary from Redis

        Returns:
            True if expired, False if still valid
        """
        try:
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            return datetime.utcnow() > expires_at
        except (KeyError, ValueError):
            # Invalid session data
            return True
