from unittest import TestCase

import pytest
import vcr

from cert_host_scraper import scraper

TIMEOUT = 2


@pytest.mark.enable_socket
class TestScraper(TestCase):
    def test_fetch_urls_clean_true(self):
        with vcr.use_cassette("fixtures/vcr/google.com.yaml"):
            results = scraper.fetch_urls(
                "google.com", scraper.Options(timeout=2, clean=True)
            )
            self.assertEqual(53, len(results))
            self.assertIn("https://www.google.com", results)

    def test_fetch_urls_clean_false(self):
        with vcr.use_cassette("fixtures/vcr/google.com.yaml"):
            results = scraper.fetch_urls(
                "google.com", scraper.Options(timeout=2, clean=False)
            )
            self.assertEqual(60, len(results))
            self.assertIn("https://*.mail.google.com", results)

    def test_fetch_site_information_valid(self):
        with vcr.use_cassette("fixtures/vcr/fetch_site_information_valid.yaml"):
            result = scraper.fetch_site_information("https://example.org", TIMEOUT)
            self.assertEqual(200, result)


class TestResults(TestCase):
    def test_filter_by_status_code(self):
        results = scraper.Result(
            [
                scraper.UrlResult("https://example-200.org", 200),
                scraper.UrlResult("https://example-500.org", 500),
            ]
        )

        filtered = results.filter_by_status_code(200)
        self.assertEqual(1, len(filtered))
        self.assertEqual("https://example-200.org", filtered[0].url)
        self.assertEqual(200, filtered[0].status_code)
