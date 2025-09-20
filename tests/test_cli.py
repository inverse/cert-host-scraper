import json
from unittest import TestCase
from unittest.mock import AsyncMock, Mock, patch

import pytest
from click.testing import CliRunner
from requests import RequestException

from cert_host_scraper import __version__
from cert_host_scraper.cli import cli, process_urls, search
from cert_host_scraper.scraper import Options, UrlResult


class TestVersion(TestCase):
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, f"{__version__}\n")


class TestSearch(TestCase):
    def test_search_no_args(self):
        runner = CliRunner()
        result = runner.invoke(search)
        self.assertEqual(result.exit_code, 2)

    @patch("cert_host_scraper.cli.fetch_urls")
    def test_search_network_error(self, mock_fetch_urls: Mock):
        mock_fetch_urls.side_effect = RequestException()
        runner = CliRunner()
        result = runner.invoke(search, ["example.com"])
        self.assertEqual(result.exit_code, 1)

    def test_search_status_code_wrong(self):
        runner = CliRunner()
        result = runner.invoke(search, ["example.com", "--status-code", "xyz"])
        self.assertEqual(result.exit_code, 2)

    def test_search_lower_invalid_status_code(self):
        runner = CliRunner()
        result = runner.invoke(search, ["example.com", "--status-code", "99"])
        self.assertEqual(result.exit_code, 2)

    def test_search_upper_invalid_status_code(self):
        runner = CliRunner()
        result = runner.invoke(search, ["example.com", "--status-code", "600"])
        self.assertEqual(result.exit_code, 2)

    def test_invalid_output(self):
        runner = CliRunner()
        result = runner.invoke(search, ["example.com", "--output", "csv"])
        self.assertEqual(result.exit_code, 2)


class TestSearchSuccess(TestCase):
    @patch("cert_host_scraper.cli.process_urls")
    @patch("cert_host_scraper.cli.fetch_urls")
    def test_search_table_output(self, mock_fetch_urls: Mock, mock_process_urls: Mock):
        runner = CliRunner()
        urls = [
            "https://example-200.com",
            "https://example-404.com",
            "https://example-error.com",
        ]
        mock_fetch_urls.return_value = urls

        mock_process_urls.return_value = [
            UrlResult("https://example-200.com", 200),
            UrlResult("https://example-404.com", 404),
            UrlResult("https://example-error.com", -1),
        ]

        result = runner.invoke(search, ["example.com", "--output", "table"])

        self.assertEqual(result.exit_code, 0)

        output = result.output
        self.assertIn("Searching for example.com", output)
        self.assertIn(f"Found {len(urls)} URLs for example.com", output)
        self.assertIn("URL", output)
        self.assertIn("Status Code", output)
        self.assertIn("https://example-200.com", output)
        self.assertIn("200", output)
        self.assertIn("https://example-404.com", output)
        self.assertIn("404", output)
        self.assertIn("https://example-error.com", output)
        self.assertIn("-", output)

    @patch("cert_host_scraper.cli.process_urls")
    @patch("cert_host_scraper.cli.fetch_urls")
    def test_search_json_output(self, mock_fetch_urls: Mock, mock_process_urls: Mock):
        runner = CliRunner()
        urls = ["https://example-200.com", "https://example-404.com"]
        mock_fetch_urls.return_value = urls

        mock_process_urls.return_value = [
            UrlResult("https://example-200.com", 200),
            UrlResult("https://example-404.com", 404),
        ]

        result = runner.invoke(search, ["example.com", "--output", "json"])

        self.assertEqual(result.exit_code, 0)
        expected_json = [
            {"url": "https://example-200.com", "status_code": 200},
            {"url": "https://example-404.com", "status_code": 404},
        ]
        output_json = json.loads(result.output)
        self.assertCountEqual(output_json, expected_json)

    @patch("cert_host_scraper.cli.process_urls")
    @patch("cert_host_scraper.cli.fetch_urls")
    def test_search_status_code_200(
        self, mock_fetch_urls: Mock, mock_process_urls: Mock
    ):
        runner = CliRunner()
        urls = [
            "https://example-200.com",
            "https://example-404.com",
            "https://example-error.com",
        ]
        mock_fetch_urls.return_value = urls

        mock_process_urls.return_value = [
            UrlResult("https://example-200.com", 200),
            UrlResult("https://example-404.com", 404),
            UrlResult("https://example-error.com", -1),
        ]

        result = runner.invoke(
            search, ["example.com", "--status-code", "200", "--output", "json"]
        )

        self.assertEqual(result.exit_code, 0)
        expected_json = [
            {"url": "https://example-200.com", "status_code": 200},
        ]
        output_json = json.loads(result.output)
        self.assertCountEqual(output_json, expected_json)

    @pytest.mark.asyncio
    @patch("cert_host_scraper.cli.validate_url", new_callable=AsyncMock)
    def test_process_urls(self, mock_validate_url: AsyncMock):
        urls = ["http://example.com", "http://test.com"]
        options = Options(timeout=2, clean=True)
        batch_size = 1
        show_progress = False

        mock_validate_url.side_effect = [
            UrlResult(url="http://example.com", status_code=200),
            UrlResult(url="http://test.com", status_code=404),
        ]

        results = process_urls(urls, options, batch_size, show_progress)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].url, "http://example.com")
        self.assertEqual(results[0].status_code, 200)
        self.assertEqual(results[1].url, "http://test.com")
        self.assertEqual(results[1].status_code, 404)
