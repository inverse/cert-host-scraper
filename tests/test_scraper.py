from unittest import TestCase

import pytest
import vcr

from cert_host_scraper.scraper import Options, fetch_site_information, fetch_urls

TIMEOUT = 2


class TestScraper(TestCase):
    @pytest.mark.enable_socket
    @vcr.use_cassette("fixtures/vcr/google.com.yaml")
    def test_fetch_urls_clean_true(self):
        results = fetch_urls("google.com", Options(timeout=2, clean=True))
        self.assertEqual(53, len(results))
        self.assertIn("https://www.google.com", results)

    @pytest.mark.enable_socket
    @vcr.use_cassette("fixtures/vcr/google.com.yaml")
    def test_fetch_urls_clean_false(self):
        results = fetch_urls("google.com", Options(timeout=2, clean=False))
        self.assertEqual(60, len(results))
        self.assertIn("https://*.mail.google.com", results)

    @pytest.mark.enable_socket
    @vcr.use_cassette("fixtures/vcr/fetch_site_information_valid.yaml")
    def test_fetch_site_information_valid(self):
        result = fetch_site_information("https://example.org", TIMEOUT)
        self.assertEqual(200, result)
