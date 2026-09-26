from datetime import datetime, timezone
from itertools import product
from typing import Optional
from wsgiref import validate
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from pydantic import BaseModel, ValidationError
from typing import Optional
import json

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    availability_text: str
    rating_text: str
    price_gbp: float
    description: Optional[str] = None
    source_page: str
    fetched_at: str

HEADERS = {"User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/LlokieHere/polite-scraper)"}

def fetch_and_parse_page(url, cache_filename):
    if os.path.exists(cache_filename):
        print("CACHE HIT")
        with open(cache_filename, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        print("FETCH")
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.encoding = 'utf-8'
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
        next_url = None
        print("No next page")

    return book_urls, next_url


def extract_book_record(book_url, source_page):
    file_name = book_url.split("/")
    cache_filename = f"cache/{file_name[4]}.html"

    if os.path.exists(cache_filename):
        print("CACHE HIT")
        with open(cache_filename, "r", encoding="utf-8") as f:
            html = f.read()
    else:
        
        print("FETCH")
        try:
            response = requests.get(book_url, headers=HEADERS, timeout=10)
            response.encoding = 'utf-8'
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

    title = soup.find("h1").text
    price_text = soup.find("p", class_="price_color").text
    price_gbp = float(price_text.replace("£", ""))
    availability_text = soup.find("p", class_="instock availability").text.strip()
    rating_tag = soup.find("p", class_="star-rating")
    rating_text = rating_tag["class"][1]
    description_tag = soup.find("div", id="product_description")

    if description_tag:
        description = description_tag.find_next_sibling("p").text
    else:
        description = None

    record = {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "price_gbp": price_gbp,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

    return record


run_start = datetime.now(timezone.utc)
# --- Stage 2: discover all book URLs across 3 catalogue pages ---
all_books = []
current_url = "https://books.toscrape.com/catalogue/page-1.html"
page_number = 1

while page_number <= 3:
    cache_filename = f"cache/catalogue-page-{page_number}.html"
    books, next_url = fetch_and_parse_page(current_url, cache_filename)

    for book_url in books:
        all_books.append((book_url, current_url))

    print(f"Page {page_number}: found {len(books)} books")
    page_number += 1
    time.sleep(0.5)
    current_url = next_url

print(f"catalogue_pages={page_number - 1}")
print(f"discovered={len(all_books)}")

unique_books = list(set(all_books))
print(f"unique_urls={len(unique_books)}")

unique_books.append(("https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html", "https://books.toscrape.com/catalogue/page-1.html"))
print(f"unique_urls={len(unique_books)}")  # should now show 61
# --- Stage 3: extract full record for every unique book ---
all_records = []
failed_pages = []

for book_url, source_page in unique_books:
    try:
        record = extract_book_record(book_url, source_page)
        all_records.append(record)
    except Exception as e:
        print(f"FAILED: {book_url} - {e}")
        failed_pages.append({"url": book_url, "error": str(e)})
    time.sleep(0.5)

print(f"failed_pages={len(failed_pages)}")

print(f"detail_pages={len(all_records)}")

valid_records = []
invalid_records = []

for record in all_records:
    try: 
        validated = BookRecord(**record)
        valid_records.append(validated.model_dump())
    except ValidationError as e:
        invalid_records.append({"record": record, "error": str(e)})

print(f"valid: {len(valid_records)}")
print(f"invalid: {len(invalid_records)}")

os.makedirs("output", exist_ok=True)

with open("output/books.json", "w", encoding="utf-8") as f:
    json.dump(valid_records, f, indent=2, ensure_ascii=False)

with open("output/errors.json", "w", encoding="utf-8") as f:
    json.dump(invalid_records, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(valid_records)} records to output/books.json")
print(f"Wrote {len(invalid_records)} records to output/errors.json")


run_end = datetime.now(timezone.utc)

run_report = {
    "start_time": run_start.isoformat(),
    "end_time": run_end.isoformat(),
    "duration_seconds": (run_end - run_start).total_seconds(),
    "pages_fetched": page_number - 1,
    "valid_records": len(valid_records),
    "invalid_records": len(invalid_records),
    "failed_pages": len(failed_pages),
}

with open("output/run-report.json", "w", encoding="utf-8") as f:
    json.dump(run_report, f, indent=2, ensure_ascii=False)

print(f"Wrote run report to output/run-report.json")