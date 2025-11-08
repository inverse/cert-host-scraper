import asyncio
import logging
from dataclasses import dataclass

import requests
import urllib3

logger = logging.getLogger(__name__)
logging.getLogger("urllib3").setLevel(logging.ERROR)

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
    scraped: list[UrlResult]

    def filter_by_status_code(self, status_code: int) -> list[UrlResult]:
        return [result for result in self.scraped if result.status_code == status_code]


def fetch_site_information(url: str, timeout: int) -> int:
    try:
        return requests.get(url, timeout=timeout).status_code
    except Exception as e:
        logger.debug(e)
        return -1


async def async_fetch_site_information(url: str, timeout: int) -> int:
    return await asyncio.to_thread(fetch_site_information, url, timeout)


def fetch_site(search: str) -> list[dict]:
    url = f"https://crt.sh/?q={search}&output=json"
    result = requests.get(url)
    result.raise_for_status()

    return result.json()


def scrape_urls(results: list[dict], options: Options) -> list[str]:
    total_urls = []
    for result in results:
        common_name = result["common_name"]

        if options.clean and "*" in common_name:
            continue

        total_urls.append(f"https://{common_name}")

    return list(set(total_urls))


def fetch_urls(site: str, options: Options) -> list[str]:
    results = fetch_site(site)
    return scrape_urls(results, options)


async def validate_url(url: str, options: Options) -> UrlResult:
    return UrlResult(url, await async_fetch_site_information(url, options.timeout))
