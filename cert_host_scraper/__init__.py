
from typing import List
from bs4 import BeautifulSoup

import requests
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UrlResult:
    url: str
    status_code: int


@dataclass
class Result:
    search: str
    scraped: List[UrlResult]


def fetch_site_information(url: str) -> int:
    try:
        return requests.get(url, timeout=2).status_code
    except Exception as e:
        logger.debug(e)
        return -1


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


def validate_urls(results: List[str]) -> List[UrlResult]:
    valid_urls = []
    for i, url in enumerate(results):
        logger.info(f"Validating {i}/{len(results)}")
        status_code = fetch_site_information(url)
        valid_urls.append(UrlResult(url, status_code))

    return valid_urls


def fetch_results_for_search(site: str) -> Result:
    contents = fetch_site(site)
    total_urls = scrape_urls(contents)
    logger.debug(f"Found {len(total_urls)}")
    url_results = validate_urls(total_urls)

    return Result(site, url_results)
