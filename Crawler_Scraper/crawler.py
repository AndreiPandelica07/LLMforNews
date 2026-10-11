import requests
from bs4 import BeautifulSoup
import json
import os
from time import time
from urllib.parse import urljoin, urlparse



def clean_links(links: list[str], url:str) -> list[str]:
    #Remove duplicate, pagination, and non-article links; return absolute URLs.
    domain = urlparse(url).netloc.removeprefix("www.").split(".")[0]
    cleaned_links: list[str] = []
    count={}
    if domain=='digi24':
        for link in links:
            count[link]=count.get(link, 0)+1
            if count[link]>1:
                continue
    
            if link is not None and link.startswith("/stiri/"):
                cleaned_links.append(urljoin(url, link))
        return cleaned_links
    
    if domain=='stirilekanald':
        for link in links:
            count[link]=count.get(link, 0)+1
            if count[link]>1:
                continue
            last_part=urlparse(link).path.rstrip('/').split('/')[-1]
            if link is not None and not last_part.startswith('pagina-'):
                cleaned_links.append(urljoin(url,link))
        return cleaned_links
    if domain=='stirileprotv':
        for link in links:
            count[link]=count.get(link,0)+1
            if count[link]>1:
                continue
            if link is not None:
                cleaned_links.append(urljoin(url,link))
        return cleaned_links
def get_links(max_time: int , url: str, known_links: dict[str, {"paragraphs": int, "time": float}]) ->list[str]:
    """Fetch a section page and collect article links not recently processed."""
    response=requests.get(url)
    htmlcontent=BeautifulSoup(response.text, 'html.parser')
    links: list[str] = []
    domain = urlparse(url).netloc.removeprefix("www.").split(".")[0]
    print(domain)
    # Digi24 and Stirilekanald use numeric article URL endings; ProTV uses .html.
    if domain in ['stirilekanald', 'digi24']:
        print("ok")
        for link in htmlcontent.find_all('a'):
            link_href = link.get('href')
            if not link_href: 
                continue
            parsed_url = urlparse(link_href)
      
            if parsed_url.query:
                continue
        
            if not link_href[-1].isnumeric():
                continue
            full_url = urljoin(url, link_href)
            print(full_url)
            if full_url not in known_links or time()-known_links[full_url]['time']<max_time:
                links.append(link_href)
        return links
    if domain in ['stirileprotv']:
        for link in htmlcontent.find_all('a'):
            link_href = link.get('href')
            if not link_href: 
                continue
            parsed_url = urlparse(link_href)          
            if parsed_url.query:                        
                continue
                
            if not link_href.endswith(".html"):
                continue
            full_url=urljoin(url, link_href)
            if full_url not in known_links or time()-known_links[full_url]['time']<max_time:
                links.append(link_href)
        return links
                

