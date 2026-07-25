import asyncio
import os
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

import pytest
import requests
import vcr

from cert_host_scraper import scraper

TIMEOUT = 2

VCR_RECORD_MODE = os.getenv("VCR_RECORD_MODE", "none")
my_vcr = vcr.VCR(
    record_mode=VCR_RECORD_MODE,
    cassette_library_dir="fixtures/vcr",
)


@pytest.mark.enable_socket
class TestScraper(TestCase):
    @my_vcr.use_cassette("google.com.yaml")
    def test_fetch_urls_clean_true(self):
        results = scraper.fetch_urls(
            "google.com", scraper.Options(timeout=2, clean=True)
        )
        self.assertEqual(53, len(results))
        self.assertIn("https://www.google.com", results)

    @my_vcr.use_cassette("google.com.yaml")
    def test_fetch_urls_clean_false(self):
        results = scraper.fetch_urls(
            "google.com", scraper.Options(timeout=2, clean=False)
        )
        self.assertEqual(60, len(results))
        self.assertIn("https://*.mail.google.com", results)

    @my_vcr.use_cassette("fetch_site_information_valid.yaml")
    def test_fetch_site_information_valid(self):
        result = scraper.fetch_site_information("https://example.org", TIMEOUT)
        self.assertEqual(200, result)


class TestFetchSiteInformation(TestCase):
    @patch("cert_host_scraper.scraper.requests.get")
    def test_fetch_site_information_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("connection error")
        result = scraper.fetch_site_information("https://example.com", TIMEOUT)
        self.assertEqual(-1, result)


class TestValidateUrl(TestCase):
    @patch("cert_host_scraper.scraper.fetch_site_information")
    def test_validate_url(self, mock_fetch):
        """Exercises validate_url and async_fetch_site_information."""
        mock_fetch.return_value = 200

        async def run():
            return await scraper.validate_url(
                "https://example.com", scraper.Options(timeout=2, clean=True)
            )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run())
            self.assertEqual(result.url, "https://example.com")
            self.assertEqual(result.status_code, 200)
            mock_fetch.assert_called_once_with("https://example.com", 2)
        finally:
            loop.close()

    @patch("cert_host_scraper.scraper.fetch_site_information")
    def test_validate_url_error(self, mock_fetch):
        """Exercises validate_url when fetch_site_information returns an error code."""
        mock_fetch.return_value = -1

        async def run():
            return await scraper.validate_url(
                "https://invalid.example.com", scraper.Options(timeout=2, clean=True)
            )

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run())
            self.assertEqual(result.url, "https://invalid.example.com")
            self.assertEqual(result.status_code, -1)
        finally:
            loop.close()


class TestProcessUrls(TestCase):
    @patch("cert_host_scraper.scraper.validate_url", new_callable=AsyncMock)
    def test_process_urls(self, mock_validate_url):
        urls = ["http://example.com", "http://test.com"]
        options = scraper.Options(timeout=2, clean=True)
        batch_size = 1
        progress = Mock()

        mock_validate_url.side_effect = [
            scraper.UrlResult(url="http://example.com", status_code=200),
            scraper.UrlResult(url="http://test.com", status_code=404),
        ]

        result = scraper.process_urls(urls, options, batch_size, on_progress=progress)
        self.assertIsInstance(result, scraper.Result)
        self.assertEqual(len(result.scraped), 2)
        self.assertEqual(result.scraped[0].url, "http://example.com")
        self.assertEqual(result.scraped[0].status_code, 200)
        self.assertEqual(result.scraped[1].url, "http://test.com")
        self.assertEqual(result.scraped[1].status_code, 404)
        self.assertEqual(progress.call_count, 2)


class TestSearchUrls(TestCase):
    @patch("cert_host_scraper.scraper.process_urls")
    @patch("cert_host_scraper.scraper.fetch_urls")
    def test_search_urls(self, mock_fetch_urls, mock_process_urls):
        mock_fetch_urls.return_value = [
            "https://example.com",
            "https://test.com",
        ]
        mock_process_urls.return_value = scraper.Result(
            [
                scraper.UrlResult("https://example.com", 200),
                scraper.UrlResult("https://test.com", 404),
            ]
        )

        options = scraper.Options(timeout=2, clean=True)
        result = scraper.search_urls("example.com", options)

        self.assertIsInstance(result, scraper.Result)
        self.assertEqual(len(result.scraped), 2)
        mock_fetch_urls.assert_called_once_with("example.com", options)
        mock_process_urls.assert_called_once_with(
            ["https://example.com", "https://test.com"],
            options,
            20,
            on_progress=None,
        )

    @patch("cert_host_scraper.scraper.process_urls")
    @patch("cert_host_scraper.scraper.fetch_urls")
    def test_search_urls_with_progress(self, mock_fetch_urls, mock_process_urls):
        mock_fetch_urls.return_value = ["https://example.com"]
        mock_process_urls.return_value = scraper.Result(
            [
                scraper.UrlResult("https://example.com", 200),
            ]
        )

        options = scraper.Options(timeout=2, clean=True)
        progress = Mock()
        result = scraper.search_urls("example.com", options, on_progress=progress)

        self.assertIsInstance(result, scraper.Result)
        mock_process_urls.assert_called_once_with(
            ["https://example.com"], options, 20, on_progress=progress
        )


class TestResults(TestCase):
    def test_filter_by_status_code(self):
        results = scraper.Result(
            [
                scraper.UrlResult("https://example-200.org", 200),
                scraper.UrlResult("https://example-500.org", 500),
            ]
        )

        filtered = results.filter_by_status_code(200)
        self.assertIsInstance(filtered, scraper.Result)
        self.assertEqual(1, len(filtered.scraped))
        self.assertEqual("https://example-200.org", filtered.scraped[0].url)
        self.assertEqual(200, filtered.scraped[0].status_code)
