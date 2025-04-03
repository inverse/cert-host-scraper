# Cert Host Scraper

[![CI](https://github.com/inverse/cert-host-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/inverse/cert-host-scraper/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/cert-host-scraper.svg)](https://badge.fury.io/py/cert-host-scraper)
![PyPI downloads](https://img.shields.io/pypi/dm/cert-host-scraper?label=pypi%20downloads)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Static Badge](https://img.shields.io/badge/type%20checked-mypy-039dfc)
[![License](https://img.shields.io/github/license/inverse/cert-host-scraper.svg)](LICENSE)

Query the certificate transparency log from [crt.sh](https://crt.sh) by a given a keyword and returns the status code of the matched results. Optionally, filtering the results by status code.

<img alt="Demo of cert-host-scraper" src="https://vhs.charm.sh/vhs-7fKWanXXcalG2oS28DVyZC.gif" width="800" />

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

```bash
poetry install
poetry run python -m cert_host_scraper.cli
```

Python and poetry versions are managed [mise][1] as defined in the provided `.tool-versions` file.

## License

MIT

[0]: https://python-poetry.org
[1]: https://github.com/jdx/mise
