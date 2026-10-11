import os
from time import time
from pathlib import Path
from bs4 import BeautifulSoup
import requests
import json
import datetime


DATA_DIR = Path(__file__).resolve().parent.parent / "Data"


def url_scraper(url : str) -> BeautifulSoup:
    #Download a page and parse its HTML for article extraction.
    response=requests.get(url)
    htmlcontent=BeautifulSoup(response.text, 'html.parser')
    return htmlcontent 

def extract_paragraphs(domain : str, scraped : BeautifulSoup, url: str, known_links: dict[str, {"paragraphs": int, "time": float}]) -> BeautifulSoup:
    #Find article paragraphs and skip pages whose paragraph count is unchanged.
    if domain in ['stirilekanald', 'stirileprotv']:
        article=scraped.find('div',class_="article-text")
    if domain=='digi24':
        article=scraped.find('article',class_="article article-story")
    if article is None:
        return []
    scraped=article.find_all('p')

    for element in scraped:
        if element.name!="p":
            element.decompose()
    
    if url not in known_links:
        print(len(scraped))
        
        known_links[url]={}
        known_links[url]['time']=time()
        known_links[url]['paragraphs']=len(scraped)
        return scraped
    if known_links[url]['paragraphs']!=len(scraped):
        known_links[url]['paragraphs']=len(scraped)
    else: 
        
        scraped=[]
    
    return scraped
def make_list(domain: str, data: BeautifulSoup) -> list[str]:
    #Convert paragraph elements to clean text.
    paragraphs : list[str] = [p.get_text().replace("\n", " ") for p in data]
    paragraphs=[p for p in paragraphs if p!=""]
    paragraphs = [" ".join(p.split()) for p in paragraphs]
    if domain=='stirilekanald':
        paragraphs=[p for p in paragraphs if not p.startswith("Citește și")]
    if domain=='digi24':
        paragraphs=[p for p in paragraphs if not p.startswith(("Urmărește","Editor"))]
    return paragraphs
def save_to_json(domain: str, data: BeautifulSoup, filename: str | Path, known_links: dict[str, {"paragraphs": int, "time": float}], url: str) -> None:
    #Persist crawl metadata and append/update one article in the output JSON.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with (DATA_DIR / "known_data.json").open("w", encoding="utf-8") as f:
        json.dump(known_links, f, ensure_ascii=False, indent=2)
    
    paragraphs=make_list(domain, data)
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)
    if filename.exists() and filename.stat().st_size > 0:
        with filename.open("r", encoding="utf-8") as f:
            articles = json.load(f)
    else:
        articles ={}
    articles.setdefault(url, {})
    articles[url]['paragraphs'] = paragraphs
    articles[url]['domain'] = domain
    articles[url]['date']=datetime.date.today().isoformat()
    with filename.open("w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
