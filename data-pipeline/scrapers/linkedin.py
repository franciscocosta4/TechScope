"""Scraper do LinkedIn com gravação dos anúncios no PostgreSQL."""

import random
import sys
import time
from pathlib import Path
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
if str(PIPELINE_ROOT) not in sys.path:
    sys.path.insert(0, str(PIPELINE_ROOT))

from database import ensure_schema, get_connection, save_jobs
from state import get_next_start, update_last_start

# QUERY é o termo usado no site.
# TECHNOLOGY_NAME é o nome canónico guardado na BD.
# Se quiseres analisar .NET, por exemplo, usa QUERY=".net" e TECHNOLOGY_NAME=".NET".
QUERY = ".NET"
TECHNOLOGY_NAME = QUERY
LOCATION = "Portugal"
MAX_START = 200
PAGE_SIZE = 10
SOURCE = "linkedin"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
    "Referer": "https://www.linkedin.com/jobs/",
}


# Liga à base de dados e garante que o esquema existe.
with get_connection() as conn:
    ensure_schema(conn)

    total_pages = 0
    total_cards_found = 0
    total_jobs_ready = 0
    total_jobs_skipped = 0
    total_jobs_saved = 0

    # O LinkedIn devolve resultados por blocos de 25.
    # start=0   -> primeiros 25 resultados
    # start=25  -> resultados 26-50
    # start=50  -> resultados 51-75
    seen = set()

    # Retoma a paginação a partir do último bloco guardado para esta query.
    start_value = get_next_start(SOURCE, QUERY, PAGE_SIZE)

    # O LinkedIn devolve resultados por blocos fixos de 20 anúncios.
    for start in range(start_value, MAX_START, PAGE_SIZE):
        total_pages += 1
        params = urlencode({"keywords": QUERY, "location": LOCATION, "start": start})
        url = (
            "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
            f"?{params}"
        )
        print(f"A abrir LinkedIn com start={start} url: {url}")

        # Pequena pausa aleatória para reduzir a probabilidade de bloqueio.
        time.sleep(random.uniform(2, 5))

        # Faz o pedido à página de resultados.
        response = requests.get(url, headers=HEADERS, timeout=20)
        print(
            f"HTTP -> status={response.status_code} | "
            f"len_html={len(response.text)} | start={start}"
        )

        soup = BeautifulSoup(response.text, "html.parser")
        # print(response.text)
        job_cards = soup.select("li.base-search-card, li > div.base-card")
        print(f"Cartões encontrados nesta página: {len(job_cards)}")
        total_cards_found += len(job_cards)

        # Conta quantos anúncios novos foram encontrados nesta página.
        new_found = 0
        page_jobs = []
        skipped_jobs = 0

        # Selecciona possíveis cartões de anúncio.
        for card in job_cards:
            title = card.select_one(".base-search-card__title")
            company = card.select_one(".base-search-card__subtitle")
            location = card.select_one("[class*='_location']")
            timetag = card.select_one("[class*='job-search-card__listdate']")
            link = card.select_one("a.base-card__full-link")

            # Confirma que existem elementos essenciais antes de continuar.
            if not title or not company or not link:
                skipped_jobs += 1
                continue

            url_job = link.get("href")
            if not url_job or url_job in seen:
                skipped_jobs += 1
                continue

            seen.add(url_job)
            new_found += 1

            job_data = {
                "title": title.get_text(strip=True),
                "company": company.get_text(strip=True),
                "location": location.get_text(strip=True) if location else "",
                "date_posted": timetag["datetime"],
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
                job_data["date_posted"],
                "|",
                # job_data["url"],
            )

        total_jobs_ready += len(page_jobs)
        total_jobs_skipped += skipped_jobs

        if skipped_jobs:
            print(f"Anúncios ignorados por falta de dados ou duplicados: {skipped_jobs}")

        # Guarda os anúncios recolhidos na base de dados.
        if page_jobs:
            # As stats vêm da camada de BD, porque é lá que a decisão
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

        # Se não apareceram anúncios novos, pára a paginação.
        if new_found == 0:
            break

        update_last_start(SOURCE, QUERY, start)

    print("\nResumo total do run:")
    print(f"Páginas processadas: {total_pages}")
    print(f"Cartões encontrados no total: {total_cards_found}")
    print(f"Anúncios válidos preparados: {total_jobs_ready}")
    print(f"Anúncios ignorados: {total_jobs_skipped}")
    print(f"Anúncios inseridos na base de dados: {total_jobs_saved}")
