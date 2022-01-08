import click
from cert_host_scraper import fetch_results_for_search


@click.command()
@click.argument("search")
def search(search: str):
    result = fetch_results_for_search(search)

    print(f"Found {len(result.scraped)} URLs for {result.search}")
    for url_result in result.scraped:
        print(f"- {url_result.url} - ({url_result.status_code})")


if __name__ == '__main__':
    search()
