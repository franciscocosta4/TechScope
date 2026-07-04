import requests
from bs4 import BeautifulSoup

url = "https://www.indeed.com/jobs?q=python&l=Texas"
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

resp = requests.get(url, headers=headers, timeout=20)
# resp.raise_for_status()
print(resp.status_code)
print(resp.text[:1000])

soup = BeautifulSoup(resp.text, "html.parser")

results = soup.find(id="mosaic-jobResults")
job_cards = results.find_all("td", class_="resultContent css-1o6lhys eu4oa1w0")

for job_card in job_cards:
    title = card.select_one("[class*='jcs-JobTitle']")
    # company = card.select_one("[class*='_subtitle']")
    location = card.select_one("[class*='company_location']")
    link = card.select_one("[class*='jcs-JobTitle']")

    if title and company:
        print(
            title.get_text(strip=True),
            "|",
            # company.get_text(strip=True),
            # "|",
            location.get_text(strip=True) if location else "",
            "|",
            link["href"] if link and link.has_attr("href") else ""
        )