from unittest import TestCase
import vcr
import pytest

from cert_host_scraper.scraper import fetch_urls, Options


class TestScraper(TestCase):

    @pytest.mark.enable_socket
    @vcr.use_cassette("fixtures/vcr/example.org.yaml")
    def test_fetch_urls_clean(self):
        results = fetch_urls("example.org", Options(timeout=2, clean=True))
        self.assertIn('https://www.example.org', results)
