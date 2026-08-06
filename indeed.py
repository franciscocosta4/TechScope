"""Scraper simples para recolher anúncios do Indeed por páginas.

O script percorre várias páginas de resultados usando o parâmetro `start`,
abre um browser para cada página, extrai os dados visíveis e fecha o browser
antes de avançar para a página seguinte.
"""

import random

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


# Lista onde guardamos todos os anúncios recolhidos.
all_jobs = []

# Inicia o Playwright.
with sync_playwright() as p:
    # Percorre os resultados em blocos de 15 anúncios.
    for start in range(0, 45, 15):
        url = f"https://www.indeed.com/jobs?q=python&l=Texas&radius=50&start={start}"
        print(f"\nPágina start={start}")

        # Abre um novo browser para cada página.
        browser = p.chromium.launch(headless=False)

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

            # Localiza a secção principal com os resultados.
            results = soup.find(id="mosaic-jobResults")
            if results is None:
                print("Não foi encontrado 'mosaic-jobResults'.")
                continue

            # Selecciona os cartões de cada anúncio.
            job_cards = results.select("[data-testid='slider_item']")
            print(f"Foram encontrados {len(job_cards)} anúncios.\n")

            # Extrai os campos relevantes de cada anúncio.
            for card in job_cards:
                title = card.select_one("[data-testid='job-title']")
                company = card.select_one("[data-testid='company-name']")
                location = card.select_one("[data-testid='text-location']")
                link = card.select_one("a")

                job_data = {
                    "title": title.get_text(strip=True) if title else "",
                    "company": company.get_text(strip=True) if company else "",
                    "location": location.get_text(strip=True) if location else "",
                    "link": (
                        "https://www.indeed.com" + link["href"]
                        if link and link.has_attr("href")
                        else ""
                    ),
                    "start": start,
                }

                # Guarda o anúncio na lista global.
                all_jobs.append(job_data)

                # Mostra o anúncio no terminal.
                print(
                    job_data["title"],
                    "|",
                    job_data["company"],
                    "|",
                    job_data["location"],
                    "|",
                    job_data["link"],
                )
        finally:
            # Fecha sempre o browser, mesmo que ocorra algum erro.
            browser.close()

# Resumo final com o total de anúncios recolhidos.
print(f"\nTotal de anúncios recolhidos: {len(all_jobs)}")