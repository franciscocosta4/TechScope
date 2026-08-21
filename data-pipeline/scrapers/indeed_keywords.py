"""Scraper de keywords de descrições de anúncios do Indeed.

Percorre a base de dados, abre cada página de anúncio,
extrai a descrição e guarda as keywords encontradas na tabela JobKeywords.
"""

import random
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

CHROME_CDP_URL = "http://localhost:9222"
SOURCE = "indeed"
BATCH_SIZE = 50

from database import get_connection
from keyword_extractor import extract_keywords


def fetch_jobs_without_keywords(conn, source: str, limit: int) -> list[dict]:
    """Busca jobs sem keywords, ordenados por CreatedAt."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT j."Id", j."ExternalId", j."Title", j."Location", j."CreatedAt"
            FROM "Jobs" j
            WHERE j."Source" = %s
              AND j."Id" NOT IN (
                  SELECT "JobId" FROM "JobKeywords"
              )
            ORDER BY j."CreatedAt" ASC
            LIMIT %s
            """,
            (source, limit),
        )
        rows = cur.fetchall()
    return [
        {
            "id": row[0],
            "external_id": row[1],
            "title": row[2],
            "location": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]


def scrape_indeed_description(external_id: str) -> str | None:
    """Abre a página de um anúncio do Indeed e extrai o texto da descrição."""
    if not external_id:
        return None

    url = urljoin("https://pt.indeed.com/viewjob?jk=", external_id)

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CHROME_CDP_URL)
        context = browser.contexts[0] if browser.contexts else browser.new_context()
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(random.uniform(3, 6))

            html = page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Seletores comuns do Indeed para descrição
            desc_elem = soup.select_one(
                "#jobDescriptionText, .jobsearch-JobComponent-description, #vjs-content"
            )
            if desc_elem:
                return desc_elem.get_text(separator="\n", strip=True)

            return None
        except Exception as e:
            print(f"Erro ao abrir {url}: {e}")
            return None
        finally:
            page.close()


def save_keywords(conn, job_id, keywords: dict[str, list[str]]) -> None:
    """Guarda as keywords extraídas na tabela JobKeywords."""
    with conn.cursor() as cur:
        for category, words in keywords.items():
            for keyword in words:
                cur.execute(
                    """
                    INSERT INTO "JobKeywords" ("JobId", "Keyword", "Category")
                    VALUES (%s, %s, %s)
                    ON CONFLICT ("JobId", "Keyword", "Category") DO NOTHING
                    """,
                    (job_id, keyword, category),
                )
    conn.commit()


def main():
    with get_connection() as conn:
        jobs = fetch_jobs_without_keywords(conn, SOURCE, BATCH_SIZE)

        if not jobs:
            print(f"Nenhum job novo para processar em {SOURCE}.")
            return

        print(f"A processar {len(jobs)} jobs de {SOURCE}...")

        processed = 0
        skipped = 0

        for job in jobs:
            job_id = job["id"]
            title = job["title"]
            external_id = job["external_id"]

            print(f"\nJob: {title[:60]}...")

            if not external_id:
                print("  Sem external_id, a saltar.")
                skipped += 1
                continue

            description = scrape_indeed_description(external_id)

            if not description:
                print("  Sem descrição, a saltar.")
                skipped += 1
                continue

            keywords = extract_keywords(title, description)

            if keywords:
                save_keywords(conn, job_id, keywords)
                print(f"  Keywords: {keywords}")
            else:
                print("  Nenhuma keyword encontrada.")

            processed += 1
            time.sleep(random.uniform(2, 5))

        print(f"\nResumo: {processed} processados, {skipped} ignorados.")


if __name__ == "__main__":
    main()
