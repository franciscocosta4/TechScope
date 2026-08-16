"""Scraper do Indeed com gravação dos anúncios no PostgreSQL."""

import random
import sys
from pathlib import Path
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

from database import ensure_schema, get_connection, save_jobs
from state import get_next_start, update_last_start

# QUERY é o termo usado no site.
# TECHNOLOGY_NAME é o nome canónico guardado na BD.
# Se quiseres analisar .NET, por exemplo, usa QUERY=".net" e TECHNOLOGY_NAME=".NET".
QUERY = "php"
TECHNOLOGY_NAME = QUERY
LOCATION = "Portugal"
RADIUS = 50
PAGE_SIZE = 15
MAX_START = 90
SOURCE = "indeed"


# Liga à base de dados e garante que o esquema existe.
with get_connection() as conn:
    ensure_schema(conn)

    total_pages = 0
    total_cards_found = 0
    total_jobs_ready = 0
    total_jobs_skipped = 0
    total_jobs_saved = 0

    # Inicia o Playwright.
    with sync_playwright() as p:
        # Retoma a paginação a partir do último bloco guardado para esta query.
        start_value = get_next_start(SOURCE, QUERY, PAGE_SIZE)
        # Percorre os resultados em blocos de 15 anúncios.
        for start in range(start_value, MAX_START, PAGE_SIZE):
            params = urlencode(
                {
                    "q": QUERY,
                    "l": LOCATION,
                    "radius": RADIUS,
                    "start": start,
                }
            )
            url = f"https://pt.indeed.com/jobs?{params}"
            print(f"\nPágina start={start}")

            # Abre um novo browser para cada página.
            browser = p.chromium.launch(headless=False)
            total_pages += 1

            try:
                # Cria um contexto com aspeto mais próximo de um browser real.
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/138.0.0.0 Safari/537.36"
                    ),
                    locale="en-US",
                )

                # Abre uma nova página e navega para o URL da pesquisa.
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded")

                # Pequena pausa aleatória para reduzir a probabilidade de bloqueio.
                page.wait_for_timeout(random.randint(3000, 6000))

                # Obtém o HTML já renderizado pela página.
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")

                # Selecciona os anúncios directamente pela estrutura real do Indeed.
                job_cards = soup.select("td.resultContent")
                total_cards_found += len(job_cards)

                if not job_cards:
                    print("Não foram encontrados cartões de anúncio nesta página.")
                    continue

                print(f"Foram encontrados {len(job_cards)} anúncios.\n")

                page_jobs = []
                skipped_jobs = 0

                # Extrai os campos relevantes de cada anúncio.
                for card in job_cards:
                    title = card.select_one("h3.jobTitle a span")
                    company = card.select_one("span[data-testid='company-name']")
                    location = card.select_one("div[data-testid='text-location']")
                    link = card.select_one("h3.jobTitle a")

                    external_id = ""
                    if link and link.has_attr("data-jk"):
                        external_id = link.get("data-jk", "")
                    elif link and link.has_attr("href"):
                        external_id = link["href"]

                    href = link["href"] if link and link.has_attr("href") else ""
                    if href.startswith("/"):
                        url_job = "https://www.indeed.com" + href
                    else:
                        url_job = href

                    job_data = {
                        "title": title.get_text(strip=True) if title else "",
                        "company": company.get_text(strip=True) if company else "",
                        "location": location.get_text(strip=True) if location else "",
                        "url": url_job,
                        "external_id": external_id,
                        "start": start,
                    }

                    if not job_data["title"] or not job_data["company"]:
                        skipped_jobs += 1
                        continue

                    page_jobs.append(job_data)

                    # Mostra o anúncio no terminal.
                    print(
                        job_data["title"],
                        "|",
                        job_data["company"],
                        "|",
                        job_data["location"],
                        "|",
                        # job_data["url"], está comentado para nao poluir a terminal
                    )

                if skipped_jobs:
                    print(f"Anúncios ignorados por falta de dados: {skipped_jobs}")

                total_jobs_ready += len(page_jobs)
                total_jobs_skipped += skipped_jobs

                # Guarda os anúncios recolhidos na base de dados.
                if page_jobs:
                    # As stats vêm da camada de BD (postegres.py), porque é lá que a decisão
                    # real acontece: inserir, ignorar existentes ou rejeitar inválidos.
                    stats = save_jobs(
                        conn,
                        page_jobs,
                        SOURCE,
                        TECHNOLOGY_NAME,
                        QUERY,
                    )
                    total_jobs_saved += stats["inserted"]
                    print(
                        "BD -> "
                        f"processados: {stats['processed']}, "
                        f"novos: {stats['inserted']}, "
                        f"existentes: {stats['skipped_existing']}, "
                        f"inválidos: {stats['skipped_invalid']}"
                    )

            finally:
                # Fecha sempre o browser, mesmo que ocorra algum erro.
                browser.close()

            update_last_start(SOURCE, QUERY, start)

    print("\nResumo total do run:")
    print(f"Páginas processadas: {total_pages}")
    print(f"Cartões encontrados no total: {total_cards_found}")
    print(f"Anúncios válidos preparados: {total_jobs_ready}")
    print(f"Anúncios ignorados: {total_jobs_skipped}")
    print(f"Anúncios inseridos na base de dados: {total_jobs_saved}")
