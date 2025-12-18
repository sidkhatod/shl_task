import requests
import re
from bs4 import BeautifulSoup

# ----------------------------
# CONFIG
# ----------------------------
TEST_TYPE_CODES = {"A", "B", "C", "D", "E", "K", "P", "S"}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.shl.com/",
    "Connection": "keep-alive"
}

# ----------------------------
# Generic metadata extractor
# ----------------------------
def extract_metadata_sections(soup):
    """
    Extracts all <h4> -> <p> pairs from
    product-catalogue-training-calendar__row blocks.
    """
    sections = {}

    rows = soup.find_all("div", class_="product-catalogue-training-calendar__row")
    for row in rows:
        h4 = row.find("h4")
        p = row.find("p")

        if h4 and p:
            key = h4.get_text(strip=True).lower()
            value = p.get_text(strip=True)
            sections[key] = value

    return sections


# ----------------------------
# Field-specific parsers
# ----------------------------
def parse_description(sections):
    return sections.get("description", "")


def parse_job_levels(sections):
    text = sections.get("job levels")
    if not text:
        return []
    return [x.strip() for x in text.split(",") if x.strip()]


def parse_languages(sections):
    text = sections.get("languages")
    if not text:
        return []
    return [x.strip() for x in text.split(",") if x.strip()]


def parse_duration_minutes(sections):
    """
    Returns:
    - int if duration is numeric
    - None if missing or TBC
    """
    text = sections.get("assessment length")
    if not text:
        return None

    text_lower = text.lower()

    if "tbc" in text_lower:
        return None

    match = re.search(r"(\d+)", text_lower)
    if match:
        return int(match.group(1))

    return None


def extract_test_types(soup):
    """
    Extracts test type codes (A, B, C, D, E, K, P, S)
    """
    test_types = set()

    for el in soup.find_all(["div", "span", "p"]):
        text = el.get_text(" ", strip=True)
        if text.startswith("Test Type"):
            for c in text.split(":")[-1].split():
                if c in TEST_TYPE_CODES:
                    test_types.add(c)

    return sorted(test_types)


# ----------------------------
# FINAL single-page parser
# ----------------------------
def parse_assessment_page(url: str) -> dict:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Title
    name_tag = soup.find("h1")
    name = name_tag.get_text(strip=True) if name_tag else ""

    # Metadata
    sections = extract_metadata_sections(soup)

    assessment = {
        "assessment_name": name,
        "description": parse_description(sections),
        "test_types": extract_test_types(soup),
        "job_levels": parse_job_levels(sections),
        "languages": parse_languages(sections),
        "duration_minutes": parse_duration_minutes(sections),
        "assessment_url": url
    }

    return assessment

import json
import time
from tqdm import tqdm
import requests

# ----------------------------
# CONFIG
# ----------------------------
INPUT_URL_JSON = "data/crawled/assessment_urls_all.json"      # your existing file
OUTPUT_PARSED_JSON = "data/parsed/assessments_metadata.json"

REQUEST_DELAY = 0.2    # seconds (important to avoid blocking)
MAX_RETRIES = 3


# ----------------------------
# Load URLs
# ----------------------------
with open(INPUT_URL_JSON, "r") as f:
    raw_data = json.load(f)

urls = []
for item in raw_data:
    if isinstance(item, str):
        urls.append(item)
    elif isinstance(item, dict) and "assessment_url" in item:
        urls.append(item["assessment_url"])

urls = list(dict.fromkeys(urls))  # deduplicate, preserve order

print(f"[INFO] Loaded {len(urls)} assessment URLs")


# ----------------------------
# Batch parsing
# ----------------------------
parsed_results = []
failed_urls = []

for url in tqdm(urls, desc="Parsing assessments"):
    success = False

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            assessment = parse_assessment_page(url)
            parsed_results.append(assessment)
            success = True
            break

        except requests.exceptions.RequestException as e:
            print(f"[WARN] Attempt {attempt}/{MAX_RETRIES} failed for {url}")
            time.sleep(2)

    if not success:
        failed_urls.append(url)

    time.sleep(REQUEST_DELAY)


# ----------------------------
# Save outputs
# ----------------------------
with open(OUTPUT_PARSED_JSON, "w") as f:
    json.dump(parsed_results, f, indent=2)

with open("failed_urls.json", "w") as f:
    json.dump(failed_urls, f, indent=2)

print("\n[FINAL]")
print(f"Parsed successfully: {len(parsed_results)}")
print(f"Failed URLs: {len(failed_urls)}")
print(f"Saved → {OUTPUT_PARSED_JSON}")
