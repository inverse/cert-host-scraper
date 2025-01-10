from unittest import TestCase
from unittest.mock import Mock, patch

from click.testing import CliRunner
from requests import RequestException

from cert_host_scraper import __version__
from cert_host_scraper.cli import cli


class TestVersion(TestCase):
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--version"])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, f"{__version__}\n")


class TestSearch(TestCase):
    def test_search_no_args(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["search"])
        self.assertEqual(result.exit_code, 2)

    @patch("cert_host_scraper.cli.fetch_urls")
    def test_search_network_error(self, mock_fetch_urls: Mock):
        mock_fetch_urls.side_effect = RequestException()
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "example.com"])
        self.assertEqual(result.exit_code, 1)

    def test_search_status_code_wrong(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "example.com", "--status-code", "xyz"])
        self.assertEqual(result.exit_code, 2)

    def test_search_lower_invalid_status_code(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "example.com", "--status-code", "99"])
        self.assertEqual(result.exit_code, 2)

    def test_search_upper_invalid_status_code(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "example.com", "--status-code", "600"])
        self.assertEqual(result.exit_code, 2)

    def test_invalid_output(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["search", "example.com", "--output", "csv"])
        self.assertEqual(result.exit_code, 2)
