import asyncio
import json
import logging
import sys

import click
from requests import RequestException
from rich import box
from rich.console import Console
from rich.progress import track
from rich.table import Table

from typing import List

from cert_host_scraper import __version__
from cert_host_scraper.scraper import (
    Options,
    Result,
    UrlResult,
    fetch_urls,
    validate_url,
)
from cert_host_scraper.utils import divide_chunks, strip_url

NO_STATUS_CODE_FILTER = 0


def process_urls(
    urls: List[str], options: Options, batch_size: int, show_progress: bool
) -> List[UrlResult]:
    """
    Process a list of URLs concurrently and return the results.
    """
    results = []
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    chunks = list(divide_chunks(urls, batch_size))

    progress_iterable = range(len(chunks))
    if show_progress:
        progress_iterable = track(progress_iterable, "Checking URLs")

    for chunk_index in progress_iterable:
        chunk = chunks[chunk_index]
        chunk_result = loop.run_until_complete(
            asyncio.gather(*[validate_url(url, options) for url in chunk])
        )
        results.extend(chunk_result)

    return results


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


class Output:
    TABLE = "table"
    JSON = "json"

    @classmethod
    def values(cls) -> list:
        return [cls.TABLE, cls.JSON]


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
@click.option(
    "--batch-size",
    help="Number of URLs to process at once",
    default=20,
)
@click.option(
    "--output", type=click.Choice(Output.values()), required=True, default="table"
)
def search(
    search: str,
    status_code: int,
    timeout: int,
    clean: bool,
    strip: bool,
    batch_size: int,
    output: str,
):
    """
    Search the certificate transparency log.
    """
    if strip:
        search = strip_url(search)

    display_json = output == Output.JSON

    if not display_json:
        click.echo(f"Searching for {search}")
    options = Options(timeout, clean)

    try:
        urls = fetch_urls(search, options)
    except RequestException as e:
        click.echo(f"Failed to search for results: {e}")
        sys.exit(1)

    if not display_json:
        click.echo(f"Found {len(urls)} URLs for {search}")

    scraped_results = process_urls(
        urls, options, batch_size, show_progress=not display_json
    )

    result = Result(scraped_results)
    if status_code != NO_STATUS_CODE_FILTER:
        display = result.filter_by_status_code(status_code)
    else:
        display = result.scraped

    if display_json:
        json_output = [
            {"url": url_result.url, "status_code": url_result.status_code}
            for url_result in display
        ]
        click.echo(json.dumps(json_output, indent=2))
    else:
        table = Table(show_header=True, header_style="bold", box=box.MINIMAL)
        table.add_column("URL")
        table.add_column("Status Code")
        for url_result in display:
            display_code = str(url_result.status_code)
            if url_result.status_code == -1:
                display_code = "-"

            url = url_result.url
            if url_result.status_code == 200:
                display_code = f"[green]{display_code}[/green]"
                url = f"[green]{url}[/green]"

            table.add_row(url, display_code)

        console = Console()
        console.print(table)


if __name__ == "__main__":
    cli()
