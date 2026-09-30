from __future__ import annotations

import json
import logging
import sys
from importlib.metadata import version

__version__ = version("cert-host-scraper")

import click
from requests import RequestException
from rich import box
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from cert_host_scraper.prober_error import ProbeStatus
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
NO_STATUS_CODE_DISPLAY = "-"

PROBE_REASONS = {
    ProbeStatus.DNS_ERROR: "DNS lookup failed",
    ProbeStatus.TLS_ERROR: "TLS handshake failed",
    ProbeStatus.CONNECTION_REFUSED: "connection refused",
    ProbeStatus.TIMEOUT: "timed out",
    ProbeStatus.OTHER: "request failed",
}


def _render_json_output(results: list[UrlResult]) -> str:
    return json.dumps(
        [
            {
                "url": r.url,
                "status_code": r.status_code,
                "probe_error": r.probe_error.value if r.probe_error else None,
            }
            for r in results
        ],
        indent=2,
    )


def _result_rank(r: UrlResult) -> tuple[int, str]:
    if r.probe_error is not None:
        group = 0
    elif 200 <= r.status_code < 300:
        group = 1
    elif 300 <= r.status_code < 400:
        group = 2
    else:
        group = 3
    return (group, r.url)


def _status_cell(r: UrlResult) -> str:
    if r.probe_error is not None or r.status_code == NO_STATUS_CODE_TIMEOUT:
        return f"[red]{NO_STATUS_CODE_DISPLAY}[/red]"
    if 200 <= r.status_code < 400:
        return f"[green]{r.status_code}[/green]"
    return f"[red]{r.status_code}[/red]"


def _reason_cell(r: UrlResult) -> str:
    if r.probe_error is None:
        return ""
    return f"[red]{PROBE_REASONS[r.probe_error]}[/red]"


def _summary(results: list[UrlResult]) -> str:
    failed = sum(1 for r in results if r.probe_error is not None)
    ok = sum(1 for r in results if r.probe_error is None and 200 <= r.status_code < 300)
    redirected = sum(
        1 for r in results if r.probe_error is None and 300 <= r.status_code < 400
    )
    errored = len(results) - failed - ok - redirected

    parts = [f"{len(results)} checked", f"[green]{ok} ok[/green]"]
    if redirected:
        parts.append(f"{redirected} redirect")
    if errored:
        parts.append(f"[red]{errored} error[/red]")
    if failed:
        parts.append(f"[red]{failed} failed[/red]")
    return "  ".join(parts)


def _render_table_output(results: list[UrlResult], console: Console) -> None:
    table = Table(box=box.ROUNDED, header_style="bold")
    table.add_column("URL", overflow="ellipsis")
    table.add_column("Status", justify="right")
    table.add_column("Reason")
    for r in sorted(results, key=_result_rank):
        table.add_row(r.url, _status_cell(r), _reason_cell(r))
    console.print(table)
    if results:
        console.print(_summary(results), highlight=False)


def validate_result(_ctx: click.core.Context, _param: click.core.Option, value: str):
    if value is None:
        return NO_STATUS_CODE_FILTER

    status = value.strip().lower()
    try:
        return ProbeStatus(status)
    except ValueError:
        pass

    try:
        status_code = int(status)
    except ValueError as e:
        raise click.BadParameter(
            "must be an HTTP status code or one of: "
            + ", ".join(p.value for p in ProbeStatus)
        ) from e

    if not (100 <= status_code <= 599):
        raise click.BadParameter("status code must be between 100 and 599")

    return status_code


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


def _fetch_urls_with_spinner(search: str, options: Options) -> list[str]:
    with Progress(
        SpinnerColumn(), TextColumn("{task.description}"), transient=True
    ) as progress:
        progress.add_task(f"Searching for {search}", total=None)
        return fetch_urls(search, options)


@click.group()
@click.option("--debug", is_flag=True, help="Whether to enable debug level output")
@click.version_option(__version__, message="%(version)s")
def cli(debug: bool):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.getLogger().setLevel(log_level)


@cli.command()
@click.argument("search")
@click.option(
    "--result",
    help="HTTP status code or failure class (dns, tls, refused, timeout, other) to filter on",
    callback=validate_result,
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
    "--output", type=click.Choice(Output.values()), required=False, default="table"
)
def search(
    search: str,
    result: int | ProbeStatus,
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

    options = Options(timeout, clean)
    fetch = _fetch_urls_with_spinner if show_progress else fetch_urls

    try:
        urls = fetch(search, options)
    except RequestException as e:
        click.echo(f"Failed to search for results: {e}")
        sys.exit(1)

    if show_progress:
        click.echo(f"Results for {search}")

    if show_progress:
        with Progress(transient=True) as progress:
            task_id = progress.add_task("Checking URLs", total=len(urls))
            scraped_results = process_urls(
                urls,
                options,
                batch_size,
                on_progress=lambda: progress.advance(task_id),
            )
    else:
        scraped_results = process_urls(urls, options, batch_size)

    results = Result(scraped_results)
    if result != NO_STATUS_CODE_FILTER:
        display = results.filter_by_status(result)
    else:
        display = results.scraped

    render(display)


if __name__ == "__main__":  # pragma: no cover
    cli()
