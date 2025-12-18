import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# -----------------------------
# CONFIG
# -----------------------------
BASE_URL = "https://www.shl.com"
CATALOGUE_URL = "https://www.shl.com/products/product-catalog/"
PAGE_SIZE = 12

TEST_TYPE_CODES = {"A", "B", "C", "D", "E", "K", "P", "S"}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (SHL-Academic-Assessment-Crawler/1.0)"
}

# -----------------------------
# HTTP SESSION (ROBUST)
# -----------------------------
def create_session():
    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    session.headers.update(HEADERS)
    return session


# -----------------------------
# UTILITY: extract assessment URLs
# -----------------------------
def extract_links(html):
    soup = BeautifulSoup(html, "lxml")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/products/product-catalog/view/"):
            links.add(BASE_URL + href)

    return links


# -----------------------------
# PHASE 1A: Crawl catalog URLs
# solution_type = 1 (job solutions)
# solution_type = 2 (individual tests)
# -----------------------------
def crawl_catalog_urls(solution_type):
    session = create_session()
    all_links = set()
    start = 0

    print(f"\n[START] Crawling solution_type={solution_type}")

    while True:
        params = {
            "type": solution_type,
            "start": start
        }

        try:
            response = session.get(
                CATALOGUE_URL,
                params=params,
                timeout=(10, 20)
            )
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            print(f"[WARN] start={start} | {e}")
            print("[INFO] Backing off 10 seconds...")
            time.sleep(10)
            continue

        links = extract_links(response.text)

        if not links:
            print(f"[STOP] No links found at start={start}")
            break

        all_links.update(links)

        print(
            f"[INFO] type={solution_type} | start={start} | "
            f"found={len(links)} | total={len(all_links)}"
        )

        start += PAGE_SIZE
        time.sleep(2)

    return sorted(all_links)




# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":

    # ---------- Phase 1A ----------
    urls_type2 = crawl_catalog_urls(2)  # Individual tests
    urls_type1 = crawl_catalog_urls(1)  # Job solutions

    with open("data/assessment_urls_type2.json", "w") as f:
        json.dump(urls_type2, f, indent=2)

    with open("data/assessment_urls_type1.json", "w") as f:
        json.dump(urls_type1, f, indent=2)

    all_urls = sorted(set(urls_type1 + urls_type2))

    with open("data/assessment_urls_all.json", "w") as f:
        json.dump(all_urls, f, indent=2)

    print("\n[SUMMARY]")
    print(f"type=2 (individual tests): {len(urls_type2)}")
    print(f"type=1 (job solutions): {len(urls_type1)}")
    print(f"TOTAL unique solutions: {len(all_urls)}")
