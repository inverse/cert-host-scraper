from unittest import TestCase

import pytest
import vcr

from cert_host_scraper.scraper import Options, fetch_site_information, fetch_urls

TIMEOUT = 2


class TestScraper(TestCase):
    @pytest.mark.enable_socket
    @vcr.use_cassette("fixtures/vcr/example.org.yaml")
    def test_fetch_urls_clean(self):
        results = fetch_urls("example.org", Options(timeout=2, clean=True))
        self.assertEqual(4, len(results))
        self.assertIn("https://www.example.org", results)

    @pytest.mark.enable_socket
    @vcr.use_cassette("fixtures/vcr/fetch_site_information_valid.yaml")
    def test_fetch_site_information_valid(self):
        result = fetch_site_information("https://example.org", TIMEOUT)
        self.assertEqual(200, result)
