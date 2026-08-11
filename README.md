## Target Classification

**Site:** [Books to Scrape](https://books.toscrape.com/)

**Why this site:** Books to Scrape explicitly states on its homepage that it exists as a training ground for people learning to scrape, making it an appropriate and intended target for this project.

**Scope:** This project scrapes only the first 3 catalogue pages (roughly 60 books), not the site's full catalogue.

**Data collected:** For each book, we collect: title, product URL, price, availability, rating, description, source page, and fetch timestamp.

**robots.txt result:** Requesting `https://books.toscrape.com/robots.txt` returns a 404 — no robots file exists. A missing file is not the same as permission, so this project still applies caution regardless: a deliberate delay between requests, an honest, identifying user-agent, and fetching only the pages explicitly scoped for this assignment.

I will not reuse this code on another site without checking its rules and terms first.