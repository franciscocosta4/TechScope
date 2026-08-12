"""Limpa e recria a base de dados do TechScope.

Usa este script quando quiseres começar do zero e garantir que o schema
fica alinhado com a versão actual do código.
"""

from __future__ import annotations

import sys
from pathlib import Path

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

from database import ensure_schema, get_connection


def reset_database() -> None:
    """Apaga as tabelas principais e recria o schema actual."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Drop completo para garantir que as colunas novas (como o ID auto-
            # incrementado em technologies) ficam mesmo aplicadas.
            cur.execute(
                """
                DROP TABLE IF EXISTS job_technologies;
                DROP TABLE IF EXISTS jobs;
                DROP TABLE IF EXISTS technologies;
                DROP TABLE IF EXISTS companies;
                """
            )
        conn.commit()
        ensure_schema(conn)


if __name__ == "__main__":
    reset_database()
    print("Base de dados limpa e recriada com sucesso.")
