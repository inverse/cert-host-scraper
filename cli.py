import click
from beautifultable import BeautifulTable

from cert_host_scraper import fetch_results_for_search


@click.command()
@click.argument("search")
def search(search: str):
    result = fetch_results_for_search(search)
    table = BeautifulTable()
    print(f"Found {len(result.scraped)} URLs for {result.search}")
    for url_result in result.scraped:
        table.rows.append([url_result.url, url_result.status_code])

    table.columns.header = ["URL", "Status Code"]
    table.columns.alignment["URL"] = BeautifulTable.ALIGN_LEFT
    print(table)


if __name__ == "__main__":
    search()
