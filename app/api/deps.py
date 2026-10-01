"""Dependencias compartidas de la API (DB, auth, etc.)."""

from app.db.session import get_db

__all__ = ["get_db"]
