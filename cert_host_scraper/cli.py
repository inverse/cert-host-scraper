import json
import logging
import sys

import click
from requests import RequestException
from rich import box
from rich.console import Console
from rich.progress import track
from rich.table import Table

from cert_host_scraper import __version__
from cert_host_scraper.scraper import (
    Options,
    Result,
    UrlResult,
    fetch_urls,
    process_urls,
)
from cert_host_scraper.utils import strip_url

NO_STATUS_CODE_FILTER = 0
NO_STATUS_CODE_TIMEOUT = -1


def _render_json_output(results: list[UrlResult]) -> str:
    return json.dumps(
        [{"url": r.url, "status_code": r.status_code} for r in results],
        indent=2,
    )


def _render_table_output(results: list[UrlResult], console: Console) -> None:
    table = Table(show_header=True, header_style="bold", box=box.MINIMAL)
    table.add_column("URL")
    table.add_column("Status Code")
    for r in results:
        code = str(r.status_code) if r.status_code != NO_STATUS_CODE_TIMEOUT else "-"
        url, code_display = r.url, code
        if r.status_code == 200:
            code_display = f"[green]{code}[/green]"
            url = f"[green]{url}[/green]"
        table.add_row(url, code_display)
    console.print(table)


def validate_status_code(
    _ctx: click.core.Context, _param: click.core.Option, value: str
):
    try:
        status_code = int(value)
        if not (100 <= status_code <= 599):
            raise click.BadParameter("status code must be between 100 and 599")

        return status_code
    except ValueError as e:
        raise click.BadParameter("must be an integer") from e
    except TypeError:
        return NO_STATUS_CODE_FILTER


class Output:
    TABLE = "table"
    JSON = "json"

    @classmethod
    def values(cls) -> list:
        return [cls.TABLE, cls.JSON]


RENDERERS = {
    Output.TABLE: lambda results: _render_table_output(results, Console()),
    Output.JSON: lambda results: click.echo(_render_json_output(results)),
}


@click.group()
@click.option("--debug", is_flag=True, help="Whether to enable debug level output")
@click.version_option(__version__, message="%(version)s")
def cli(debug: bool):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.getLogger().setLevel(log_level)


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

    render = RENDERERS[output]
    show_progress = output == Output.TABLE

    if show_progress:
        click.echo(f"Searching for {search}")
    options = Options(timeout, clean)

    try:
        urls = fetch_urls(search, options)
    except RequestException as e:
        click.echo(f"Failed to search for results: {e}")
        sys.exit(1)

    if show_progress:
        click.echo(f"Found {len(urls)} URLs for {search}")

    progress_iter = (
        iter(track(range(len(urls)), "Checking URLs")) if show_progress else None
    )
    scraped_results = process_urls(
        urls,
        options,
        batch_size,
        on_progress=lambda: (
            None if progress_iter is None else next(progress_iter) and None
        ),
    )

    result = Result(scraped_results)
    if status_code != NO_STATUS_CODE_FILTER:
        display = result.filter_by_status_code(status_code)
    else:
        display = result.scraped

    render(display)


if __name__ == "__main__":  # pragma: no cover
    cli()
