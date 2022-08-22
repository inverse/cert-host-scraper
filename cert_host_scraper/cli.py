import logging
import sys
from pathlib import Path

import click
from requests import RequestException
from rich.console import Console
from rich.progress import track
from rich.table import Table
from single_source import get_version

__version__ = get_version(
    "auto-pr",
    Path(__file__).parent.parent,
)

from cert_host_scraper import Options, Result, fetch_urls, validate_url


def validate_status_code(
    _ctx: click.core.Context, _param: click.core.Option, value: str
):
    try:
        int(value)
    except ValueError:
        raise click.BadParameter("must be an integer")


@click.group()
@click.option("--debug", is_flag=True, help="Whether to enable debug level output")
@click.version_option(__version__, message="%(prog)s: %(version)s")
def cli(debug: bool):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)


@cli.command()
@click.argument("search")
@click.option(
    "--status-code",
    help="Pass the HTTP status code to filter results on",
    callback=validate_status_code,
)
@click.option("--timeout", help="Seconds before timing out on each request", default=2)
@click.option(
    "--clean/--no-clean", is_flag=True, help="Clean wildcard results", default=True
)
def search(search: str, status_code: int, timeout: int, clean: bool):
    """
    Search the certificate transparency log.
    """
    click.echo(f"Searching for {search}")
    options = Options(timeout, clean)
    results = []
    try:
        urls = fetch_urls(search, options)
        click.echo(f"Found {len(urls)} URLs for {search}")
        for url in track(urls, "Checking URLs"):
            results.append(validate_url(url, options))
    except RequestException as e:
        click.echo(f"Failed to search for results: {e}")
        sys.exit(1)

    result = Result(results)
    if status_code:
        display = result.filter_by_status_code(int(status_code))
    else:
        display = result.scraped

    table = Table(show_header=True, header_style="bold")
    table.add_column("URL")
    table.add_column("Status Code")
    for url_result in display:
        table.add_row(url_result.url, str(url_result.status_code))

    console = Console()
    console.print(table)


if __name__ == "__main__":
    cli()
