from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

url = "https://www.indeed.com/jobs?q=python&l=Texas"

with sync_playwright() as p:

    # Inicia o Chromium
    browser = p.chromium.launch(
        headless=False  # False para testar
    )

    # Cria um contexto semelhante a um navegador real
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        locale="en-US"
    )

    page = context.new_page()

    # Abre a página
    page.goto(url, wait_until="networkidle")

    # Obtém o HTML já renderizado
    html = page.content()

    browser.close()

soup = BeautifulSoup(html, "html.parser")

results = soup.find(id="mosaic-jobResults")

if results is None:
    print("Não foi encontrado 'mosaic-jobResults'.")
    exit()

job_cards = results.select("[data-testid='slider_item']")

print(f"Foram encontrados {len(job_cards)} anúncios.\n")

for card in job_cards:

    title = card.select_one("[data-testid='job-title']")

    company = card.select_one("[data-testid='company-name']")

    location = card.select_one("[data-testid='text-location']")

    link = card.select_one("a")

    print(
        title.get_text(strip=True) if title else "",
        "|",
        company.get_text(strip=True) if company else "",
        "|",
        location.get_text(strip=True) if location else "",
        "|",
        "https://www.indeed.com" + link["href"] if link and link.has_attr("href") else ""
    )