import logging

import click
from beautifultable import BeautifulTable

from cert_host_scraper import Options, fetch_results_for_search


@click.group()
@click.option("--debug", is_flag=True, help="Whether to enable debug level output")
def cli(debug: bool):
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level)


@cli.command()
@click.argument("search")
@click.option("--status-code", help="Pass the HTTP status code to filter results on")
@click.option(
    "--timeout", help="Amount in seconds before timing out on each request", default=2
)
def search(search: str, status_code: int, timeout: int):
    """
    Search the certificate transparency log.
    """
    result = fetch_results_for_search(search, Options(timeout))
    table = BeautifulTable()
    click.echo(f"Found {len(result.scraped)} URLs for {result.search}")
    if status_code:
        display = result.filter_by_status_code(int(status_code))
    else:
        display = result.scraped

    for url_result in display:
        table.rows.append([url_result.url, url_result.status_code])

    table.columns.header = ["URL", "Status Code"]
    table.columns.alignment["URL"] = BeautifulTable.ALIGN_LEFT
    click.echo(table)


if __name__ == "__main__":
    cli()
