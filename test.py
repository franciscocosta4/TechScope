import requests
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0"}
seen = set()

for start in range(0, 250, 25):  #é um offset, ou seja vai das paginas de job : start=0 → jobs 1–25. start=25 → jobs 26–50. start=50 → jobs 51–75.
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=web%20dev&start={start}"
    r = requests.get(url, headers=headers, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    new_found = 0
    for card in soup.select("li.base-search-card, li > div.base-card"):
        title = card.select_one("[class*='_title']")
        company = card.select_one("[class*='_subtitle']")
        location = card.select_one("[class*='_location']")
        link = card.select_one("[class*='_full-link']")

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
            print(
                new_found,
                "|",
                title.get_text(strip=True),
                "|",
                company.get_text(strip=True),
                "|",
                location.get_text(strip=True) if location else "",
                "|",
                url
                # link["href"] if link and link.has_attr("href") else "" 
            )

    if new_found == 0:
        break