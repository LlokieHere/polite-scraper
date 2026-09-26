## Target Classification

**Site:** [Books to Scrape](https://books.toscrape.com/)

**Why this site:** Books to Scrape explicitly states on its homepage that it exists as a training ground for people learning to scrape, making it an appropriate and intended target for this project.

**Scope:** This project scrapes only the first 3 catalogue pages (roughly 60 books), not the site's full catalogue.

**Data collected:** For each book, we collect: title, product URL, price, availability, rating, description, source page, and fetch timestamp.

**robots.txt result:** Requesting `https://books.toscrape.com/robots.txt` returns a 404 — no robots file exists. A missing file is not the same as permission, so this project still applies caution regardless: a deliberate delay between requests, an honest, identifying user-agent, and fetching only the pages explicitly scoped for this assignment.

I will not reuse this code on another site without checking its rules and terms first.

## Setup & Run

1. Clone this repo
2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/Scripts/activate   # Windows Git Bash
   source venv/bin/activate       # Mac/Linux
   ```
3. Install dependencies:
   ```
   pip install requests beautifulsoup4 pydantic
   ```
4. Run the scraper:
   ```
   python main.py
   ```
5. Check the results in `output/books.json`, `output/errors.json`, and `output/run-report.json`

## Record Schema

| Field | Type | Notes |
|---|---|---|
| `title` | string | Book title |
| `product_url` | string | Absolute URL to the book's page |
| `price_text` | string | Raw price as scraped, e.g. `£51.77` |
| `price_gbp` | float | Cleaned numeric price, e.g. `51.77` |
| `availability_text` | string | e.g. `In stock (22 available)` |
| `rating_text` | string | Word rating, e.g. `Three` |
| `description` | string or null | May be `null` if the book has no description |
| `source_page` | string | Which catalogue page this book was discovered on |
| `fetched_at` | string | ISO 8601 UTC timestamp of when this record was fetched |

## Politeness Rules

- Every real request sends an identifying `User-Agent`: `FlyRankInternship-A9/1.0 (+https://github.com/LlokieHere/polite-scraper)`
- Every request has a 10-second timeout
- A 0.5 second delay is applied between real (non-cached) requests
- All pages are cached locally after first fetch; development and re-runs read from cache instead of re-hitting the site
- Only the first 3 catalogue pages (60 books) are scraped — never the full 1000-book catalogue

## Why No Browser Was Needed

All the data (title, price, availability, rating, description) is present directly in the HTML the server sends back — nothing is loaded dynamically with JavaScript, so a full browser would only add unnecessary cost and complexity.

## Sample Run Report

{
  "start_time": "2026-09-26T11:47:28.538254+00:00",
  "end_time": "2026-09-26T11:48:03.094132+00:00",
  "duration_seconds": 34.555878,
  "pages_fetched": 3,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 1
}

## Known Limitation

This scraper does not implement retry-with-backoff for temporary failures (timeouts, 5xx errors) — a failed page is logged once and skipped rather than retried. This is a deliberate simplification for this stage; real retry logic with exponential backoff is planned for a later assignment.

## Ethics Note

This project only scrapes Books to Scrape, a site explicitly built for scraping practice, and only within the 3-page scope defined for this assignment. Where a real API exists for a target site, it should always be preferred over scraping. This code should never be pointed at another site, a login-gated page, or a paywall without first checking that site's own terms and rules.
```
