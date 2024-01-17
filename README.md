# Cert Host Scraper

![CI](https://github.com/inverse/cert-host-scraper/workflows/CI/badge.svg)
[![PyPI version](https://badge.fury.io/py/cert-host-scraper.svg)](https://badge.fury.io/py/cert-host-scraper)
![PyPI downloads](https://img.shields.io/pypi/dm/cert-host-scraper?label=pypi%20downloads)
[![License](https://img.shields.io/github/license/inverse/cert-host-scraper.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Query the certificate transparency log from [crt.sh](https://crt.sh) by a given a keyword and returns the status code of the matched results. Optionally, filtering the results by status code.

<img alt="Demo of cert-host-scraper" src="https://vhs.charm.sh/vhs-3n8rmkDw9BDCmq55P8YKAy.gif" width="800" />
        

## Usage

```bash
cert-host-scraper search your-domain.com [--status-code 200]
```

## Installation

With pipx:

```bash
pipx install cert-host-scraper
```

With pip:

```bash
pip install cert-host-scraper
```

## Development

Requires [poetry][0] and Python 3.10+.

```
poetry install
poetry run python -m cert_host_scraper.cli
```

## License

MIT

[0]: https://python-poetry.org
