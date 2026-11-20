import logging
from abc import ABC, abstractmethod

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
from cert_host_scraper.scraper import Options

logger = logging.getLogger(__name__)


def _default_headers() -> dict:
    return {
        "User-Agent": f"Mozilla/5.0 Cert-Host-Scraper/{__version__} (https://github.com/inverse/cert-host-scraper)"
    }


class Provider(ABC):
    """A certificate transparency log source."""

    @abstractmethod
    def fetch_site(self, search: str) -> list[dict]:
        """Return the raw records for a search term."""
        ...

    @abstractmethod
    def scrape_urls(self, results: list[dict], options: Options) -> list[str]:
        """Extract URLs from raw records."""
        ...

    def fetch_urls(self, site: str, options: Options) -> list[str]:
        results = self.fetch_site(site)
        logger.debug(f"Found {len(results)} results for {site}")
        urls = self.scrape_urls(results, options)
        logger.debug(f"Found {len(urls)} URLs for {site}")

        return urls


class CrtSh(Provider):
    """crt.sh provider."""

    # Conservative and tunable: covers p95 crt.sh latency without hanging forever.
    TIMEOUT = 30

    MAX_ATTEMPTS = 5

    @retry(
        retry=retry_if_exception_type(
            (requests.RequestException, urllib3.exceptions.HTTPError)
        ),
        stop=stop_after_attempt(MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
        before=before_log(logger, logging.DEBUG),
    )
    def fetch_site(self, search: str) -> list[dict]:
        url = f"https://crt.sh/?q={search}&output=json"
        result = requests.get(url, headers=_default_headers(), timeout=self.TIMEOUT)
        result.raise_for_status()

        return result.json()

    def scrape_urls(self, results: list[dict], options: Options) -> list[str]:
        total_urls = []
        for result in results:
            common_name = result["common_name"]

            if options.clean and "*" in common_name:
                continue

            total_urls.append(f"https://{common_name}")

        return list(set(total_urls))


class CertKit(Provider):
    """certkit.io provider."""

    TIMEOUT = 30

    MAX_ATTEMPTS = 5

    @retry(
        retry=retry_if_exception_type(
            (requests.RequestException, urllib3.exceptions.HTTPError)
        ),
        stop=stop_after_attempt(MAX_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
        before=before_log(logger, logging.DEBUG),
    )
    def fetch_site(self, search: str) -> list[dict]:
        result = requests.post(
            "https://ct.certkit.io/search",
            headers={
                **_default_headers(),
                "Content-Type": "application/json",
                "Origin": "https://www.certkit.io",
                "Referer": "https://www.certkit.io/",
            },
            json={"domain": search, "sort": ""},
            timeout=self.TIMEOUT,
        )
        result.raise_for_status()

        return result.json()["results"]

    def scrape_urls(self, results: list[dict], options: Options) -> list[str]:
        total_urls = []
        for result in results:
            for name in result["dnsNames"]:
                if options.clean and "*" in name:
                    continue

                total_urls.append(f"https://{name}")

        return list(set(total_urls))
