from unittest import TestCase

from cert_host_scraper.utils import strip_url


class TestStripUrl(TestCase):
    def test_strip_protocol_and_www(self):
        self.assertEqual("example.com", strip_url("https://www.example.com"))

    def test_strip_protocol(self):
        self.assertEqual("example.com", strip_url("https://example.com"))

    def test_strip_www(self):
        self.assertEqual("example.com", strip_url("www.example.com"))
