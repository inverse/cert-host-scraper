# Cert Host Scraper

[![PyPI version](https://badge.fury.io/py/cert-host-scraper.svg)](https://badge.fury.io/py/cert-host-scraper)
[![Python](https://img.shields.io/pypi/pyversions/cert-host-scraper)](https://pypi.org/project/cert-host-scraper/)
![PyPI downloads](https://img.shields.io/pypi/dm/cert-host-scraper?label=pypi%20downloads)
[![License](https://img.shields.io/github/license/inverse/cert-host-scraper.svg)](LICENSE)

[![CI](https://github.com/inverse/cert-host-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/inverse/cert-host-scraper/actions/workflows/ci.yml)
[![codecov](https://codecov.io/github/inverse/cert-host-scraper/graph/badge.svg?token=TLO58M5UC5)](https://codecov.io/github/inverse/cert-host-scraper)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![Static Badge](https://img.shields.io/badge/type%20checked-mypy-039dfc)

Search certificate transparency logs - via [crt.sh](https://crt.sh) or [certkit.io](https://www.certkit.io) - for hostnames matching a keyword. Each result is probed and shown with its HTTP status code or failure class, and results can be filtered by status code or error type, with output as a table or JSON.

<img alt="Demo of cert-host-scraper" src="https://vhs.charm.sh/vhs-2UjiUosXl5Zov5TfIbViGF.gif" width="800" />

## Installation

With [pipx]:

```bash
pipx install cert-host-scraper
```

With pip:

```bash
pip install cert-host-scraper
```

## Usage

Once installed you can look up information about a domain using the `search` command:

```bash
cert-host-scraper search your-domain.com
```

There are additional options that can be provided to change this behaviour and result filtering.

Pass `--help` to this command for a full list of options.

## Development

Requires [uv][0] and Python 3.10+.

```bash
uv sync
uv run python -m cert_host_scraper.cli
```

### Testing

Run the test suite:

```bash
mise run test
```

Run with a new fixture, first remove the old; than run with record mode:

```bash
rm fixtures/vcr/fetch_site_information_valid.yaml
mise run test:record
```

## License

MIT

[0]: https://github.com/astral-sh/uv
[1]: https://github.com/jdx/mise
[2]: https://pipx.pypa.io
[vcrpy]: https://vcrpy.readthedocs.io
