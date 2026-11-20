import os
from typing import Any, cast
from unittest import TestCase
from unittest.mock import Mock, patch

import pytest
import requests
import vcr

from cert_host_scraper import providers
from cert_host_scraper.scraper import Options

VCR_RECORD_MODE = os.getenv("VCR_RECORD_MODE", "none")
my_vcr = vcr.VCR(
    record_mode=VCR_RECORD_MODE,
    cassette_library_dir="fixtures/vcr",
)

FETCH_SITE_RETRY = cast(Any, providers.CrtSh.fetch_site).retry


@pytest.mark.enable_socket
class TestFetchUrls(TestCase):
    @my_vcr.use_cassette("google.com.yaml")
    def test_fetch_urls_clean_true(self):
        results = providers.CrtSh().fetch_urls(
            "google.com", Options(timeout=2, clean=True)
        )
        self.assertEqual(53, len(results))
        self.assertIn("https://www.google.com", results)

    @my_vcr.use_cassette("google.com.yaml")
    def test_fetch_urls_clean_false(self):
        results = providers.CrtSh().fetch_urls(
            "google.com", Options(timeout=2, clean=False)
        )
        self.assertEqual(60, len(results))
        self.assertIn("https://*.mail.google.com", results)


class TestFetchSite(TestCase):
    @patch("cert_host_scraper.providers.requests.get")
    def test_fetch_site_timeout(self, mock_get):
        mock_get.return_value.json.return_value = []
        result = providers.CrtSh().fetch_site("example.com")
        self.assertEqual([], result)
        expected_url = "https://crt.sh/?q=example.com&output=json"
        mock_get.assert_called_once_with(
            expected_url,
            headers=providers._default_headers(),
            timeout=providers.CrtSh.TIMEOUT,
        )

    @patch.object(FETCH_SITE_RETRY, "sleep")
    @patch("cert_host_scraper.providers.requests.get")
    def test_fetch_site_retries_bad_gateway_then_succeeds(self, mock_get, _sleep):
        response = Mock()
        response.json.return_value = [{"common_name": "example.com"}]
        response.raise_for_status.side_effect = [
            requests.HTTPError("502 Server Error"),
            requests.HTTPError("503 Service Unavailable"),
            None,
        ]
        mock_get.return_value = response

        result = providers.CrtSh().fetch_site("example.com")

        self.assertEqual([{"common_name": "example.com"}], result)
        self.assertEqual(3, mock_get.call_count)

    @patch.object(FETCH_SITE_RETRY, "sleep")
    @patch("cert_host_scraper.providers.requests.get")
    def test_fetch_site_gives_up_after_max_attempts(self, mock_get, _sleep):
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("502 Bad Gateway")
        mock_get.return_value = response

        with self.assertRaises(requests.HTTPError):
            providers.CrtSh().fetch_site("example.com")

        self.assertEqual(providers.CrtSh.MAX_ATTEMPTS, mock_get.call_count)


@pytest.mark.enable_socket
class TestCertKit(TestCase):
    @my_vcr.use_cassette("certkit_example.org.yaml")
    def test_fetch_urls_clean_true(self):
        results = providers.CertKit().fetch_urls(
            "example.org", Options(timeout=2, clean=True)
        )
        self.assertIn("https://example.org", results)
        self.assertNotIn("https://*.example.org", results)

    @my_vcr.use_cassette("certkit_example.org.yaml")
    def test_fetch_urls_clean_false(self):
        results = providers.CertKit().fetch_urls(
            "example.org", Options(timeout=2, clean=False)
        )
        self.assertIn("https://*.example.org", results)

    @patch("cert_host_scraper.providers.requests.post")
    def test_fetch_site_posts_domain(self, mock_post):
        mock_post.return_value.json.return_value = {"results": []}
        result = providers.CertKit().fetch_site("example.com")
        self.assertEqual([], result)
        mock_post.assert_called_once_with(
            "https://ct.certkit.io/search",
            headers={
                **providers._default_headers(),
                "Content-Type": "application/json",
                "Origin": "https://www.certkit.io",
                "Referer": "https://www.certkit.io/",
            },
            json={"domain": "example.com", "sort": ""},
            timeout=providers.CertKit.TIMEOUT,
        )
