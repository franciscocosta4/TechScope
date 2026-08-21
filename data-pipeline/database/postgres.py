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

# Calculamos a raiz do repositório para encontrar o `.env` e o schema
# mesmo quando o script é executado a partir de outra pasta.
REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_ROOT = REPO_ROOT / "data-pipeline"
SCHEMA_PATH = PIPELINE_ROOT / "database" / "migrations" / "001_initial.sql"
ENV_PATH = REPO_ROOT / ".env"

# Carrega automaticamente as variáveis do `.env`.
# Isto evita credenciais hardcoded e mantém o repo seguro.
load_dotenv(ENV_PATH)


def get_connection() -> psycopg.Connection:
    """Abre uma ligação ao PostgreSQL.

    Damos prioridade a `DATABASE_URL` porque simplifica ambientes locais e de
    produção. Se não existir, usamos as variáveis separadas da ligação.
    """
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg.connect(database_url)

    # Se não houver `DATABASE_URL`, usamos variáveis separadas.
    # Isto dá flexibilidade para ambientes locais e produção.
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
        # O schema fica num ficheiro SQL separado para ser mais fácil de rever.
        cur.execute(schema_sql)

    # O commit garante que as tabelas ficam realmente criadas na base de dados.
    conn.commit()


def _normalise_text(value: Any) -> str | None:
    """Limpa valores antes de gravar.

    Remove espaços a mais e converte valores vazios para `None`, porque a BD
    trabalha melhor com nulos do que com strings vazias.
    """
    if value is None:
        return None

    text = str(value).strip()
    # Strings vazias não ajudam na BD; `None` é mais consistente.
    return text or None


def _build_external_id(job: dict[str, Any]) -> str:
    """Gera um identificador estável para deduplicação.

    Se o anúncio já trouxer URL ou ID próprio, usamos isso. Caso contrário,
    geramos um hash com os campos principais para manter consistência.
    """
    external_id = _normalise_text(job.get("url") or job.get("link") or job.get("external_id"))
    if external_id:
        return external_id

    # Se não houver URL/ID estável, criamos uma assinatura simples do anúncio.
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
    text_lower = text.casefold()  # `casefold()` é melhor do que `lower()` para comparações de texto.
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
    - 0.5: a relação vem apenas do contexto da pesquisa
    """
    text = " ".join(filter(None, [title, description]))
    if text and _technology_is_explicitly_mentioned(text, technology_name):
        return 1.0

    # A relação vem só do contexto da pesquisa.
    return 0.5


def save_jobs(
    conn: psycopg.Connection,
    jobs: list[dict[str, Any]],
    source: str,
    technology_name: str,
    query: str,
) -> dict[str, int]:
    """Guarda uma lista de anúncios e relaciona-os com uma tecnologia.

    O fluxo:
    1. garantir que a empresa existe;
    2. verificar se já existe um job igual para essa empresa;
    3. se não existir, criar o job;
    4. guardar a tecnologia e a relação na tabela pivot.
    """
    stats = {
        "processed": 0,
        "inserted": 0,
        "skipped_existing": 0,
        "skipped_invalid": 0,
    }

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

            # `DatePosted` é guardada como data pura, porque no LinkedIn e no
            # Indeed normalmente não existe hora exata do anúncio.
            date_posted = job.get("date_posted")
            if hasattr(date_posted, "date") and not isinstance(date_posted, str):
                date_posted = date_posted.date()

            # Contamos o job logo no início para saber quantos chegaram à camada de BD.
            stats["processed"] += 1

            # Sem título ou empresa o registo fica fraco para análise, por isso
            # ignoramos antes de tocar na base de dados.
            if not title or not company_name:
                stats["skipped_invalid"] += 1
                continue

            # Primeiro garantimos que a empresa existe.
            # O `UNIQUE(Name)` impede duplicados e permite reaproveitar o mesmo id.
            cur.execute(
                """
                INSERT INTO "Companies" ("Id", "Name", "Location")
                VALUES (%s, %s, %s)
                ON CONFLICT ("Name") DO UPDATE
                SET "Location" = COALESCE("Companies"."Location", EXCLUDED."Location")
                RETURNING "Id"
                """,
                (uuid.uuid4(), company_name, location),
            )
            company_id = cur.fetchone()[0]

            # A deduplicação aqui é simples: mesma empresa, mesmo título e mesma localização.
            # Isto evita guardar a mesma vaga duas vezes, mesmo que a URL mude.
            cur.execute(
                """
                SELECT "Id"
                FROM "Jobs"
                WHERE "CompanyId" = %s
                  AND "Title" = %s
                  AND COALESCE("Location", '') = COALESCE(%s, '')
                LIMIT 1
                """,
                (company_id, title, location),
            )
            existing_job = cur.fetchone()

            if existing_job:
                job_id = existing_job[0]
                # Se já existir, não criamos outro registo igual.
                stats["skipped_existing"] += 1
            else:
                # O `ExternalId` continua a ser guardado para manter a origem do anúncio,
                # mas já não é ele que define se o job é novo ou não.
                external_id = _build_external_id(job)

                cur.execute(
                    """
                    INSERT INTO "Jobs" ("Id", "CompanyId", "Title", "Location", "Source", "ExternalId", "DatePosted")
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING "Id"
                    """,
                    (
                        uuid.uuid4(),
                        company_id,
                        title,
                        location,
                        source,
                        external_id,
                        date_posted,
                    ),
                )
                job_id = cur.fetchone()[0]
                # Só contamos como inserido quando o job novo foi mesmo criado.
                stats["inserted"] += 1

            # Guardamos a tecnologia separadamente para normalizar o modelo.
            # `ON CONFLICT` evita duplicar o mesmo nome na tabela `Technologies`.
            cur.execute(
                """
                INSERT INTO "Technologies" ("Name")
                VALUES (%s)
                ON CONFLICT ("Name") DO UPDATE
                SET "Name" = EXCLUDED."Name"
                RETURNING "Id"
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

            # A relação final fica na tabela pivot.
            # O UPSERT impede duplicados e mantém o score mais alto se o mesmo
            # vínculo for encontrado de novo.
            cur.execute(
                """
                INSERT INTO "JobTechnologies" ("JobId", "TechnologyId", "ConfidenceScore")
                VALUES (%s, %s, %s)
                ON CONFLICT ("JobId", "TechnologyId") DO UPDATE
                SET "ConfidenceScore" = GREATEST(
                    "JobTechnologies"."ConfidenceScore",
                    EXCLUDED."ConfidenceScore"
                )
                """,
                (job_id, technology_id, confidence_score),
            )

    # Gravamos tudo no fim para manter a operação consistente.
    conn.commit()
    return stats
