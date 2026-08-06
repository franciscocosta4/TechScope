"""Scraper simples para recolher anúncios do LinkedIn.

Este script usa o endpoint público de "seeMoreJobPostings" do LinkedIn para
carregar blocos de resultados por offset (`start`).
A cada iteração:
- faz um pedido HTTP ao LinkedIn;
- interpreta o HTML devolvido;
- extrai os dados dos anúncios;
- evita duplicados;
- pára quando já não encontra novos resultados.
"""

import requests
from bs4 import BeautifulSoup


# Cabeçalho mínimo para simular um browser.
headers = {"User-Agent": "Mozilla/5.0"}

# Conjunto usado para evitar anúncios repetidos.
seen = set()

# O LinkedIn devolve resultados por blocos de 25.
# start=0   -> primeiros 25 resultados
# start=25  -> resultados 26-50
# start=50  -> resultados 51-75
for start in range(0, 250, 25):
    url = (
        "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
        f"?keywords=web%20dev&start={start}"
    )

    # Faz o pedido à página de resultados.
    r = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    # Conta quantos anúncios novos foram encontrados nesta página.
    new_found = 0

    # Selecciona possíveis cartões de anúncio.
    for card in soup.select("li.base-search-card, li > div.base-card"):
        title = card.select_one("[class*='_title']")
        company = card.select_one("[class*='_subtitle']")
        location = card.select_one("[class*='_location']")
        link = card.select_one("[class*='_full-link']")

        # Confirma que existem elementos essenciais antes de continuar.
        if title and company:
            link = card.select_one("a.base-card__full-link")
            title = card.select_one(".base-search-card__title")
            company = card.select_one(".base-search-card__subtitle")

            if not link or not title or not company:
                continue

            href = link.get("href")
            if href in seen:
                continue

            seen.add(href)
            new_found += 1

            # Mostra os dados principais do anúncio no terminal.
            print(
                new_found,
                "|",
                title.get_text(strip=True),
                "|",
                company.get_text(strip=True),
                "|",
                location.get_text(strip=True) if location else "",
                "|",
                url,
                # href if href else "",
            )

    # Se não apareceram anúncios novos, pára a paginação.
    if new_found == 0:
        break