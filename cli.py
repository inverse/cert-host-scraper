import click
from cert_host_scraper import fetch_results_for_search


@click.command()
@click.argument("search")
def search(search: str):
    result = fetch_results_for_search(search)

    print(f"Found {len(result.valid_urls)}/{len(result.total_urls)} URLs for {result.search}")
    for valid_url in result.valid_urls:
        print(f"- {valid_url}")


if __name__ == '__main__':
    search()
