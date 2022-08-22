import logging
from dataclasses import dataclass
from typing import List

import requests
import urllib3
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


urllib3.disable_warnings()


@dataclass
class Options:
    timeout: int
    clean: bool


@dataclass
class UrlResult:
    url: str
    status_code: int


@dataclass
class Result:
    scraped: List[UrlResult]

    def filter_by_status_code(self, status_code: int) -> List[UrlResult]:
        return [result for result in self.scraped if result.status_code == status_code]


def fetch_site_information(url: str, timeout: int) -> int:
    try:

        return requests.get(url, timeout=timeout).status_code
    except Exception as e:
        logger.debug(e)
        return -1


def fetch_site(search: str) -> str:
    url = f"https://crt.sh/?q={search}"
    result = requests.get(url)
    result.raise_for_status()

    return result.content.decode()


def scrape_urls(contents: str, options: Options) -> List[str]:
    soup = BeautifulSoup(contents, features="html.parser")
    tables = soup.findAll("table")

    if len(tables) <= 2:
        return []

    results_table = tables[2]

    total_urls = []
    for row in results_table.findAll("tr"):
        cells = row.findAll("td")
        if len(cells) == 0:
            continue

        matching_identity = cells[4].decode_contents()
        if options.clean and "*" in matching_identity:
            continue

        total_urls.append(f"https://{matching_identity}")

    return list(set(total_urls))


def validate_url(url: str, options: Options) -> UrlResult:
    return UrlResult(url, fetch_site_information(url, options.timeout))


def fetch_urls(site: str, options: Options) -> List[str]:
    contents = fetch_site(site)
    urls = scrape_urls(contents, options)
    return urls
