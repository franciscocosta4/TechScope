"""Utilitários para guardar anúncios no PostgreSQL.

Este ficheiro concentra a ligação à base de dados e a lógica de gravação,
para que os scrapers não tenham de repetir SQL, deduplicação e configuração.
"""

from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import Any

import psycopg
from dotenv import load_dotenv

# Calculamos a raiz do repositório para encontrar o .env e o schema sem depender
# da pasta onde o script é executado.
REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = REPO_ROOT / "data-pipeline"
SCHEMA_PATH = PIPELINE_ROOT / "database" / "migrations" / "001_initial.sql"
ENV_PATH = REPO_ROOT / ".env"

# Carrega automaticamente as variáveis do .env.
# Assim, as credenciais ficam fora do repositório público.
load_dotenv(ENV_PATH)


def get_connection() -> psycopg.Connection:
    """Abre uma ligação ao PostgreSQL.

    Damos prioridade a `DATABASE_URL` porque simplifica ambientes locais e de
    produção. Se não existir, usamos as variáveis separadas da ligação.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg.connect(database_url)

    # Estes fallbacks permitem configurar a base de dados de forma mais explícita
    # quando não se quer usar uma única URL.
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
    """Cria as tabelas base caso ainda não existam.

    O schema fica num ficheiro SQL separado para ser mais fácil de rever,
    versionar e reutilizar pela pipeline.
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
    """Gera um identificador estável para deduplicação.

    Se o anúncio já trouxer URL ou ID próprio, usamos isso. Caso contrário,
    geramos um hash com os campos principais para manter consistência.
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


def _technology_is_explicitly_mentioned(text: str, technology_name: str) -> bool:
    """Verifica se a tecnologia aparece de forma clara no texto.

    Usamos uma verificação simples por substring porque é fácil de manter.
    Para `.NET`, também aceitamos `dotnet` como forma comum de escrita.
    """
    text_lower = text.casefold()
    tech_lower = technology_name.casefold()

    if tech_lower in text_lower:
        return True

    if tech_lower == ".net" and "dotnet" in text_lower:
        return True

    return False


def _confidence_score(
    query: str,
    technology_name: str,
    title: str | None,
    description: str | None = None,
) -> float:
    """Calcula o score de confiança da relação job-tecnologia.

    Regras simples:
    - 1.0: a tecnologia aparece explicitamente no título ou descrição
    - 0.9: a query é exactamente a tecnologia pesquisada
    - 0.7: a relação vem apenas do contexto da pesquisa
    """
    text = " ".join(filter(None, [title, description]))
    if text and _technology_is_explicitly_mentioned(text, technology_name):
        return 1.0

    if query.casefold().strip() == technology_name.casefold().strip():
        return 0.9

    return 0.7


def save_jobs(
    conn: psycopg.Connection,
    jobs: list[dict[str, Any]],
    source: str,
    technology_name: str,
    query: str,
) -> int:
    """Guarda uma lista de anúncios e relaciona-os com uma tecnologia.

    O fluxo é este:
    1. garantir que a empresa existe;
    2. gravar o job sem duplicar;
    3. garantir que a tecnologia existe;
    4. criar a relação em `job_technologies` com `confidence_score`.
    """
    saved_jobs = 0

    technology_name = _normalise_text(technology_name)
    query = _normalise_text(query) or ""

    if not technology_name:
        raise ValueError("technology_name é obrigatório para guardar jobs.")

    with conn.cursor() as cur:
        for job in jobs:
            title = _normalise_text(job.get("title"))
            company_name = _normalise_text(job.get("company") or job.get("company_name"))
            location = _normalise_text(job.get("location"))
            description = _normalise_text(job.get("description"))

            # Sem título ou empresa o registo fica fraco para análise, por isso
            # ignoramos antes de tocar na base de dados.
            if not title or not company_name:
                continue

            # Primeiro garantimos que a empresa existe.
            # O UNIQUE(name) impede duplicados e permite reaproveitar o mesmo id.
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

            # A deduplicação aqui é simples: mesma empresa, mesmo título e mesma localização.
            # Assim evitamos guardar a mesma vaga duas vezes, mesmo que a URL mude.
            cur.execute(
                """
                SELECT id
                FROM jobs
                WHERE company_id = %s
                  AND title = %s
                  AND COALESCE(location, '') = COALESCE(%s, '')
                LIMIT 1
                """,
                (company_id, title, location),
            )
            existing_job = cur.fetchone()

            if existing_job:
                job_id = existing_job[0]
            else:
                # O external_id continua a ser guardado para manter a origem do anúncio,
                # mas já não é ele que define se o job é novo ou não.
                external_id = _build_external_id(job)

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
                    RETURNING id
                    """,
                    (
                        uuid.uuid4(),
                        company_id,
                        title,
                        location,
                        job.get("salary_min"),
                        job.get("salary_max"),
                        description,
                        source,
                        external_id,
                        job.get("date_posted"),
                    ),
                )
                job_id = cur.fetchone()[0]

            # Guardamos a tecnologia separadamente para normalizar o modelo.
            cur.execute(
                """
                INSERT INTO technologies (name)
                VALUES (%s)
                ON CONFLICT (name) DO UPDATE
                SET name = EXCLUDED.name
                RETURNING id
                """,
                (technology_name,),
            )
            technology_id = cur.fetchone()[0]

            # O score é simples e ajuda-nos a perceber quanta confiança existe
            # nesta relação job-tecnologia.
            confidence_score = _confidence_score(
                query=query,
                technology_name=technology_name,
                title=title,
                description=description,
            )

            # A relação final fica na tabela pivot. O UPSERT impede duplicados e
            # mantém o score mais alto caso o mesmo vínculo seja reencontrado.
            cur.execute(
                """
                INSERT INTO job_technologies (job_id, technology_id, confidence_score)
                VALUES (%s, %s, %s)
                ON CONFLICT (job_id, technology_id) DO UPDATE
                SET confidence_score = GREATEST(
                    job_technologies.confidence_score,
                    EXCLUDED.confidence_score
                )
                """,
                (job_id, technology_id, confidence_score),
            )

            saved_jobs += 1

    # Gravamos tudo no fim para manter a operação consistente.
    conn.commit()
    return saved_jobs
