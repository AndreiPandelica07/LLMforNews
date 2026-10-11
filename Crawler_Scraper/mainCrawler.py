import csv
import json
from pathlib import Path
from urllib.parse import urljoin, urlparse

from crawler import get_links, clean_links
from scraper import url_scraper, extract_paragraphs, save_to_json


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
# Crawl configuration stays beside this script; crawl state and article data live in Data/.
DATA_DIR = PROJECT_ROOT / "Data"
KNOWN_DATA_PATH = DATA_DIR / "known_data.json"
OUTPUT_PATH = DATA_DIR / "output.json"
DOMAINS_PATH = SCRIPT_DIR / "domainsToScan.csv"

if KNOWN_DATA_PATH.exists() and KNOWN_DATA_PATH.stat().st_size > 0:
    with KNOWN_DATA_PATH.open("r", encoding="utf-8") as f:
        known_links = json.load(f)
else:
    known_links = {}


def crawl(url:str, max_time:int, known_links: dict[str, {"paragraphs": int, "time": float}]) -> None:
    """Crawl one configured news site and save newly changed articles."""
    links=get_links(max_time, url, known_links)
    
    links=clean_links(links, url)
    domain=urlparse(url).netloc.removeprefix('www.').split('.')[0]
    
    for link in links:
        print(link)
        
        scraped_content = url_scraper(link)    
        extracted_paragraphs = extract_paragraphs(domain,scraped_content, link, known_links)
        if not extracted_paragraphs:
            continue
        save_to_json(domain, extracted_paragraphs, OUTPUT_PATH, known_links, link)
    
# Running this script starts the crawl for every URL listed in domainsToScan.csv.
with DOMAINS_PATH.open("r", encoding="utf-8", newline="") as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        url=row[0]
        print(f"Crawling {url}...")
        crawl(url, 86400, known_links)
