import asyncio
import logging
import sys

import click
from requests import RequestException
from rich.console import Console
from rich.progress import track
from rich.table import Table

from cert_host_scraper import __version__
from cert_host_scraper.scraper import Options, Result, fetch_urls, validate_url
from cert_host_scraper.utils import divide_chunks, strip_url

NO_STATUS_CODE_FILTER = 0


def validate_status_code(
    _ctx: click.core.Context, _param: click.core.Option, value: str
):
    try:
        status_code = int(value)
        if not (100 <= status_code <= 599):
            raise click.BadParameter("status code must be between 100 and 599")

        return status_code
    except ValueError:
        raise click.BadParameter("must be an integer")
    except TypeError:
        return NO_STATUS_CODE_FILTER


@click.group()
@click.option("--debug", is_flag=True, help="Whether to enable debug level output")
@click.version_option(__version__, message="%(version)s")
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
@click.option(
    "--strip/--no-strip",
    is_flag=True,
    help="Remove protocol and leading www from search",
    default=True,
)
def search(search: str, status_code: int, timeout: int, clean: bool, strip: bool):
    """
    Search the certificate transparency log.
    """
    if strip:
        search = strip_url(search)

    click.echo(f"Searching for {search}")
    options = Options(timeout, clean)
    results = []
    try:
        urls = fetch_urls(search, options)
    except RequestException as e:
        click.echo(f"Failed to search for results: {e}")
        sys.exit(1)

    click.echo(f"Found {len(urls)} URLs for {search}")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    chunks = list(divide_chunks(urls, 10))
    for chunk_index in track(range(len(chunks)), "Checking URLs"):
        chunk_result = loop.run_until_complete(
            asyncio.gather(*[validate_url(url, options) for url in chunks[chunk_index]])
        )
        results += chunk_result

    result = Result(results)
    if status_code != NO_STATUS_CODE_FILTER:
        display = result.filter_by_status_code(status_code)
    else:
        display = result.scraped

    table = Table(show_header=True, header_style="bold")
    table.add_column("URL")
    table.add_column("Status Code")
    for url_result in display:
        display_code = str(url_result.status_code)
        if url_result.status_code == -1:
            display_code = "-"
        table.add_row(url_result.url, display_code)

    console = Console()
    console.print(table)


if __name__ == "__main__":
    cli()
