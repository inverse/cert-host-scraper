import json
from unittest import TestCase
from unittest.mock import Mock, patch

from click.testing import CliRunner
from requests import RequestException

from cert_host_scraper import __version__
from cert_host_scraper.cli import cli, search
from cert_host_scraper.prober_error import ProbeStatus
from cert_host_scraper.scraper import UrlResult


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

    def test_search_result_wrong(self):
        runner = CliRunner()
        result = runner.invoke(search, ["example.com", "--result", "xyz"])
        self.assertEqual(result.exit_code, 2)

    def test_search_lower_invalid_result(self):
        runner = CliRunner()
        result = runner.invoke(search, ["example.com", "--result", "99"])
        self.assertEqual(result.exit_code, 2)

    def test_search_upper_invalid_result(self):
        runner = CliRunner()
        result = runner.invoke(search, ["example.com", "--result", "600"])
        self.assertEqual(result.exit_code, 2)

    def test_search_result_keyword_unknown(self):
        runner = CliRunner()
        result = runner.invoke(search, ["example.com", "--result", "frobnicate"])
        self.assertEqual(result.exit_code, 2)

    def test_search_result_uppercase_keyword(self):
        """Uppercase 'TIMEOUT' is accepted case-insensitively, so invocation
        proceeds to scraping (fails only because tests block sockets)."""
        runner = CliRunner()
        result = runner.invoke(search, ["example.com", "--result", "TIMEOUT"])
        self.assertEqual(result.exit_code, 1)

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
        self.assertIn("Result", output)
        self.assertIn("https://example-200.com", output)
        self.assertIn("200", output)
        self.assertIn("https://example-404.com", output)
        self.assertIn("404", output)

    @patch("cert_host_scraper.cli.process_urls")
    @patch("cert_host_scraper.cli.fetch_urls")
    def test_search_table_output_probe_error(
        self, mock_fetch_urls: Mock, mock_process_urls: Mock
    ):
        runner = CliRunner()
        mock_fetch_urls.return_value = ["https://example-error.com"]
        mock_process_urls.return_value = [
            UrlResult("https://example-error.com", -1, ProbeStatus.DNS_ERROR),
        ]

        result = runner.invoke(search, ["example.com", "--output", "table"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("https://example-error.com", result.output)
        self.assertIn(ProbeStatus.DNS_ERROR.value, result.output)

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
            {
                "url": "https://example-200.com",
                "status_code": 200,
                "probe_error": None,
            },
            {
                "url": "https://example-404.com",
                "status_code": 404,
                "probe_error": None,
            },
        ]
        output_json = json.loads(result.output)
        self.assertCountEqual(output_json, expected_json)

    @patch("cert_host_scraper.cli.process_urls")
    @patch("cert_host_scraper.cli.fetch_urls")
    def test_search_result_200(self, mock_fetch_urls: Mock, mock_process_urls: Mock):
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
            search, ["example.com", "--result", "200", "--output", "json"]
        )

        self.assertEqual(result.exit_code, 0)
        expected_json = [
            {
                "url": "https://example-200.com",
                "status_code": 200,
                "probe_error": None,
            },
        ]
        output_json = json.loads(result.output)
        self.assertCountEqual(output_json, expected_json)

    @patch("cert_host_scraper.cli.process_urls")
    @patch("cert_host_scraper.cli.fetch_urls")
    def test_search_result_keyword_timeout(
        self, mock_fetch_urls: Mock, mock_process_urls: Mock
    ):
        runner = CliRunner()
        mock_fetch_urls.return_value = [
            "https://example-200.com",
            "https://example-error.com",
        ]
        mock_process_urls.return_value = [
            UrlResult("https://example-200.com", 200),
            UrlResult("https://example-error.com", -1, ProbeStatus.TIMEOUT),
        ]

        result = runner.invoke(
            search, ["example.com", "--result", "timeout", "--output", "json"]
        )

        self.assertEqual(result.exit_code, 0)
        output_json = json.loads(result.output)
        self.assertEqual(len(output_json), 1)
        self.assertEqual(output_json[0]["url"], "https://example-error.com")
        self.assertEqual(output_json[0]["probe_error"], "timeout")


class TestCliGroup(TestCase):
    """Cover the cli() group callback path via --debug."""

    @patch("cert_host_scraper.cli.fetch_urls")
    def test_cli_with_debug(self, mock_fetch_urls: Mock):
        mock_fetch_urls.return_value = []
        runner = CliRunner()
        result = runner.invoke(cli, ["--debug", "search", "example.com"])
        self.assertEqual(result.exit_code, 0)
