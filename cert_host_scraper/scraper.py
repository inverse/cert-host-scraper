import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass

import requests
import urllib3

from cert_host_scraper.prober_error import ProbeStatus, probe_status

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
    probe_error: ProbeStatus | None = None


@dataclass
class Result:
    scraped: list[UrlResult]

    def filter_by_status(self, value: int | ProbeStatus) -> list[UrlResult]:
        if isinstance(value, ProbeStatus):
            return [result for result in self.scraped if result.probe_error == value]
        return [result for result in self.scraped if result.status_code == value]


def fetch_site_information(url: str, timeout: int) -> tuple[int, ProbeStatus | None]:
    """Fetch the HTTP status code, or classify the transport failure."""
    try:
        return requests.head(url, timeout=timeout).status_code, None
    except requests.RequestException as e:
        logger.debug(e)
        return -1, probe_status(e)


async def async_fetch_site_information(
    url: str, timeout: int
) -> tuple[int, ProbeStatus | None]:
    return await asyncio.to_thread(fetch_site_information, url, timeout)


async def validate_url(url: str, options: Options) -> UrlResult:
    status_code, probe_error = await async_fetch_site_information(url, options.timeout)
    return UrlResult(url, status_code, probe_error)


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
) -> list[UrlResult]:
    """
    Process a list of URLs concurrently and return the results.
    """
    return asyncio.run(
        _process_urls(urls, options, batch_size, on_progress=on_progress)
    )
