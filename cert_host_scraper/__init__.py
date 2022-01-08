
from typing import List
from bs4 import BeautifulSoup

import requests
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
@dataclass
class Result:
    search: str
    total_urls: List[str]
    valid_urls: List[str]


def is_valid_site(url: str) -> bool:
    try:
        result = requests.get(url, timeout=2).status_code == 200
        return result
    except:
        return False


def fetch_site(search: str) -> str:
    url = f"https://crt.sh/?q={search}"
    result = requests.get(url)
    result.raise_for_status()

    return result.content


def scrape_urls(contents: str) -> List[str]:
    soup = BeautifulSoup(contents, features="html.parser")
    tables = soup.findAll("table")
    results_table = tables[2]

    total_urls = []
    for row in results_table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 0:
            continue
        total_urls.append(f"https://{cells[4].decode_contents()}")

    return list(set(total_urls))


def validate_urls(results: List[str]) -> List[str]:
    valid_urls = []
    for i, result in enumerate(results):
        logger.debug(f"Validating {i}/{len(results)}")
        if not is_valid_site(result):
            logger.debug(f"Skipping {result} as invalid site")
            continue
        valid_urls.append(result)

    return valid_urls


def fetch_results_for_search(site: str) -> Result:
    contents = fetch_site(site)
    total_urls = scrape_urls(contents)
    logger.debug(f"Found {len(total_urls)}")
    valid_urls = validate_urls(total_urls)

    return Result(site, total_urls, valid_urls)
