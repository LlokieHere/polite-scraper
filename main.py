import requests
import os

CACHE_FILE = "cache/catalogue-page-1.html"
URL = "https://books.toscrape.com/catalogue/page-1.html"
HEADERS = {"User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/LlokieHere/polite-scraper)"}

if os.path.exists(CACHE_FILE):
    print("CACHE HIT")
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        html = f.read()
else:
    print("FETCH")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            html = response.text
            os.makedirs("cache", exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"status {response.status_code}, saved {len(html)} bytes")
        else:
            print(f"FAILED: got status {response.status_code}, not saving")
            html = ""

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        html = ""

print(len(html))