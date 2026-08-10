"""Camada de base de dados do TechScope."""

from .postgres import ensure_schema, get_connection, save_jobs

__all__ = ["ensure_schema", "get_connection", "save_jobs"]
