import click
from beautifultable import BeautifulTable

from cert_host_scraper import fetch_results_for_search


@click.command()
@click.argument("search")
@click.option("--status-code", help="Pass the HTTP status code to filter results on")
def search(search: str, status_code: int):
    """
    Search the certificate transparency log.
    """
    result = fetch_results_for_search(search)
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
    search()
