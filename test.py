import requests
from bs4 import BeautifulSoup

url = "https://www.linkedin.com/jobs/search/?keywords=web%20dev"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

resp = requests.get(url, headers=headers, timeout=20)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "html.parser")

for card in soup.select("li.base-search-card, li > div.base-card"):
    title = card.select_one("[class*='_title']")
    company = card.select_one("[class*='_subtitle']")
    location = card.select_one("[class*='_location']")
    link = card.select_one("[class*='_full-link']")

    if title and company:
        print(
            title.get_text(strip=True),
            "|",
            company.get_text(strip=True),
            "|",
            location.get_text(strip=True) if location else "",
            "|",
            link["href"] if link and link.has_attr("href") else ""
        )