from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass

import requests
import urllib3
from tenacity import (
    before_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from cert_host_scraper import __version__

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

    def filter_by_status_code(self, status_code: int) -> Result:
        return Result(
            [result for result in self.scraped if result.status_code == status_code]
        )


def _default_headers() -> dict:
    return {
        "User-Agent": f"Mozilla/5.0 Cert-Host-Scraper/{__version__} (https://github.com/inverse/cert-host-scraper)"
    }


def fetch_site_information(url: str, timeout: int) -> int:
    try:
        return requests.get(url, timeout=timeout).status_code
    except requests.RequestException as e:
        logger.debug(e)
        return -1


async def async_fetch_site_information(url: str, timeout: int) -> int:
    return await asyncio.to_thread(fetch_site_information, url, timeout)


@retry(
    retry=retry_if_exception_type(
        (requests.RequestException, urllib3.exceptions.HTTPError)
    ),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True,
    before=before_log(logger, logging.DEBUG),
)
def fetch_site(search: str) -> list[dict]:
    url = f"https://crt.sh/?q={search}&output=json"
    result = requests.get(url, headers=_default_headers())
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
    logger.debug(f"Found {len(results)} results for {site}")
    urls = scrape_urls(results, options)
    logger.debug(f"Found {len(urls)} URLs for {site}")

    return urls


async def validate_url(url: str, options: Options) -> UrlResult:
    return UrlResult(url, await async_fetch_site_information(url, options.timeout))


async def _process_urls(
    urls: list[str],
    options: Options,
    batch_size: int,
    *,
    on_progress: Callable[[], object] | None = None,
) -> list[UrlResult]:
    sem = asyncio.Semaphore(batch_size)

    async def fetch(url: str) -> UrlResult:
        async with sem:
            result = await validate_url(url, options)
            if on_progress:
                on_progress()
            return result

    return await asyncio.gather(*[fetch(u) for u in urls])


def process_urls(
    urls: list[str],
    options: Options,
    batch_size: int,
    *,
    on_progress: Callable[[], object] | None = None,
) -> Result:
    """
    Process a list of URLs concurrently and return the results.
    """
    scraped = asyncio.run(
        _process_urls(urls, options, batch_size, on_progress=on_progress)
    )
    return Result(scraped)


def search_urls(
    search_term: str,
    options: Options,
    batch_size: int = 20,
    *,
    on_progress: Callable[[], object] | None = None,
) -> Result:
    """
    Fetch certificate log URLs and scrape their status codes.
    """
    urls = fetch_urls(search_term, options)
    return process_urls(urls, options, batch_size, on_progress=on_progress)
