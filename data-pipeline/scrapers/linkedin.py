"""Scraper do LinkedIn com gravação dos anúncios no PostgreSQL."""

import sys
from pathlib import Path
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

from database import ensure_schema, get_connection, save_jobs

QUERY = "web dev"
MAX_START = 250
PAGE_SIZE = 25
SOURCE = "linkedin"
HEADERS = {"User-Agent": "Mozilla/5.0"}


# Liga à base de dados e garante que o esquema existe.
with get_connection() as conn:
    ensure_schema(conn)

    # O LinkedIn devolve resultados por blocos de 25.
    # start=0   -> primeiros 25 resultados
    # start=25  -> resultados 26-50
    # start=50  -> resultados 51-75
    seen = set()

    for start in range(0, MAX_START, PAGE_SIZE):
        params = urlencode({"keywords": QUERY, "start": start})
        url = (
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?{params}"
        )

        # Faz o pedido à página de resultados.
        response = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")

        # Conta quantos anúncios novos foram encontrados nesta página.
        new_found = 0
        page_jobs = []

        # Selecciona possíveis cartões de anúncio.
        for card in soup.select("li.base-search-card, li > div.base-card"):
            title = card.select_one(".base-search-card__title")
            company = card.select_one(".base-search-card__subtitle")
            location = card.select_one("[class*='_location']")
            link = card.select_one("a.base-card__full-link")

            # Confirma que existem elementos essenciais antes de continuar.
            if not title or not company or not link:
                continue

            url_job = link.get("href")
            if not url_job or url_job in seen:
                continue

            seen.add(url_job)
            new_found += 1

            job_data = {
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True),
                "location": location.get_text(strip=True) if location else "",
                "url": url_job,
            }
            page_jobs.append(job_data)

            # Mostra os dados principais do anúncio no terminal.
            print(
                new_found,
                "|",
                job_data["title"],
                "|",
                job_data["company"],
                "|",
                job_data["location"],
                "|",
                job_data["url"],
            )

        # Guarda os anúncios recolhidos na base de dados.
        if page_jobs:
            saved_count = save_jobs(conn, page_jobs, SOURCE)
            print(f"Anúncios guardados na base de dados: {saved_count}")

        # Se não apareceram anúncios novos, pára a paginação.
        if new_found == 0:
            break
