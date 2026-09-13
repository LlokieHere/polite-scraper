import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def fetch_and_parse_page(url, cache_filename):
    HEADERS = {"User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/LlokieHere/polite-scraper)"}

    if os.path.exists(cache_filename):
        print("CACHE HIT")
        with open(cache_filename, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        print("FETCH")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)

            if response.status_code == 200:
                html = response.text
                os.makedirs("cache", exist_ok=True)
                with open(cache_filename, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"status {response.status_code}, saved {len(html)} bytes")
            else:
                print(f"FAILED: got status {response.status_code}, not saving")
                html = ""

        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL: {e}")
            html = ""

    soup = BeautifulSoup(html, "html.parser")

    book_links = soup.find_all("h3")
    book_urls = []
    for h3 in book_links:
        link_tag = h3.find("a")
        href = link_tag["href"]
        absolute_url = urljoin(url, href)
        book_urls.append(absolute_url)

    next_link = soup.find("li", class_="next")
    if next_link:
        next_href = next_link.find("a")["href"]
        next_url = urljoin(url, next_href)
    else:
        print("No next page")

    return book_urls, next_url

all_books = []
current_url = "https://books.toscrape.com/catalogue/page-1.html"
page_number = 1


while page_number <= 3:
    cache_filename = f"cache/catalogue-page-{page_number}.html"
    books, next_url = fetch_and_parse_page(current_url, cache_filename)
    all_books.extend(books)

    print(f"Page {page_number}: found {len(books)} books")
    page_number += 1
    time.sleep(0.5)
    current_url = next_url

print(f"catalogue_pages={page_number - 1}")
print(f"discovered={len(all_books)}")
unique_books = list(set(all_books))
print(f"unique_urls={len(unique_books)}")