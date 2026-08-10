"""Utilitários para guardar anúncios no PostgreSQL.

Este ficheiro concentra a ligação à base de dados e a lógica de gravação,
para que os scrapers não tenham de repetir código de SQL e configuração.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv

# Calculamos a raiz do repositório para conseguir encontrar o .env e o schema
# mesmo quando o script é executado a partir de qualquer pasta.
REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = REPO_ROOT / "data-pipeline"
SCHEMA_PATH = PIPELINE_ROOT / "database" / "migrations" / "001_initial.sql"
ENV_PATH = REPO_ROOT / ".env"

# Carrega as variáveis do .env automaticamente.
# Isto evita ter credenciais hardcoded no código e mantém o repo seguro.
load_dotenv(ENV_PATH)


def get_connection() -> psycopg.Connection:
    """Abre uma ligação ao PostgreSQL.

    Primeiro tenta `DATABASE_URL` porque é a forma mais simples de configurar
    ambientes locais e de produção. Se não existir, usa as variáveis separadas
    da base de dados.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg.connect(database_url)

    # Estes fallbacks permitem usar o projeto mesmo que o .env esteja dividido
    # em variáveis individuais em vez de uma única URL.
    host = os.getenv("PGHOST", os.getenv("DB_HOST", "localhost"))
    port = int(os.getenv("PGPORT", os.getenv("DB_PORT", "5432")))
    dbname = os.getenv("PGDATABASE", os.getenv("DB_NAME", "techscope"))
    user = os.getenv("PGUSER", os.getenv("DB_USER", "postgres"))
    password = os.getenv("PGPASSWORD", os.getenv("DB_PASSWORD", ""))

    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )


def ensure_schema(conn: psycopg.Connection) -> None:
    """Cria as tabelas base se ainda não existirem.

    O schema fica num ficheiro SQL separado para ser mais fácil de versionar,
    rever e reutilizar sem espalhar SQL pelo código Python.
    """
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")

    with conn.cursor() as cur:
        cur.execute(schema_sql)

    conn.commit()


def _normalise_text(value: Any) -> str | None:
    """Limpa valores antes de gravar.

    Remove espaços a mais e converte valores vazios para `None`, porque a BD
    trabalha melhor com nulos do que com strings vazias.
    """
    if value is None:
        return None

    text = str(value).strip()
    return text or None


def _build_external_id(job: dict[str, Any]) -> str:
    """Gera um identificador estável para evitar duplicados.

    Se o anúncio já trouxer URL ou ID próprio, usamos isso. Caso contrário,
    criamos um hash a partir dos campos principais para identificar o job.
    """
    external_id = _normalise_text(job.get("url") or job.get("link") or job.get("external_id"))
    if external_id:
        return external_id

    fingerprint = "|".join(
        [
            _normalise_text(job.get("title")) or "",
            _normalise_text(job.get("company")) or _normalise_text(job.get("company_name")) or "",
            _normalise_text(job.get("location")) or "",
            _normalise_text(job.get("source")) or "",
        ]
    )
    digest = hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
    return f"generated:{digest}"


def save_jobs(conn: psycopg.Connection, jobs: list[dict[str, Any]], source: str) -> int:
    """Guarda uma lista de anúncios na base de dados.

    A lógica está separada em duas tabelas principais:
    - `companies`: evita repetir a mesma empresa em vários anúncios
    - `jobs`: guarda cada anúncio com `source + external_id` como chave lógica

    Isto facilita deduplicação e deixa o modelo pronto para análises futuras.
    """
    saved_jobs = 0

    with conn.cursor() as cur:
        for job in jobs:
            title = _normalise_text(job.get("title"))
            company_name = _normalise_text(job.get("company") or job.get("company_name"))
            location = _normalise_text(job.get("location"))

            # Sem título ou empresa não vale a pena gravar, porque o registo fica
            # pouco útil para análises e deduplicação.
            if not title or not company_name:
                continue

            # Primeiro garantimos que a empresa existe.
            # Usamos ON CONFLICT para não criar duplicados com o mesmo nome.
            cur.execute(
                """
                INSERT INTO companies (id, name, location)
                VALUES (%s, %s, %s)
                ON CONFLICT (name) DO UPDATE
                SET location = COALESCE(companies.location, EXCLUDED.location)
                RETURNING id
                """,
                (uuid.uuid4(), company_name, location),
            )
            company_id = cur.fetchone()[0]

            # Depois geramos o identificador do anúncio.
            external_id = _build_external_id(job)

            # Finalmente gravamos o job. O ON CONFLICT evita duplicados e permite
            # actualizar dados se o mesmo anúncio aparecer novamente.
            cur.execute(
                """
                INSERT INTO jobs (
                    id,
                    company_id,
                    title,
                    location,
                    salary_min,
                    salary_max,
                    description,
                    source,
                    external_id,
                    date_posted
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source, external_id) DO UPDATE
                SET company_id = EXCLUDED.company_id,
                    title = EXCLUDED.title,
                    location = EXCLUDED.location,
                    salary_min = EXCLUDED.salary_min,
                    salary_max = EXCLUDED.salary_max,
                    description = EXCLUDED.description,
                    date_posted = EXCLUDED.date_posted
                RETURNING id
                """,
                (
                    uuid.uuid4(),
                    company_id,
                    title,
                    location,
                    job.get("salary_min"),
                    job.get("salary_max"),
                    _normalise_text(job.get("description")),
                    source,
                    external_id,
                    job.get("date_posted"),
                ),
            )
            cur.fetchone()
            saved_jobs += 1

    # Commit no fim para gravar tudo de uma vez e manter a operação consistente.
    conn.commit()
    return saved_jobs
