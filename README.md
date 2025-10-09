# Cert Host Scraper

[![CI](https://github.com/inverse/cert-host-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/inverse/cert-host-scraper/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/cert-host-scraper.svg)](https://badge.fury.io/py/cert-host-scraper)
![PyPI downloads](https://img.shields.io/pypi/dm/cert-host-scraper?label=pypi%20downloads)
[![codecov](https://codecov.io/github/inverse/cert-host-scraper/graph/badge.svg?token=TLO58M5UC5)](https://codecov.io/github/inverse/cert-host-scraper)
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

Requires [uv][0] and Python 3.10+.

```bash
uv install
uv run python -m cert_host_scraper.cli
```

All dev tooling is managed [mise][1] as defined in the provided `mise.toml` and `.python-version` files.

## License

MIT

[0]: https://github.com/astral-sh/uv
[1]: https://github.com/jdx/mise
